from typing import Dict, Any, Tuple, Optional, Type
import random
import torch
from torch import nn, Tensor
from torch.utils.data import DataLoader
import warnings
import difflib

from .base import BaseContinualLearner
from ..models.heads import BaseHead


class ReplayContinualLearner(BaseContinualLearner):
    """
    Continual learner with experience replay.

    On each training step, one batch from the currently active task is combined with one batch
    sampled from a buffer of past tasks. This helps prevent catastrophic forgetting by
    rehearsing older tasks during training of new tasks.

    Parameters
    ----------
    base : nn.Module
        The shared backbone/feature extractor used by all tasks.
    heads : dict of {str: BaseHead}, optional
        Mapping from task name to initialized head modules.
    lambda_replay : float, default=1.0
        Global weight applied to replay losses when combining with the active
        task loss.
    per_task_lambda : dict of {str: float}, optional
        Task-specific replay weights overriding the global ``lambda_replay``.
    per_task_probs : dict of {str: float}, optional
        Sampling probabilities for replay tasks. If ``None``, tasks are sampled
        uniformly.
    batch_size_past : int, optional
        Safeguard to ensure replay batches do not exceed this size.
        Each dataloader provided via `set_replay_loaders` should already have this batch size,
        but if not, the batch will be trimmed.
    **kwargs
        Additional arguments passed to :class:`BaseContinualLearner`.

    Notes
    -----
    - Needs to call set_replay_loaders() before training to provide dataloaders for past tasks.
    - The effective batch size is `batch_size for the active task + batch_size_past`.
    """
    def __init__(
        self,
        base: nn.Module,
        heads: Optional[Dict[str, BaseHead]] = None,
        *,
        lambda_replay: float = 1.0,
        per_task_lambda: Optional[Dict[str, float]] = None,
        per_task_probs: Optional[Dict[str, float]] = None,
        # batch_size_current: Optional[int] = None,
        batch_size_past: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(base=base, heads=heads, **kwargs)
        self.lambda_replay = lambda_replay
        self.per_task_lambda = per_task_lambda or {}
        self.per_task_probs = per_task_probs or {}
        # self.bs_current = batch_size_current
        self.bs_past = batch_size_past
        self._replay_loaders: Dict[str, DataLoader] = {}
        self._replay_iters: Dict[str, Optional[object]] = {}

        if self.lambda_replay <= 0 and not self.per_task_lambda:
            raise ValueError("Must set either lambda_replay or per_task_lambda.")
        if self.lambda_replay > 0.0 and self.per_task_lambda:
            raise ValueError("Cannot set both global lambda_replay and per_task_lambda.")
        if any(p < 0 for p in self.per_task_probs.values()):
            raise ValueError("per_task_probs cannot have negative values.")
        # if self.bs_current <= 0:
        #     raise ValueError("batch_size_current must be greater than 0.")
        if self.bs_past is not None and self.bs_past <= 0:
            raise ValueError("batch_size_past must be greater than 0.")

    # ---------------------------------------------------------------------------------------------
    #  Replay utilities (public API)
    # ---------------------------------------------------------------------------------------------
    def set_replay_loaders(self, replay_loaders: Dict[str, DataLoader]):
        """
        Provide dataloaders for PAST tasks only (exclude current).
        Batch size of each loader should equal bs_past for clean behavior.
        """
        invalid = self.active_task in set(replay_loaders.keys())
        if invalid:
            raise ValueError(f"Replay loaders cannot include current task: {self.active_task}")
        self._replay_loaders = dict(replay_loaders)
        self._replay_iters = {t: None for t in self._replay_loaders}

    # ---------------------------------------------------------------------------------------------
    #  Lightning hooks
    # ---------------------------------------------------------------------------------------------
    def on_train_start(self):
        # Build (or rebuild) endless iterators for replay loaders
        self._ensure_replay_iters()
        if not self._replay_loaders:
            warnings.warn(
                "No replay loaders provided — training will proceed without replay (standard fine-tuning).",
                RuntimeWarning,
            )

    def _combine_losses(self, task2loss: Dict[str, Dict[str, Tensor]]):
        curr_loss, past_loss = 0.0, 0.0
        if self.lambda_replay > 0.0:
            for task, loss_dict in task2loss.items():
                if task == self.active_task:
                    curr_loss += loss_dict['loss']
                else:
                    past_loss += loss_dict['loss']
            return curr_loss + self.lambda_replay * past_loss
        elif self.per_task_lambda:
            total_loss = 0.0
            for task, loss_dict in task2loss.items():
                weight = self.per_task_lambda[task]
                total_loss += weight * loss_dict['loss']
            return total_loss

        raise ValueError("Either lambda_replay or per_task_lambda must be set.")

    def training_step(self, batch: Dict[str, Any], batch_idx: int) -> Tensor:
        """
        `batch` is a dict {task: subbatch}
        Sample ONE past task and add its subbatch to `batch` for replay.
        """
        # Add subbatch from a random past task to batch
        if self._replay_loaders:
            replay_task = self._choose_replay_task()
            replay_batch = self._next_replay_batch(replay_task)
            if self.bs_past is not None:
                replay_batch = self._maybe_trim_batch(replay_batch, self.bs_past)
            replay_batch = self._move_to_device(replay_batch, self.device)
            batch[replay_task] = replay_batch

        return super().training_step(batch, batch_idx)

    # Validation: by default, run standard validation

    # ---------------------------------------------------------------------------------------------
    #  Internals
    # ---------------------------------------------------------------------------------------------
    def _ensure_replay_iters(self):
        # Create iterators (and replace exhausted ones on the fly)
        for task, dl in self._replay_loaders.items():
            self._replay_iters[task] = iter(dl)

    def _next_replay_batch(self, task: str):
        # Validate task exists in provided replay loaders for clearer error messaging
        if task not in self._replay_loaders:
            available = sorted(self._replay_loaders.keys())
            suggestion = difflib.get_close_matches(task, available, n=1)
            hint = f" Did you mean '{suggestion[0]}'?" if suggestion else ""
            raise KeyError(
                f"Unknown replay task '{task}'. Available tasks: {available}.{hint}"
            )
        it = self._replay_iters.get(task)
        if it is None:
            raise RuntimeError(
                f"No iterator for replay task '{task}'. Did you call set_replay_loaders()?"
            )
        try:
            return next(it)
        except StopIteration:
            # Rebuild iterator and continue (cycling behavior)
            self._replay_iters[task] = iter(self._replay_loaders[task])
            return next(self._replay_iters[task])

    def _choose_replay_task(self) -> str:
        past = [t for t in self._replay_loaders.keys()]
        if not past:
            raise RuntimeError("No replay loaders available.")
        if self.per_task_probs:
            # Normalize and sample
            keys, probs = zip(*[(k, self.per_task_probs.get(k, 0.0)) for k in past])
            s = sum(probs)
            if s <= 0:
                raise ValueError("per_task_probs must have at least one positive value.")
            r = random.random() * s
            acc = 0.0
            for k, p in zip(keys, probs):
                acc += p
                if r <= acc:
                    return k
            return keys[-1]
        return random.choice(past)

    @staticmethod
    def _maybe_trim_batch(batch, n: int):
        """Trim batch to first n samples along dim 0 if larger; leave if equal/smaller."""
        if n is None:
            return batch
        def trim(x):
            if torch.is_tensor(x) and x.dim() >= 1 and x.size(0) > n:
                return x[:n]
            return x
        if isinstance(batch, dict):
            return {k: ReplayContinualLearner._maybe_trim_batch(v, n) for k, v in batch.items()}
        if isinstance(batch, (list, tuple)):
            return type(batch)(ReplayContinualLearner._maybe_trim_batch(v, n) for v in batch)
        return trim(batch)

    @staticmethod
    def _move_to_device(batch, device):
        if isinstance(batch, dict):
            return {k: ReplayContinualLearner._move_to_device(v, device) for k, v in batch.items()}
        if isinstance(batch, (list, tuple)):
            return type(batch)(ReplayContinualLearner._move_to_device(v, device) for v in batch)
        if torch.is_tensor(batch):
            return batch.to(device)
        return batch


# class ReplayAllContinualLearner(BaseContinualLearner):
#     """
#     A ContinualLearner that supports replaying past tasks.
#     """
#     def __init__(
#         self,
#         base: nn.Module,
#         heads: Optional[Dict[str, BaseHead]] = None,
#         *,
#         lambda_replay: float = 0.5,
#         per_task_lambda: Optional[Dict[str, float]] = None,
#         **kwargs,
#     ):
#         super().__init__(base=base, heads=heads, **kwargs)
#         self.lambda_replay = lambda_replay
#         self.per_task_lambda = per_task_lambda or {}
#         self.current_tasks = set()

#         if self.lambda_replay > 0.0 and self.per_task_lambda:
#             raise ValueError("Cannot set both global lambda_replay and per_task_lambda.")

#     def set_current_tasks(self, tasks):
#         self.current_tasks = set(tasks)

#     def combine_losses(self, task2loss: Dict[str, Dict[str, Tensor]]):
#         curr_loss, past_loss = 0.0, 0.0
#         if self.lambda_replay > 0.0:
#             for task, loss_dict in task2loss.items():
#                 if task in self.current_tasks:
#                     curr_loss += loss_dict['loss']
#                 else:
#                     past_loss += loss_dict['loss']
#             return curr_loss + self.lambda_replay * past_loss
#         elif self.per_task_lambda:
#             total_loss = 0.0
#             for task, loss_dict in task2loss.items():
#                 weight = self.per_task_lambda[task]
#                 total_loss += weight * loss_dict['loss']
#             return total_loss

#         raise ValueError("Either lambda_replay or per_task_lambda must be set.")

#     def training_step(self, batch, batch_idx: int) -> Tensor:
#         """
#         Training step for the given task.
#         """
#         task2loss = self._step(batch, batch_idx)

#         total_loss = self.combine_losses(task2loss)
#         for task, loss_dict in task2loss.items():
#             for key, value in loss_dict.items():
#                 self.log(f"{task}_train_{key}", value, on_step=True, on_epoch=True)
#         self.log("train_loss", total_loss, on_step=True, on_epoch=True, prog_bar=True)
#         return total_loss

#     def validation_step(self, batch, batch_idx: int) -> Tensor:
#         """
#         Validation step for the given task.
#         """
#         task2loss = self._step(batch, batch_idx)

#         total_loss = self.combine_losses(task2loss)
#         for task, loss_dict in task2loss.items():
#             for key, value in loss_dict.items():
#                 self.log(f"{task}_val_{key}", value, on_step=True, on_epoch=True)
#         self.log("val_loss", total_loss, on_step=True, on_epoch=True, prog_bar=True)
#         return total_loss

#     def test_step(self, batch, batch_idx):
#         pass

#     def on_before_batch_transfer(self, batch: Dict[str, Any], batch_idx: int):
#         """
#         Ensure batch is properly routed to tasks.
#         """
#         batch = super().on_before_batch_transfer(batch, batch_idx)
#         if not self.current_tasks:
#             raise ValueError("current_tasks must be set before training.")
#         return batch