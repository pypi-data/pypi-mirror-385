import torch
import pytorch_lightning as pl
from torch import nn, Tensor
from pathlib import Path
from typing import Any

from ..models.heads import HEAD_REGISTRY, BaseHead
from ..adapters import ADAPTER_REGISTRY, BaseAdapter


class BaseContinualLearner(pl.LightningModule):
    """
    A PyTorch Lightning module for continual learning with multiple heads.

    Parameters
    ----------
    base : nn.Module
        The shared backbone/feature extractor used by all tasks.
    heads : dict of {str: BaseHead}, optional
        Mapping from task name to initialized head modules.
    base_trainable : bool, default=False
        Whether the base's parameters start unfrozen.
    lr_base : float, default=1e-3
        Learning rate for trainable base parameters.
    lr_head : float, default=1e-3
        Learning rate for trainable head parameters.
    weight_decay : float, default=0.0
        Weight decay applied to both parameter groups.
    scheduler_name : str, optional
        Name of a scheduler from `torch.optim.lr_scheduler` to use (e.g., 'ReduceLROnPlateau').
    scheduler_kwargs : dict, optional
        Keyword arguments passed to the scheduler constructor.
    lr_scheduler_kwargs : dict, optional
        Additional kwargs for configuring the LR scheduler in PyTorch Lightning.
        (e.g., `{"interval": "epoch", "frequency": 1}` or `{"monitor": "valid_loss"}`).
    """

    def __init__(
        self,
        base: nn.Module,
        heads: dict[str, BaseHead] | None = None,
        *,
        base_trainable: bool = False,
        lr_base: float = 1e-3,
        lr_head: float = 1e-3,
        weight_decay: float = 0.0,
        scheduler_name: str | None = None,
        scheduler_kwargs: dict | None = None,
        lr_scheduler_kwargs: dict | None = None,
        active_task: str | None = None,  # For backward compatibility with old checkpoints
    ):
        super().__init__()
        self.save_hyperparameters(ignore=["base", "heads", "active_task"])
        self.base: nn.Module = base
        self.heads = nn.ModuleDict(heads or {})
        self.base_trainable: bool = base_trainable
        self.lr_base: float = lr_base
        self.lr_head: float = lr_head
        self.weight_decay: float = weight_decay
        self.scheduler_name: str | None = scheduler_name
        self.scheduler_kwargs: dict = scheduler_kwargs or {}
        self.lr_scheduler_kwargs: dict = lr_scheduler_kwargs or {}

        # Initialize adapter to None
        self.adapter: BaseAdapter | None = None  # optional adapter

        # For backward compatibility. Use activate_task() instead.
        self.active_task: str | None = active_task

        if self.base_trainable:
            self.unfreeze_base()
        else:
            self.freeze_base()

    # ---------------------------------------------------------------------------------------------
    #  Task/Head helpers
    # ---------------------------------------------------------------------------------------------
    def add_head(self, task: str, head: BaseHead, activate: bool = False):
        if task in self.heads:
            raise ValueError(f"Task '{task}' already exists.")
        self.heads[task] = head
        if activate:
            self.activate_task(task)

    def delete_head(self, task: str):
        if task not in self.heads:
            raise ValueError(f"Task '{task}' not found.")
        del self.heads[task]

    def get_heads(self) -> dict[str, BaseHead]:
        return {task: head for task, head in self.heads.items()}

    def get_tasks(self) -> list[str]:
        return list(self.heads.keys())

    def activate_task(self, task: str):
        """
        Set the active task head/adapter for forward/predict if not specified.
        """
        if task not in self.heads:
            raise ValueError(f"Task '{task}' not found.")
        if self.adapter is not None and self.adapter.active_adapter != task:
            self.activate_adapter(task)
        self.active_task = task

    def validate_task(self, task: str | None):
        if task is None:
            raise ValueError(
                "Task must be specified either by passing it as an argument "
                "or calling 'activate_task()'."
            )
        if task not in self.heads:
            raise ValueError(f"Task '{task}' not found. Available tasks: {self.get_tasks()}")

    def save_head(self, task: str, path: Path | str):
        head = self.heads[task]
        payload = {
            "cls": getattr(head, "_registry_name", head.__class__.__name__),
            "cfg": head.to_config(),
            "state_dict": head.state_dict(),
        }
        torch.save(payload, path)

    def load_head(self, path: Path | str, task: str, strict: bool = True):
        payload = torch.load(path, map_location="cpu")
        cls_name, cfg, state = payload["cls"], payload["cfg"], payload["state_dict"]
        head_cls = HEAD_REGISTRY[cls_name]
        head = head_cls.from_config(cfg)
        head.load_state_dict(state, strict=strict)
        self.add_head(task=task, head=head)

    # ------ Adapter utilities ------
    def init_adapter(self, adapter_type="peft", **kwargs) -> None:
        if self.adapter is not None:
            raise ValueError("An adapter is already attached.")
        if adapter_type not in ADAPTER_REGISTRY:
            raise ValueError(f"Unknown adapter type: {adapter_type}")
        AdapterCls = ADAPTER_REGISTRY[adapter_type]
        adapter = AdapterCls(base=self.base, **kwargs)
        self.attach_adapter(adapter)

    def attach_adapter(self, adapter: BaseAdapter):
        if self.adapter is not None:
            raise ValueError(
                "A BaseAdapter is already attached. Call detach_adapter() first to attach a new one."
            )
        self.adapter = adapter

    def detach_adapter(self):
        if self.adapter is None:
            raise ValueError("No BaseAdapter attached. Nothing to detach.")
        self.adapter = None

    def add_adapter(self, task: str, cfg: dict[str, Any], activate: bool = False):
        if self.adapter is None:
            raise ValueError("No BaseAdapter attached. Call attach_adapter() first.")
        if task not in self.heads:
            raise ValueError(
                f"No head found for task '{task}'. Adapter needs a corresponding head."
            )  # could be warning instead
        self.adapter.add_adapter(adapter_name=task, cfg=cfg, activate=activate)
        if activate:
            self.activate_task(task)

    def delete_adapter(self, task: str):
        if self.adapter is None:
            raise ValueError("No BaseAdapter attached. Call attach_adapter() first.")
        self.adapter.delete_adapter(adapter_name=task)
        if self.active_task == task:
            self.active_task = None

    def activate_adapter(self, task: str):
        if self.adapter is None:
            raise ValueError("No BaseAdapter attached. Call attach_adapter() first.")
        self.validate_task(task)
        self.adapter.activate_adapter(adapter_name=task)

    # ---------------------------------------------------------------------------------------------
    #  Freezing utilities
    # ---------------------------------------------------------------------------------------------
    def freeze_base(self):
        """Freeze all parameters in the base model including adapters if attached."""
        for p in self.base.parameters():
            p.requires_grad = False
        self.base_trainable = False

    def unfreeze_base(self):
        """Unfreeze all parameters in the base model including adapters if attached."""
        for p in self.base.parameters():
            p.requires_grad = True
        self.base_trainable = True

    def _set_head_trainable(self, tasks: str | list[str], requires_grad: bool, strict: bool = True):
        if isinstance(tasks, str):
            tasks = [tasks]
        for task in tasks:
            if task not in self.heads:
                if strict:
                    raise ValueError(f"Task '{task}' not found.")
                else:
                    print(f"Warning: Task '{task}' not found; skipping.")
                    continue
            for p in self.heads[task].parameters():
                p.requires_grad = requires_grad

    def freeze_head(self, tasks: str | list[str]):
        """Freeze all parameters in the head(s) for the specified task(s)."""
        self._set_head_trainable(tasks, requires_grad=False)

    def unfreeze_head(self, tasks: str | list[str]):
        """Unfreeze all parameters in the head(s) for the specified task(s)."""
        self._set_head_trainable(tasks, requires_grad=True)

    def freeze_all_heads(self):
        """Freeze all parameters in all heads."""
        tasks = self.get_tasks()
        self._set_head_trainable(tasks, requires_grad=False)

    def unfreeze_all_heads(self):
        """Unfreeze all parameters in all heads."""
        tasks = self.get_tasks()
        self._set_head_trainable(tasks, requires_grad=True)

    def freeze_inactive_heads(self):
        """Freeze all heads except the active one."""
        if self.active_task is None:
            raise ValueError("Call activate_task() to set the active task.")
        tasks = [t for t in self.get_tasks() if t != self.active_task]
        self._set_head_trainable(tasks, requires_grad=False, strict=False)

    # ------ Adapter helpers ------
    def freeze_adapter(self, tasks: str | list[str]):
        """Freeze all parameters in the adapters."""
        if self.adapter is not None:
            self.adapter.freeze_adapter(adapter_names=tasks)
        else:
            print("No adapter attached; nothing to freeze.")

    def unfreeze_adapter(self, tasks: str | list[str]):
        """Unfreeze all parameters in the adapters."""
        if self.adapter is not None:
            self.adapter.unfreeze_adapter(adapter_names=tasks)
        else:
            print("No adapter attached; nothing to unfreeze.")

    # ---------------------------------------------------------------------------------------------
    #  Lightning hooks and internals # TODO: consider sorting methods
    # ---------------------------------------------------------------------------------------------
    def forward(self, x: Tensor, task: str | None = None, return_embeddings: bool = False) -> Any:
        """
        Parameters
        ----------
        x : Tensor
            Input tensor.
        task : str, optional
            Task name. If None, will use the active task.
        return_embeddings : bool, default=False
            If True, return the embeddings from the base model without passing through the head.
        """
        if self.adapter is not None:
            # Adapter needs to be set before base forward
            task = task or self.active_task
            self.adapter.activate_adapter(adapter_name=task)
            embeds = self.base(x)
            if return_embeddings:
                return embeds
            self.validate_task(task)  # check "head" existence
            head: BaseHead = self.heads[task]
            return head.forward(embeds)
        else:
            embeds = self.base(x)
            if return_embeddings:
                return embeds
            task = task or self.active_task
            self.validate_task(task)
            head: BaseHead = self.heads[task]
            return head.forward(embeds)

    def predict(self, x: Tensor, task: str | None = None) -> Any:
        """
        Note
        - Logic is simpler than `forward()` because we don't need to handle return_embeddings,
          which does not require active head but does require active adapter if using adapter.
        """
        with torch.no_grad():
            task = task or self.active_task
            self.validate_task(task)
            if self.adapter is not None:
                self.adapter.activate_adapter(adapter_name=task)
            embeds = self.base(x)
            head: BaseHead = self.heads[task]
            return head.predict(embeds)

    def _route(self, batch):
        """
        Route the batch and outputs dict of {task: sub-batch}.
        """
        # A) Dict of loaders keyed by task name
        if isinstance(batch, dict) and any(k in self.heads for k in batch.keys()):
            return batch

        # B) Single loader with 'task' key
        if isinstance(batch, dict) and "task" in batch:
            return {batch["task"]: batch}

        # C) Single loader without 'task' key
        if self.active_task is not None:
            return {self.active_task: batch}

        raise KeyError(
            "Cannot resolve task. Please "
            "(A) provide dict of loaders keyed by task name, "
            "(B) provide 'task' key in batch, or "
            "(C) activate a task by 'activate_task()'."
        )

    def on_before_batch_transfer(self, batch, batch_idx: int = 0):
        """
        Ensure batch is properly routed to tasks.
        It returns batch as a dict of {task: sub-batch}.
        """
        routed = self._route(batch)

        # Check if heads are set for each task
        missing_tasks = set(routed.keys()) - set(self.heads.keys())
        if missing_tasks:
            raise KeyError(
                f"Tasks {missing_tasks} not found in heads. "
                f"Available tasks: {list(self.heads.keys())}"
            )

        # Check sub-batch structure
        for task, subbatch in routed.items():
            if hasattr(self.heads[task], "validate_batch"):
                self.heads[task].validate_batch(subbatch)

        return routed

    def _step(self, batch: dict[str, Any], batch_idx: int) -> dict[str, Tensor]:
        task2loss = {}
        for task, subbatch in batch.items():
            outputs = self.forward(subbatch["x"], task=task)
            loss_dict = self.heads[task].compute_loss(outputs, subbatch)
            task2loss[task] = loss_dict

        return task2loss

    def _metrics_step(self, batch: dict[str, Any]) -> dict[str, Tensor]:
        task2metrics = {}
        for task, subbatch in batch.items():
            if self.adapter is not None:
                self.adapter.activate_adapter(adapter_name=task)
            metrics_dict = self.heads[task].compute_metrics(subbatch, self.base)
            task2metrics[task] = metrics_dict

        return task2metrics

    def _combine_losses(self, task2loss: dict[str, dict[str, Tensor]]) -> Tensor:
        total_loss = 0.0
        for task, loss_dict in task2loss.items():
            total_loss += loss_dict["loss"]
        return total_loss

    def _log_dicts(self, batch: dict[str, Any], task2dict: dict[str, dict], split: str) -> int:
        total_bs = 0
        for task, taskdict in task2dict.items():
            if taskdict is None:
                continue
            bs = batch[task]["x"].size(0)
            for key, value in taskdict.items():
                if key != "batch_size":
                    self.log(
                        f"{task}_{split}_{key}",
                        value,
                        on_step=True if split == "train" else False,
                        on_epoch=True,
                        batch_size=bs,
                    )
            total_bs += bs
        return total_bs

    def training_step(self, batch: dict[str, Any], batch_idx: int) -> Tensor:
        """
        Training step for the given task.
        """
        task2loss = self._step(batch, batch_idx)
        total_loss = self._combine_losses(task2loss)

        # Logging
        total_bs = self._log_dicts(batch, task2loss, split="train")
        self.log(
            "train_loss",
            total_loss,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            batch_size=total_bs,
        )
        return total_loss

    def validation_step(self, batch: dict[str, Any], batch_idx: int) -> Tensor:
        """
        Validation step for the given task.
        """
        task2loss = self._step(batch, batch_idx)
        total_loss = self._combine_losses(task2loss)
        task2metrics = self._metrics_step(batch)  # TODO: avoid double forward pass

        # Logging
        total_bs = self._log_dicts(batch, task2loss, split="valid")
        self.log(
            "valid_loss",
            total_loss,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            batch_size=total_bs,
        )
        self._log_dicts(batch, task2metrics, split="valid")
        return total_loss

    def test_step(self, batch, batch_idx):
        pass

    def configure_optimizers(self):
        base_params = [p for p in self.base.parameters() if p.requires_grad]
        head_params = [p for h in self.heads.values() for p in h.parameters() if p.requires_grad]

        groups = []
        if base_params:
            groups.append(
                {"params": base_params, "lr": self.lr_base, "weight_decay": self.weight_decay}
            )  # TODO: Exclude biases/LayerNorm from weight decay
        if head_params:
            groups.append(
                {"params": head_params, "lr": self.lr_head, "weight_decay": self.weight_decay}
            )
        if not groups:
            raise ValueError("No trainable parameters found in base or heads.")

        optimizer = torch.optim.AdamW(groups)  # TODO: make optimizer configurable

        if not self.scheduler_name:
            return optimizer

        scheduler_class = getattr(torch.optim.lr_scheduler, self.scheduler_name)
        scheduler = scheduler_class(optimizer, **(self.scheduler_kwargs or {}))
        cfg = {"optimizer": optimizer}
        if self.lr_scheduler_kwargs is not None:
            cfg["lr_scheduler"] = {**{"scheduler": scheduler}, **self.lr_scheduler_kwargs}
        else:
            if isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                cfg["lr_scheduler"] = {"scheduler": scheduler, "monitor": "valid_loss"}
            else:
                cfg["lr_scheduler"] = {"scheduler": scheduler, "interval": "epoch", "frequency": 1}
        return cfg

    # ---------------------------------------------------------------------------------------------
    # Checkpointing
    # ---------------------------------------------------------------------------------------------
    def on_save_checkpoint(self, checkpoint: dict[str, Any]) -> None:
        checkpoint["heads_meta"] = self._save_heads_meta()
        checkpoint["adapter_meta"] = self._save_adapter_meta()

    def on_load_checkpoint(self, checkpoint: dict[str, Any]) -> None:
        self._load_heads_meta(checkpoint)
        self._load_adapter_meta(checkpoint)

    def _save_heads_meta(self) -> dict[str, Any]:
        """
        Return metadata for all heads for checkpointing.
        """
        return {
            task: {
                "cls": getattr(head, "_registry_name", head.__class__.__name__),
                "cfg": head.to_config(),
            }
            for task, head in self.heads.items()
        }

    def _save_adapter_meta(self) -> dict[str, Any] | None:
        """
        Return metadata for the adapter for checkpointing.
        """
        if getattr(self, "adapter", None) is not None:
            return self.adapter.to_config()
        return None

    def _load_heads_meta(self, checkpoint: dict[str, Any]) -> None:
        """
        Load heads from metadata in checkpoint.
        """
        heads_meta: dict[str, Any] | None = checkpoint.get("heads_meta", None)
        if not heads_meta:
            return

        rebuilt = {}
        for task, info in heads_meta.items():
            cls_name = info["cls"]
            cfg = info.get("cfg", {})
            if cls_name not in HEAD_REGISTRY:
                raise KeyError(f"Unknown head class '{cls_name}' in registry.")
            head_cls = HEAD_REGISTRY[cls_name]
            rebuilt[task] = head_cls.from_config(cfg)
        # Only set missing tasks to avoid clobbering heads passed explicitly to __init__
        for task, head in rebuilt.items():
            if task not in self.heads:
                self.heads[task] = head

    def _load_adapter_meta(self, checkpoint: dict[str, Any]) -> None:
        """
        Load adapter from metadata in checkpoint.
        """
        adapter_meta: dict[str, Any] | None = checkpoint.get("adapter_meta", None)
        if not adapter_meta:
            return
        cls_name = adapter_meta["cls"]
        if cls_name not in ADAPTER_REGISTRY:
            raise KeyError(f"Unknown adapter class '{cls_name}' in registry.")
        AdapterCls = ADAPTER_REGISTRY[cls_name]
        adapter = AdapterCls(base=self.base)
        adapter.load_from_meta(adapter_meta)
        self.adapter = adapter
        # Align active task; comment out to avoid unexpected assignment for now
        # if adapter.active_adapter is not None:
        #     self.active_task = adapter.active_adapter

    # ---------------------------------------------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------------------------------------------
    def print_model_summary(self) -> None:
        """
        Print a table summarizing parameter counts for base and each head.
        """
        print_model_summary(self)

