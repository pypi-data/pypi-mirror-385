from typing import Dict, Any, Tuple, Optional, Type
import torch
import numpy as np
import torch.nn.functional as F
from torch import nn, Tensor

from . import BaseHead, register_head
from ...losses import create_loss

from torchmetrics.regression import MeanSquaredError
from ...metrics import MeanPearsonCorrCoefPerChannel


@register_head()
class EnformerHead(BaseHead):
    def __init__(
        self,
        loss_fn_name: str = "PoissonNLLoss",
        in_channels: int = 3072,
        out_channels: int = 5313,
        use_softplus: bool = True,
        # label_aware_dual_MSEloss loss function arguments
        ref_y: Tensor | None = None,
        alpha: float = 0.5,
        rescale: bool = False,
    ):
        super().__init__()
        if loss_fn_name == "label_aware_dual_MSEloss":
            self.loss_fn = create_loss(loss_fn_name, ref_y=ref_y, alpha=alpha, rescale=rescale)
        else:
            self.loss_fn = create_loss(loss_fn_name)
        self.head = nn.Linear(in_features=in_channels, out_features=out_channels, bias=True)
        if use_softplus:
            self.softplus = nn.Softplus()
        else:
            self.softplus = nn.Identity()

        # Config for save/load
        self._cfg = {
            "loss_fn_name": loss_fn_name,
            "in_channels": in_channels,
            "out_channels": out_channels,
            "use_softplus": use_softplus,
        }

        # Store loss function parameters for checkpointing
        if loss_fn_name == "label_aware_dual_MSEloss":
            self._cfg.update({
                "ref_y": ref_y,
                "alpha": alpha,
                "rescale": rescale,
            })

    def forward(self, embeds: Tensor) -> Tensor:
        return self.softplus(self.head(embeds))

    def _align_outputs_and_labels(self, outputs: Tensor, y_true: Tensor) -> tuple[Tensor, Tensor]:
        """
        Align outputs and labels by center-cropping based on their shapes.
        Returns (aligned_outputs, aligned_y_true).
        """
        # Normalize y to have at least 2 dims: [B, C]
        if y_true.dim() == 1:
            y_true = y_true.unsqueeze(-1)

        if outputs.dim() == 3:
            L_out = outputs.shape[1]
            if y_true.dim() == 2:
                center_idx = L_out // 2
                outputs = outputs[:, center_idx, :]
            elif y_true.dim() == 3:
                L_y = y_true.shape[1]
                if L_y == 1 and L_out > 1:
                    center_idx = L_out // 2
                    outputs = outputs[:, center_idx, :]
                    y_true = y_true[:, 0, :]
                elif L_y < L_out:
                    start = max(0, (L_out - L_y) // 2)
                    end = start + L_y
                    outputs = outputs[:, start:end, :]
                elif L_y > L_out:
                    y_start = max(0, (L_y - L_out) // 2)
                    y_end = y_start + L_out
                    y_true = y_true[:, y_start:y_end, :]
        return outputs, y_true

    def compute_loss(
        self,
        outputs: Tensor,
        batch: Dict[str, Any],
    ) -> Dict[str, Tensor]:
        y_true = batch["y"]
        outputs, y_true = self._align_outputs_and_labels(outputs, y_true)
        # Mask NaNs similar to Lightning code to avoid invalid pairwise ops in loss
        if torch.isnan(y_true).any():
            # For 2D [B, C], remove any sample with any NaN across channels
            reduce_dims = tuple(range(1, y_true.dim())) if y_true.dim() > 1 else ()
            valid_mask = (~torch.isnan(y_true)).all(dim=reduce_dims) if reduce_dims else ~torch.isnan(y_true)
            if valid_mask.any():
                loss = self.loss_fn(outputs[valid_mask], y_true[valid_mask])
            else:
                loss = torch.tensor(0.0, device=y_true.device, requires_grad=True)
        else:
            loss = self.loss_fn(outputs, y_true)
        loss = loss.mean()  # Average over the batch
        return {"loss": loss}

    def compute_metrics(self, batch, base):
        # Compute predictions using base model embeddings -> head
        with torch.no_grad():
            embeds = base(batch["x"])
            outputs = self(embeds)

        y_true = batch["y"]
        outputs, y_true = self._align_outputs_and_labels(outputs, y_true)

        # Reduce any remaining 3D to 2D if sequence length is 1 bin
        if outputs.dim() == 3 and outputs.shape[1] == 1:
            outputs = outputs[:, 0, :]
        if y_true.dim() == 3 and y_true.shape[1] == 1:
            y_true = y_true[:, 0, :]

        # Create sample-level valid mask (exclude samples with any NaNs)
        if torch.isnan(y_true).any():
            reduce_dims = tuple(range(1, y_true.dim()))
            valid_mask = (~torch.isnan(y_true)).all(dim=reduce_dims)
            if valid_mask.any():
                outputs_valid = outputs[valid_mask]
                y_valid = y_true[valid_mask]
            else:
                return {
                    "pearson_R": torch.tensor(0.0, device=y_true.device),
                    "poisson": torch.tensor(0.0, device=y_true.device),
                }
        else:
            outputs_valid = outputs
            y_valid = y_true

        # Metrics
        pcc_metric = MeanPearsonCorrCoefPerChannel(n_channels=self.head.out_features).to(
            outputs_valid.device
        )
        pearson = pcc_metric(outputs_valid, y_valid).mean()

        poisson_loss = torch.nn.PoissonNLLLoss(log_input=False)
        poisson = poisson_loss(outputs_valid, y_valid)

        return {"Pearson_Corr_Coef": pearson, "Poisson_NLL": poisson}

    def to_config(self) -> Dict[str, Any]:
        return dict(self._cfg)

    @classmethod
    def from_config(cls, cfg: Dict[str, Any]) -> "EnformerHead":
        """Create EnformerHead from config dictionary."""
        # Extract loss function specific parameters
        loss_fn_name = cfg.get("loss_fn_name", "PoissonNLLLoss")
        ref_y = cfg.get("ref_y", None)
        alpha = cfg.get("alpha", 0.5)
        rescale = cfg.get("rescale", False)

        return cls(
            loss_fn_name=loss_fn_name,
            in_channels=cfg["in_channels"],
            out_channels=cfg["out_channels"],
            use_softplus=cfg.get("use_softplus", True),
            ref_y=ref_y,
            alpha=alpha,
            rescale=rescale,
        )

    def load_weights(self, conv: nn.Conv1d, freeze: bool = False):
        # Shapes must match: (out_c, in_c, k)
        if conv.weight.shape != self.head.weight.shape:
            raise ValueError(f"Shape mismatch: {conv.weight.shape} vs {self.head.weight.shape}")

        with torch.no_grad():
            self.head.weight.copy_(conv.weight)
            if conv.bias is not None and self.head.bias is not None:
                self.head.bias.copy_(conv.bias)

        if freeze:
            for p in self.head.parameters():
                p.requires_grad = False
