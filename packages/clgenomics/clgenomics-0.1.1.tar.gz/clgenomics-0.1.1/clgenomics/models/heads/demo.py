from typing import Dict, Any
from torch import Tensor

from . import BaseHead, register_head
from ...losses import create_loss


@register_head()
class DemoHead(BaseHead):
    def __init__(
        self,
        loss_fn_name: str,
        custom_param1: Any = None,
        custom_param2: Any = None,
    ):
        super().__init__()
        self.head = None  # Define your head layers here
        self.loss_fn = create_loss(loss_fn_name)

        # Config for save/load
        self._cfg = {
            "loss_fn_name": loss_fn_name,
            "custom_param1": custom_param1,
            "custom_param2": custom_param2,
        }

    def forward(self, embeds: Tensor) -> Tensor:
        # Define your forward pass here from embeddings to predictions
        return self.head(embeds)

    def compute_loss(
        self,
        outputs: Tensor,
        batch: Dict[str, Any],
    ) -> Dict[str, Tensor]:
        y_true = batch['y']
        loss = self.loss_fn(outputs, y_true)
        loss = loss.mean()  # Average over the batch
        return {"loss": loss}

    def compute_metrics(self, batch, base):
        # override if you want to compute extra metrics during training/validation
        pass

    def to_config(self) -> Dict[str, Any]:
        return dict(self._cfg)
