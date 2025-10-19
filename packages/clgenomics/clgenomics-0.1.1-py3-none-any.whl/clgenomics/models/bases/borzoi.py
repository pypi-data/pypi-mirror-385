from __future__ import annotations
from torch import nn
from typing import TYPE_CHECKING
from ...utils import require_pkg


if TYPE_CHECKING:
    # Editor/linter-only imports; no runtime import of optional deps
    from borzoi_pytorch import Borzoi as _Borzoi


class Borzoi(nn.Module):
    """
    Simple wrapper for Borzoi model.
    The Pytorch implementation of Borzoi model is from https://github.com/johahi/borzoi-pytorch
    """

    def __init__(self, pretrained: bool = True, use_flashzoi: bool = False):
        super().__init__()

        require_pkg("borzoi_pytorch", "borzoi")
        from borzoi_pytorch import Borzoi as RawBorzoi  # rename to avoid confusion
        from borzoi_pytorch.config_borzoi import BorzoiConfig

        if pretrained:
            if use_flashzoi:  # use flashzoi
                borzoi = RawBorzoi.from_pretrained("johahi/flashzoi-replicate-0")
            else:  # use original borzoi
                borzoi = RawBorzoi.from_pretrained("johahi/borzoi-replicate-0")
        else:
            cfg = BorzoiConfig(enable_mouse_head=True)
            if use_flashzoi:
                cfg.flashed = True
            borzoi = RawBorzoi(cfg)

        self.model = borzoi

    def forward(self, x, **kwargs):
        return self.model(x, **kwargs)


class BorzoiBase(nn.Module):
    """
    Extracts the base component of Borzoi, returning embeddings.
    Removes heads and final softplus.
    """

    def __init__(self, model: _Borzoi):
        super().__init__()
        for submodule in ["human_head", "mouse_head", "final_softplus"]:
            if submodule in model._modules:
                del model._modules[submodule]
        self.model = model

    def forward(self, x):
        """Returns embeddings from Borzoi"""
        x = self.model.get_embs_after_crop(x)
        x = self.model.final_joined_convs(x)
        return x
