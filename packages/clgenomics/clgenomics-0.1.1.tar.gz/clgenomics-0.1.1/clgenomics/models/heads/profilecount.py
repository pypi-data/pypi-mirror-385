from typing import Dict, Any, Tuple, Optional, Type
import torch
import numpy as np
import torch.nn.functional as F
from torch import nn, Tensor

from . import BaseHead, register_head
from ...losses import create_loss
from ...metrics import compute_performance_metrics


@register_head()
class ProfileCountHeads(BaseHead):
    """
    Example of a task that needs two outputs (e.g., regression + classification).
    """
    def __init__(
        self,
        in_dim: int,
        num_classes: int,
        kernel_size: int = 75,
        profile_loss_fn_name: str = "MNLLLoss",
        count_loss_fn_name: str = "log1pMSELoss",
        lambda_count: float = 1.0
    ):
        super().__init__()
        self.profile_head = nn.Conv1d(
            in_channels=in_dim,
            out_channels=num_classes,
            kernel_size=kernel_size,
        )
        self.count_head = nn.Linear(in_dim, 1)
        self.profile_loss_fn_name = profile_loss_fn_name
        self.count_loss_fn_name = count_loss_fn_name
        self.profile_loss_fn = create_loss(profile_loss_fn_name)
        self.count_loss_fn = create_loss(count_loss_fn_name)
        self.lambda_count = lambda_count

        # Config for save/load
        self._cfg = {
            "in_dim": in_dim,
            "num_classes": num_classes,
            "kernel_size": kernel_size,
            "profile_loss_fn_name": profile_loss_fn_name,
            "count_loss_fn_name": count_loss_fn_name,
            "lambda_count": lambda_count,
        }

    @staticmethod
    def log_softmax_over_strands(t: torch.Tensor):
        # log-softmax helper: flatten -> log_softmax -> reshape
        # log-softmax over the both strands, so logsumexp over both strands is 0.
        return F.log_softmax(t.view(t.shape[0], -1), dim=-1).view_as(t)

    def forward(self, embeds: Tensor, **kwargs) -> Tuple[Tensor, Tensor]:
        """
        Parameters
        ----------
        embeds: Tensor of shape (B, in_dim, L_emb)
            L_emb could be longer than L_out due to convolutional kernel size.

        Returns
        -------
        y_profile: Tensor of shape (B, num_classes, L_out)
        y_count: Tensor of shape (B, 1)
        """
        # Profile prediction
        y_profile = self.profile_head(embeds)  # (B, num_classes, L_out)

        # Count prediction
        avg_embeds = embeds.mean(dim=2)  # (B, in_dim)
        y_count = self.count_head(avg_embeds).view(embeds.size(0), 1) # (B, 1)

        return y_profile, y_count

    def predict(self, embeds: Tensor, **kwargs) -> Tuple[Tensor, Tensor]:
        logits, count = self.forward(embeds, **kwargs)
        return self.log_softmax_over_strands(logits), count

    def compute_loss(
        self,
        outputs: Tuple[Tensor, Tensor],
        batch: Dict[str, Any],
    ) -> Dict[str, Tensor]:
        X = batch['x']
        y_true_signal = batch['y']
        mask = batch.get('mask', None)

        batch_size = X.shape[0]

        y_pred_profile_logits, y_pred_count = outputs

        # Profile loss
        if mask is None:
            y_pred_log = self.log_softmax_over_strands(y_pred_profile_logits)  # (B, num_classes, L_out)
            y_pred_flat = y_pred_log.view(batch_size, -1)  # (B, num_classes * L_out)
            y_true_flat = y_true_signal.view(batch_size, -1)
            profile_loss = self.profile_loss_fn(y_pred_flat, y_true_flat).mean()
        else:
            terms = []
            for y_p, y_t, m in zip(y_pred_profile_logits, y_true_signal, mask):
                m = m.bool()  # Ensure mask is boolean
                sel_pred = torch.masked_select(y_p, m).unsqueeze(0)
                sel_pred = self.log_softmax_over_strands(sel_pred)
                sel_true = torch.masked_select(y_t, m).unsqueeze(0)
                terms.append(self.profile_loss_fn(sel_pred, sel_true).mean())
            profile_loss = torch.stack(terms).mean()

        # Count loss
        true_count = y_true_signal.sum(dim=(1, 2)).unsqueeze(1)
        count_loss = self.count_loss_fn(y_pred_count, true_count).mean()

        loss = profile_loss + self.lambda_count * count_loss

        return {'loss': loss, 'profile_loss': profile_loss, 'count_loss': count_loss}

    @torch.no_grad()
    def compute_metrics(self, batch: Dict[str, Any], base: nn.Module) -> Dict[str, Any]:
        X = batch['x']  # (N, 2, L_in)
        y_true_signal = batch['y']

        y_pred_profile_logits, y_pred_count = self.forward_with_base(X, base)

        # Reshape predictions
        y_pred_profile = self.log_softmax_over_strands(y_pred_profile_logits)  # (B, num_classes, L_out)
        y_pred_profile = y_pred_profile.cpu().numpy()  # (N, 2, L_out)
        y_pred_profile = y_pred_profile.reshape(y_pred_profile.shape[0], -1)  # (N, 2*L_out)
        y_pred_profile = np.expand_dims(y_pred_profile, (1, 3))  # (N, 1, 2*L_out, 1)
        y_pred_count = y_pred_count.cpu().numpy()  # (N, 1)
        y_pred_count = np.expand_dims(y_pred_count, 1)  # (N, 1, 1)

        # Reshape true signals
        y_true_signal = y_true_signal.cpu().numpy()  # (N, 2, L_out)
        y_true_signal = y_true_signal.reshape(y_true_signal.shape[0], -1)  # (N, 2*L_out)
        y_true_signal = np.expand_dims(y_true_signal, (1, 3))  # (N, 1, 2*L_out, 1)
        y_true_count = y_true_signal.sum(axis=2)  # (N, 1, 1)

        measures = compute_performance_metrics(
            y_true_signal,
            y_pred_profile,
            y_true_count,
            y_pred_count,
            prof_smooth_kernel_sigma=7,
            prof_smooth_kernel_width=81,
        )
        measures = {k: np.mean(v) for k, v in measures.items()}

        return measures

    def to_config(self) -> Dict[str, Any]:
        return dict(self._cfg)
