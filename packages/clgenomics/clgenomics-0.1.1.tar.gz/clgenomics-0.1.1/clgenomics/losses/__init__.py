from typing import Dict, Callable, Optional, Iterable, Union, Type, Tuple, Any
import torch.nn as nn
import torch.nn.functional as F
import inspect
from torch import Tensor
from functools import partial

LossObj = Union[Callable[..., Any], Type[nn.Module]]
LOSS_REGISTRY: Dict[str, LossObj] = {}


def register_loss(name: Optional[str] = None):
    """
    Decorator to register a loss function or class.

    Parameters
    ----------
    name : str, optional
        Optional name to register under. If not provided, the class or function name is used.

    Returns
    -------
    Callable
        The decorator function that registers the class or function.

    Examples
    --------
    >>> @register_loss()
    ... class MyLoss(nn.Module):
    ...     def forward(self, pred, target):
    ...         return (pred - target).abs().mean()

    >>> @register_loss("my_custom_loss")
    ... def my_loss_fn(pred, target):
    ...     return ((pred - target) ** 2).mean()
    """
    def _wrap(cls):
        key = name or cls.__name__
        LOSS_REGISTRY[key] = cls
        cls._registry_name = key
        return cls
    return _wrap


def register(name: str, obj: LossObj):
    """
    Register a custom loss function or class programmatically.

    Parameters
    ----------
    name : str
        Name to register under.
    obj : LossObj
        Loss function or nn.Module class.

    Examples
    --------
    >>> register("my_loss", my_loss_fn)
    """
    LOSS_REGISTRY[name] = obj
    setattr(obj, "_registry_name", name)


def register_many(items: Iterable[Tuple[str, LossObj]]):
    """
    Bulk register multiple losses at once.

    Parameters
    ----------
    items : iterable of (str, LossObj)
        Iterable of name-object pairs to register.

    Examples
    --------
    >>> register_many([("loss1", loss_fn1), ("loss2", loss_fn2)])
    """
    for n, o in items:
        register(n, o)


def get_loss(name: str) -> LossObj:
    """
    Retrieve a loss object by name.

    This function checks:
      1. User-registered losses in `LOSS_REGISTRY`
      2. Classes in `torch.nn`
      3. Functions in `torch.nn.functional`

    Parameters
    ----------
    name : str
        The name of the loss.

    Returns
    -------
    LossObj
        The corresponding class or function.

    Raises
    ------
    KeyError
        If the loss cannot be found.

    Examples
    --------
    >>> get_loss("MSELoss")   # returns nn.MSELoss class
    >>> get_loss("mse_loss")  # returns torch.nn.functional.mse_loss
    """
    if name in LOSS_REGISTRY:
        return LOSS_REGISTRY[name]

    # --- lazy check nn modules (classes) ---
    if hasattr(nn, name):
        obj = getattr(nn, name)
        if inspect.isclass(obj) and issubclass(obj, nn.modules.loss._Loss):
            LOSS_REGISTRY[name] = obj
            return obj

    # --- lazy check functionals ---
    if hasattr(F, name):
        obj = getattr(F, name)
        if callable(obj):
            LOSS_REGISTRY[name] = obj
            return obj

    raise KeyError(
        f"Loss '{name}' not found. "
        f"Available: torch.nn modules, torch.nn.functional functions, "
        f"and {list(LOSS_REGISTRY.keys())}"
    )


def create_loss(name: str, **kwargs):
    """
    Create an instantiated loss object.

    If the loss is a class (subclass of nn.Module), it is instantiated with the provided kwargs.
    If it is a function, a `functools.partial` is returned with kwargs bound (if any).

    Parameters
    ----------
    name : str
        The name of the loss.
    **kwargs
        Keyword arguments to pass to the loss constructor or bind to the loss function.

    Returns
    -------
    nn.Module or Callable
        Instantiated loss object or partially-applied function.

    Raises
    ------
    TypeError
        If the object is neither a subclass of nn.Module nor a callable.

    Examples
    --------
    >>> loss = create_loss("KLDivLoss", reduction="batchmean")
    >>> isinstance(loss, nn.Module)
    True

    >>> loss_fn = create_loss("mse_loss", reduction="mean")
    >>> loss_fn(torch.randn(3, 5), torch.randn(3, 5)).shape
    torch.Size([])
    """
    obj = get_loss(name)
    if inspect.isclass(obj) and issubclass(obj, nn.Module):
        return obj(**kwargs)
    if callable(obj):
        return partial(obj, **kwargs) if kwargs else obj
    raise TypeError(f"Registered object for '{name}' is neither nn.Module nor callable.")


get_loss_fn = get_loss  # alias
create_loss_fn = create_loss  # alias


# Import built-in losses to trigger registration
from .common import *
from .contrastive import *


__all__ = [
    # Registry API
    "LOSS_REGISTRY",
    "register_loss",
    "register",
    "register_many",
    "get_loss",
    "get_loss_fn",
    "create_loss",
    "create_loss_fn",

    # Built-in losses from common.py

    # Built-in losses from contrastive.py
    "label_aware_dual_MSEloss",
]
