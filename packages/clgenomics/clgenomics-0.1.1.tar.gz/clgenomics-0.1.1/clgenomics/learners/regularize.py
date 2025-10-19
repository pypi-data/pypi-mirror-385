from typing import Dict, Any, Tuple, Optional, Type
import warnings
import torch
from torch import nn, Tensor
from torch.utils.data import DataLoader

from .base import BaseContinualLearner
from ..models.heads import BaseHead


# ============================
# Elastic Weight Consolidation
# ============================
class EWCContinualLearner(BaseContinualLearner):
    """
    Continual learner with Elastic Weight Consolidation (EWC).

    EWC penalizes changes to parameters that are estimated to be important for past tasks,
    to mitigate catastrophic forgetting. After training each task, parameter importance
    (the diagonal of the Fisher information matrix) is estimated and used as a quadratic
    regularization term in subsequent tasks.
    
    This implementation supports multiple variants of online EWC:
    
    - **Online EWC** (Schwarz et al., 2018, *Progress & Compress*): 
      Use `0 < gamma_past <= 1` and `gamma_curr = 1.0`. This recovers the classical online
      Fisher update with exponential decay of past information.
    
    - **EMA-style EWC**: 
      If only one of `gamma_past` or `gamma_curr` is specified, the other is set to 
      `1.0 - gamma_past` or `1.0 - gamma_curr`, respectively. This ensures the Fisher 
      update behaves like an exponential moving average (EMA) between past and current 
      estimates — analogous to the EWC++ update in Arslan et al. (ECCV 2018).
    
    - **Generalized weighting**:
      You may also explicitly set both `0 < gamma_past <= 1` and `0 < gamma_curr <= 1`.
      This enables more flexible update rules beyond the canonical online EWC or EMA-style
      cases. 

    Parameters
    ----------
    base : nn.Module
        The shared backbone/feature extractor used by all tasks.
    heads : dict of {str: BaseHead}, optional
        Mapping from task name to initialized head modules.
    ewc_lambda : float, default=1.0
        Regularization strength controlling the importance of preserving past tasks' parameters.
    online : bool, default=True
        If True, maintains a single running Fisher estimate with exponential decay.
        If False, stores a separate Fisher for each task.
    gamma_past : float, default=0.99
        Decay factor for past Fisher estimates.
    gamma_curr : float, optional
        Scaling factor for the current task's Fisher before accumulation.
        If not provided, it defaults to `1.0 - gamma_past` (following EMA-style updates).
    **kwargs
        Additional arguments passed to `BaseContinualLearner`.

    Notes
    -----
    - When `online=False`, memory requirements grow with the number of tasks as it requires saving
        separate Fisher and mean parameter estimates for each task.
    - Fisher information is typically estimated using the gradients of the log-likelihood
        with respect to model parameters.
    - Online EWC follows Schwarz et al. (2018), *Progress & Compress*.  
        EMA-style updates extend this via Fisher accumulation using an exponential moving average
        (see Arslan et al., ECCV 2018, “Riemannian Walk / EWC++”).  
    """
    def __init__(
        self,
        base: nn.Module,
        heads: Optional[Dict[str, BaseHead]] = None,
        *,
        ewc_lambda: float = 1.0,
        online: bool = True,
        gamma_past: float = 0.99,
        gamma_curr: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(base=base, heads=heads, **kwargs)
        self.ewc_lambda = ewc_lambda
        self.online = online
        if not (0.0 <= gamma_past <= 1.0):
            raise ValueError("gamma_past must be between 0 and 1.")
        self.gamma_past = gamma_past
        self.gamma_curr = gamma_curr if gamma_curr is not None else (1 - gamma_past)

        # For offline mode (multiple fisher/means for each tasks)
        self.task2fisher: Dict[str, Dict[str, Tensor]] = {}
        self.task2means: Dict[str, Dict[str, Tensor]] = {}

        # For online mode (single consolidated Fisher/mean)
        self.fisher_online: Optional[Dict[str, Tensor]] = None
        self.mean_online: Optional[Dict[str, Tensor]] = None
        self.task_count = 0

        if self.ewc_lambda <= 0.0:
            raise ValueError("ewc_lambda must be positive.")

    # ---------------------------------------------------------------------------------------------
    #  EWC utilities (public API)
    # ---------------------------------------------------------------------------------------------
    def setup_ewc(self):
        if self.online:
            if not self.fisher_online:
                # fisher needs to be loaded
                raise ValueError("No online EWC information registered.")
            if not self.mean_online:
                # anchor weights can be loaded or can be pretrained weights
                print('Using the current base weights as the anchor.')
                self.mean_online = self._snapshot_base_params()
            else:
                print('Using the loaded means as the anchor.')
        else:
            if not self.task2fisher or not self.task2means:
                # both fisher and means need to be loaded
                raise ValueError("No task-specific EWC information registered.")

    def update_ewc(
        self,
        dataloader: DataLoader,
        num_batches: int = 128,
        task: Optional[str] = None,
        update_online_mean: bool = True,
    ):
        fisher = self.estimate_fisher(dataloader, num_batches, task)
        self._register_ewc(fisher=fisher, task=task, update_online_mean=update_online_mean)
        self.task_count += 1

    @torch.no_grad()
    def _register_ewc(
        self,
        fisher: Dict[str, Tensor],
        task: Optional[str] = None,
        update_online_mean: bool = True,
    ):
        """Register precomputed (F, theta*). Tensors may be on CPU; they will be moved on use."""
        means = self._snapshot_base_params()
        if self.online:
            if not self.fisher_online:
                self.fisher_online = {k: v.clone() for k, v in fisher.items()}
            else:
                # Online: decay old Fisher and overwrite mean to latest
                for k, v in fisher.items():
                    past = self.fisher_online.get(k, torch.zeros_like(v))
                    self.fisher_online[k] = self.gamma_past * past + self.gamma_curr * v
            if update_online_mean:
                self.mean_online = means
        else:
            task = task or self.active_task
            self.validate_task(task)
            self.task2fisher[task] = {k: v.clone() for k, v in fisher.items()}
            self.task2means[task] = means

    def estimate_fisher(
        self,
        dataloader: DataLoader,
        num_batches: int  = 128,
        task: Optional[str] = None,
    ):
        """
        Estimate diagonal Fisher on the provided dataloader using the model's routed loss.
        Accumulates into self._fisher. Does NOT touch the anchor.
        """
        was_training = self.training
        device = self.device
        
        # Clear GPU memory before Fisher computation
        if device.type == 'cuda':
            torch.cuda.empty_cache()

        def move_to(x, dev):
            if torch.is_tensor(x): return x.to(dev)
            if isinstance(x, dict): return {k: move_to(v, dev) for k, v in x.items()}
            if isinstance(x, (list, tuple)): return type(x)(move_to(v, dev) for v in x)
            return x

        try:
            self.eval()

            # init accumulators
            fisher = {
                n: torch.zeros_like(p, device=device)
                for n, p in self.base.named_parameters()
                if p.requires_grad
            }

            num_accum = 0
            #with torch.enable_grad(): context is more explicit and can lead to more efficient memory management. Otherwise PyTorch might keep additional buffers or intermediate states
            with torch.enable_grad():
                for i, batch in enumerate(dataloader):
                    if i >= num_batches:
                        break
                    batch = move_to(batch, device)

                    # Compute per-batch loss via the model's routing logic
                    self.zero_grad(set_to_none=True)
                    batch['task'] = task  # Add task key for routing
                    routed_batch = self._route(batch)  # Route the batch before _step
                    task2loss = self._step(routed_batch, i)
                    use_task = task or next(iter(task2loss.keys()))
                    loss = task2loss[use_task]["loss"]
                    loss = loss.mean()
                    loss.backward()

                    # Accumulate squared grads
                    for n, p in self.base.named_parameters():
                        if p.requires_grad and p.grad is not None:
                            fisher[n] += p.grad.detach().pow(2)
                    num_accum += 1
                    
                    # Clear cache after each batch to reduce memory fragmentation
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()

            # No batches processed
            if num_accum == 0:
                raise ValueError("No batches were processed; cannot estimate Fisher.")

            # average
            for n in fisher:
                fisher[n] /= float(num_accum)

            return fisher

        finally:
            self.train(mode=was_training)

    def _snapshot_base_params(self):
        return {
            n: p.detach().clone()
            for n, p in self.base.named_parameters()
            if p.requires_grad
        }

    # ---------------------------------------------------------------------------------------------
    #  Lightning hooks
    # ---------------------------------------------------------------------------------------------
    def forward(self, x: Tensor, task: str = None, return_embeddings: bool = False):
        return super().forward(x, task, return_embeddings)

    def predict(self, x: Tensor, task: str = None):
        return super().predict(x, task)

    def _ewc_penalty(self) -> Tensor:
        total = torch.zeros((), device=self.device)

        # Online EWC (one set of Fisher and means)
        if self.online and self.fisher_online is not None and self.mean_online is not None:
            for n, p in self.base.named_parameters():
                if not p.requires_grad:
                    continue
                if n not in self.fisher_online or n not in self.mean_online:
                    warnings.warn(f"Parameter '{n}' missing in EWC information.")
                    continue
                F_n = self.fisher_online[n].to(device=p.device, dtype=p.dtype)
                mu_n = self.mean_online[n].to(device=p.device, dtype=p.dtype)
                total += (F_n * (p - mu_n).pow(2)).sum()

        # Task-specific EWC (separate Fisher and means for each task)
        elif self.task2fisher and self.task2means:
            # for F, M in zip(self.task2fisher.values(), self.task2means.values()):
            for tname, F in self.task2fisher.items():
                M = self.task2means[tname]
                part = torch.zeros((), device=self.device)
                for n, p in self.base.named_parameters():
                    if not p.requires_grad:
                        continue
                    if n not in F or n not in M:
                        warnings.warn(f"Parameter '{n}' missing in EWC information.")
                        continue
                    F_n = F[n].to(device=p.device, dtype=p.dtype)
                    mu_n = M[n].to(device=p.device, dtype=p.dtype)
                    part += (F_n * (p - mu_n).pow(2)).sum()
                total += part

        else:
            raise ValueError("No EWC information registered; cannot compute penalty.")

        return total

    def training_step(self, batch, batch_idx):
        """
        Training step for the given task.
        """
        task2loss = self._step(batch, batch_idx)
        total_loss = self._combine_losses(task2loss)
        self._log_dicts(batch, task2loss, split="train")

        # EWC penalty  # TODO: consider simplifying this so that super().training_step can be used
        reg = self._ewc_penalty()
        self.log("ewc_loss_raw", reg.detach(), on_step=True, on_epoch=True)
        self.log("ewc_loss", self.ewc_lambda * reg.detach(), on_step=True, on_epoch=True)
        self.log("ewc_penalty_ratio", (self.ewc_lambda * reg.detach())/total_loss, on_step=True, on_epoch=False)
        total_loss = total_loss + self.ewc_lambda * reg

        self.log("train_loss", total_loss, on_step=True, on_epoch=True, prog_bar=True)
        return total_loss

    def validation_step(self, batch, batch_idx: int):
        return super().validation_step(batch, batch_idx)

    # ---------------------------------------------------------------------------------------------
    # Checkpointing
    # ---------------------------------------------------------------------------------------------
    def on_save_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        super().on_save_checkpoint(checkpoint)

        # Save EWC information
        if self.online:
            checkpoint['fisher_online'] = self.fisher_online
            checkpoint['mean_online'] = self.mean_online
        else:
            checkpoint['task2fisher'] = self.task2fisher
            checkpoint['task2means'] = self.task2means
        checkpoint['task_count'] = self.task_count

    def on_load_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        super().on_load_checkpoint(checkpoint)

        # Load EWC information
        if 'fisher_online' in checkpoint and 'mean_online' in checkpoint:
            print('Loading online EWC information...')
            self.fisher_online = checkpoint.get('fisher_online', {})
            self.mean_online = checkpoint.get('mean_online', {}) # or self._snapshot_base_params()
        elif 'task2fisher' in checkpoint and 'task2means' in checkpoint:
            print('Loading task-specific EWC information...')
            self.task2fisher = checkpoint.get('task2fisher', {})
            self.task2means = checkpoint.get('task2means', {})

        if 'task_count' in checkpoint:
            self.task_count = checkpoint['task_count']


# =========================
# L2 to pretrained weights
# =========================
class L2ContinualLearner(BaseContinualLearner):
    """
    Adds a quadratic penalty on the deviation of BASE parameters
    from the pretrained (initial) base weights: lambda * ||theta - theta_0||^2
    """
    def __init__(
        self,
        base: nn.Module,
        heads: Optional[Dict[str, BaseHead]] = None,
        *,
        l2_lambda: float = 1.0,
        online: bool = False,
        **kwargs,
    ):
        super().__init__(base=base, heads=heads, **kwargs)

        self.l2_lambda = l2_lambda
        if self.l2_lambda <= 0.0:
            raise ValueError("l2_lambda must be positive.")
        self.online = online
        self.base_anchor: Dict[str, Tensor] = {}

    # ---------------------------------------------------------------------------------------------
    #  Public API
    # ---------------------------------------------------------------------------------------------
    def setup_l2(self):
        if self.online:
            self.base_anchor = self._snapshot_base_params()
        else:
            if not self.base_anchor:
                raise ValueError("The base anchor needs to be loaded if not online.")

    def set_base_anchor(self):
        self.base_anchor = self._snapshot_base_params()

    def _snapshot_base_params(self):
        return {
            n: p.detach().clone()
            for n, p in self.base.named_parameters()
            if p.requires_grad
        }

    # ---------------------------------------------------------------------------------------------
    #  Lightning hooks
    # ---------------------------------------------------------------------------------------------
    def _l2_penalty(self) -> Tensor:
        total = torch.zeros((), device=self.device)
        for n, p in self.base.named_parameters():
            if not p.requires_grad or n not in self.base_anchor:
                continue
            anchor = self.base_anchor[n].to(p.device)
            total = total + (p - anchor).pow(2).sum()
        return total

    def training_step(self, batch, batch_idx):
        """
        Training step for the given task.
        """
        task2loss = self._step(batch, batch_idx)
        total_loss = self._combine_losses(task2loss)
        self._log_dicts(batch, task2loss, split="train")

        # L2 penalty # TODO: consider simplifying this so that super().training_step can be used
        reg = self._l2_penalty()
        self.log("l2_loss_raw", reg.detach(), on_step=True, on_epoch=True)
        self.log("l2_loss", (self.l2_lambda * reg).detach(), on_step=True, on_epoch=True)

        total_loss = total_loss + self.l2_lambda * reg
        self.log("train_loss", total_loss, on_step=True, on_epoch=True, prog_bar=True)
        return total_loss

    # ---------------------------------------------------------------------------------------------
    # Checkpointing
    # ---------------------------------------------------------------------------------------------
    def on_save_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        super().on_save_checkpoint(checkpoint)

        if not self.online:
            # offline means we use a specific anchor instead of weights right before
            checkpoint['base_anchor'] = self.base_anchor

    def on_load_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        super().on_load_checkpoint(checkpoint)

        if 'base_anchor' in checkpoint:
            print('Loading base anchor information...')
            self.base_anchor = checkpoint['base_anchor']
