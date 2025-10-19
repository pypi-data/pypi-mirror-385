from __future__ import annotations
from typing import Dict, Any, Optional, Type
import torch
from torch import nn, Tensor
from ...metrics import MeanPearsonCorrCoefPerChannel


class BaseHead(nn.Module):
    """
    A task head implements:
      - forward(embeds, batch): pure head logic on embeddings
      - compute_loss(outputs, batch): returns loss dict
      - compute_metrics(batch, base): optional, for validation/test

    For non-trivial tasks (needing raw x / different embed flow), override forward_with_base.
    """

    def forward(self, embeds: Tensor, **ctx) -> Any:
        """
        ctx: optional task-specific hints, e.g. mask, lengths, temperature.
        """
        raise NotImplementedError("Subclasses must implement forward()")

    def forward_with_base(self, x: Tensor, base: nn.Module, base_trainable: bool = None, **ctx) -> Any:
        # If base_trainable not provided, check it (but only once, caller should cache this)
        if base_trainable is None:
            base_trainable = any(p.requires_grad for p in base.parameters())
        with torch.set_grad_enabled(base_trainable):
            embeds = base(x)
        return self.forward(embeds, **ctx)

    def predict(self, embeds: Tensor, **ctx) -> Any:
        """
        Predict outputs from embeddings. Default is to call forward.
        """
        with torch.no_grad():
            return self.forward(embeds, **ctx)

    def predict_with_base(self, x: Tensor, base: nn.Module, **ctx) -> Any:
        """
        Predict outputs from raw input x using the base model.
        """
        with torch.no_grad():
            embeds = base(x)
            return self.predict(embeds, **ctx)

    def compute_loss(
        self,
        outputs: Tensor,
        batch: Dict[str, Any],
    ) -> Dict[str, Tensor]:
        """
        Compute the loss for the given outputs and batch.
        The output dict must contain "loss" for the total loss.
        """
        raise NotImplementedError("Subclasses must implement compute_loss()")

    @torch.no_grad()
    def compute_metrics(self, batch: Dict[str, Any], base: nn.Module) -> Dict[str, Any]:
        """
        Compute metrics for the given batch.
        """
        return {}

    def validate_batch(self, batch: Any) -> bool:
        """
        Validate the batch structure. Override if your head requires specific batch format.
        """
        if not isinstance(batch, dict):
            raise ValueError("Batch must be a dict containing 'x' and 'y' keys.")
        if 'x' not in batch or 'y' not in batch:
            raise KeyError("Batch must contain 'x' and 'y' keys.")
        return True

    # ---- Config for save/load ----
    def to_config(self) -> Dict[str, Any]:
        """
        Return init config to reconstruct this head.
        Keep it small & JSON-serializable.
        """
        raise NotImplementedError("Subclasses must implement to_config()")

    @classmethod
    def from_config(cls, cfg: Dict[str, Any]) -> "BaseHead":
        return cls(**cfg)