# Alias
ContinualLearner = BaseContinualLearner


def _humanize(n: int) -> str:
    import math
    if n < 1_000:
        return str(n)
    units = ["", "K", "M", "B", "T"]
    k = max(0, min(int(math.floor(math.log10(n) / 3)), len(units) - 1))
    return f"{n / (1000 ** k):.2f} {units[k]}".rstrip("0").rstrip(".")


def _count_params(module: nn.Module, *, trainable_only: bool = False) -> int:
    total = 0
    for _, p in module.named_parameters(recurse=True):
        if trainable_only and not p.requires_grad:
            continue
        total += p.numel()
    return total


def print_model_summary(model: BaseContinualLearner) -> None:
    rows = []

    # Base (includes any adapters as part of base)
    base_type = type(model.base).__name__
    base_total = _count_params(model.base)
    base_train = _count_params(model.base, trainable_only=True)
    base_mode  = "train" if model.base.training else "eval"
    rows.append(("base", base_type, base_train, base_total, base_mode))

    # Each head individually: head (<key>)
    for key, head in model.heads.items():
        htype = type(head).__name__
        h_total = _count_params(head)
        h_train = _count_params(head, trainable_only=True)
        h_mode  = "train" if head.training else "eval"
        rows.append((f"head ({key})", htype, h_train, h_total, h_mode))

    # Column widths
    name_w = max(4, *(len(r[0]) for r in rows))
    type_w = max(4, *(len(r[1]) for r in rows))
    tr_w   = max(9, *(len(_humanize(r[2])) for r in rows))   # Trainable
    tot_w  = max(5, *(len(_humanize(r[3])) for r in rows))   # Total
    mode_w = max(4, *(len(r[4]) for r in rows))

    # Header + separator
    header = (
        f"  | {'Name':<{name_w}} | {'Type':<{type_w}} | "
        f"{'Trainable':>{tr_w}} | {'Total':>{tot_w}} | {'Mode':<{mode_w}}"
    )
    sep = "-" * (len(header) + 3)
    print(header)
    print(sep)

    # Rows
    for name, typ, tr, tot, mode in rows:
        print(
            f"  | {name:<{name_w}} | {typ:<{type_w}} | "
            f"{_humanize(tr):>{tr_w}} | {_humanize(tot):>{tot_w}} | {mode:<{mode_w}}"
        )

    print(sep)

    # Totals
    grand_train = sum(r[2] for r in rows)
    grand_total = sum(r[3] for r in rows)
    print(f"Trainable params: {_humanize(grand_train)}")
    print(f"Total params:     {_humanize(grand_total)}")
