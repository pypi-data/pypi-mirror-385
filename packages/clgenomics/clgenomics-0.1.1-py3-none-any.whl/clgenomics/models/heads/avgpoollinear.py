from typing import Dict, Any
from torch import nn, Tensor

from . import BaseHead, register_head
from ...losses import create_loss


@register_head()
class AvgPoolLinearHead(BaseHead):
    def __init__(
        self,
        in_dim: int,
        num_classes: int = 1,
        loss_fn_name: str = "MNLLLoss",
    ):
        super().__init__()
        self.head = nn.Linear(in_dim, num_classes)
        self.loss_fn_name = loss_fn_name
        self.loss_fn = create_loss(loss_fn_name)

        # Config for save/load
        self._cfg = {
            "in_dim": in_dim,
            "num_classes": num_classes,
            "loss_fn_name": loss_fn_name,
        }

    def forward(self, embeds: Tensor) -> Tensor:
        avg_embeds = embeds.mean(dim=2)  # (B, in_dim)
        y_pred = self.head(avg_embeds)  # (B, num_classes)
        return y_pred

    def compute_loss(
        self,
        outputs: Tensor,
        batch: Dict[str, Any],
    ) -> Dict[str, Tensor]:
        y_true = batch['y']
        loss = self.loss_fn(outputs, y_true)
        loss = loss.mean()  # Average over the batch
        return {"loss": loss}

    # def compute_metrics(self, batch, base):
    #     pass

    def to_config(self) -> Dict[str, Any]:
        return dict(self._cfg)
