from .base import BaseContinualLearner, ContinualLearner
from .replay import ReplayContinualLearner
from .regularize import EWCContinualLearner, L2ContinualLearner

__all__ = [
    "BaseContinualLearner",
    "ContinualLearner",
    "ReplayContinualLearner",
    "EWCContinualLearner",
    "L2ContinualLearner"
]
