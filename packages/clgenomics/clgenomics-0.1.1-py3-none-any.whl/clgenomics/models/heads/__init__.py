from typing import Dict, Type, Optional

HEAD_REGISTRY: Dict[str, Type["BaseHead"]] = {}


def register_head(name: Optional[str] = None):
    def _wrap(cls):
        key = name or cls.__name__
        HEAD_REGISTRY[key] = cls
        cls._registry_name = key  # for export metadata
        return cls

    return _wrap


from .base import BaseHead
from .avgpoollinear import AvgPoolLinearHead
from .profilecount import ProfileCountHeads
from .enformer import EnformerHead
from .borzoi import BorzoiHead

CountHead = AvgPoolLinearHead  # alias
BPNetHead = ProfileCountHeads  # alias

__all__ = [
    "HEAD_REGISTRY",
    "register_head",
    "BaseHead",
    "AvgPoolLinearHead",
    "CountHead",
    "ProfileCountHeads",
    "BPNetHead",
    "EnformerHead",
    "BorzoiHead",
]
