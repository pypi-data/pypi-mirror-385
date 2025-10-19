from typing import Dict, Mapping, Sequence, Any
import torch
from torch import Tensor, nn

from . import BaseHead, register_head
from ...losses import create_loss
from ...metrics import compute_per_channel_pcc


@register_head()
class BorzoiHead(BaseHead):
    """
    A head for the Borzoi model, consisting of a 1x1 convolution followed by a softplus activation.

    Parameters
    ----------
    loss_fn_name : str, optional
        The name of the loss function to use. Default is "poisson_mn".
    in_channels : int, optional
        The number of input channels (features) from the base model. Default is 1920.
    out_channels : int, optional
        The number of output channels (tasks). Default is 7611.
    use_softplus : bool, optional
        Whether to apply a softplus activation after the convolution. Default is True.
    eval_channels : Dict[str, Sequence[int]] or Sequence[int] or None, optional
        Channels to evaluate metrics on. If None, evaluate on all channels and return the mean.
        Default is None.
    """

    def __init__(
        self,
        loss_fn_name: str = "poisson_mn",
        in_channels: int = 1920,
        out_channels: int = 7611,
        use_softplus: bool = True,
        eval_channels: Dict[str, Sequence[int]] | Sequence[int] | None = None,
    ):
        super().__init__()
        self.loss_fn = create_loss(loss_fn_name)
        self.head = nn.Conv1d(in_channels, out_channels, kernel_size=1)
        self.softplus = nn.Softplus() if use_softplus else nn.Identity()
        self.eval_channels = eval_channels  # channels to evaluate metrics on

        # Config for save/load
        self._cfg = {
            "loss_fn_name": loss_fn_name,
            "in_channels": in_channels,
            "out_channels": out_channels,
            "use_softplus": use_softplus,
            "eval_channels": eval_channels,
        }

    def forward(self, embeds: Tensor) -> Tensor:
        return self.softplus(self.head(embeds))

    def compute_loss(self, outputs: Tensor, batch: Dict[str, Any]) -> Dict[str, Tensor]:
        y_true = batch["y"]
        loss = self.loss_fn(outputs, y_true)
        loss = loss.mean()  # Average over the batch
        return {"loss": loss}

    def compute_metrics(self, batch: Dict[str, Any], base: nn.Module) -> Dict[str, Tensor]:
        outputs = self.predict_with_base(batch["x"], base)  # (B, C, L)
        y_true = batch["y"]  # (B, C, L)
        pcc_per_channel = compute_per_channel_pcc(outputs, y_true, channel_dim=1)  # (C,)
        device = pcc_per_channel.device

        metrics = {
            'pearsonr': pcc_per_channel.mean(),  # mean over all channels
        }

        # Case 1: eval_channels is a list -> pearsonr over those indices
        if isinstance(self.eval_channels, Sequence):
            idx = torch.as_tensor(self.eval_channels, device=device, dtype=torch.long)
            metrics["pearsonr_selected"] = torch.index_select(pcc_per_channel, 0, idx).mean()

        # Case 2: eval_channels is a dict -> pearsonr_{group} for each group
        elif isinstance(self.eval_channels, Mapping) and len(self.eval_channels) > 0:
            # per-group
            for group in sorted(self.eval_channels.keys()):
                idx = torch.as_tensor(self.eval_channels[group], device=device, dtype=torch.long)
                metrics[f"pearsonr_{group}"] = torch.index_select(pcc_per_channel, 0, idx).mean()

        return metrics

    def to_config(self) -> Dict[str, Any]:
        return dict(self._cfg)

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
