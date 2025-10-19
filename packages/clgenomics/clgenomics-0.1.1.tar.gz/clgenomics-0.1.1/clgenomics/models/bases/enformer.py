from __future__ import annotations
from torch import nn
from typing import TYPE_CHECKING
from ...utils import require_pkg

if TYPE_CHECKING:
    # Editor/linter-only imports; no runtime import of optional deps
    from enformer_pytorch import Enformer as _Enformer


class Enformer(nn.Module):
    """
    Enformer model from https://github.com/lucidrains/enformer-pytorch

    Parameters
    ----------
    **kwargs
        Keyword arguments passed to  `Enformer.from_pretrained` function.

    Returns
    -------
    torch.nn.Module
        Instantiated Enformer model.
    """

    def __init__(self, **kwargs):
        super().__init__()

        require_pkg("enformer_pytorch", "enformer")
        from enformer_pytorch import from_pretrained

        # Load the pretrained model
        self.model = from_pretrained("EleutherAI/enformer-official-rough", **kwargs)

    def forward(self, x, **kwargs):
        return self.model(x, **kwargs)


class EnformerBase(nn.Module):
    def __init__(self, model: _Enformer):
        super().__init__()
        self.model = model

    def forward(self, x):
        """Returns embeddings from the enformer model - pytorch implementation"""
        embeddings = self.model(x, return_only_embeddings=True)
        return embeddings
