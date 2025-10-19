"""
A demo script to show how to create a custom continual learner
"""
from typing import Dict, Any, Optional
from torch import nn, Tensor

from .base import BaseContinualLearner
from ..models.heads import BaseHead


class DemoContinualLearner(BaseContinualLearner):
    """
    A demo continual learner that implements a simple training loop.
    """
    def __init__(
        self,
        base: nn.Module,
        heads: Optional[Dict[str, BaseHead]] = None,
        *,
        custom_param1: Any = None,
        custom_param2: Any = None,
        **kwargs,  # parameters for the base learner
    ):
        super().__init__(base=base, heads=heads, **kwargs)
        self.custom_param1 = custom_param1
        self.custom_param2 = custom_param2

    # ---- Public API ---------------------------------------------------------


    # ---- Lightning hooks ----------------------------------------------------
    def forward(self, x: Tensor, task: str = None, return_embeddings: bool = False):
        return super().forward(x, task, return_embeddings)

    def predict(self, x: Tensor, task: str = None):
        return super().predict(x, task)

    def training_step(self, batch, batch_idx: int):
        return super().training_step(batch, batch_idx)

    def validation_step(self, batch, batch_idx: int):
        return super().validation_step(batch, batch_idx)
