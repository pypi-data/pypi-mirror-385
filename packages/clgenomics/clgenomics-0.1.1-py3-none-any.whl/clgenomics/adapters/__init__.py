ADAPTER_REGISTRY: dict[str, type["BaseAdapter"]] = {}


def register_adapter(name: str | None = None):
    def _wrap(cls):
        key = name or cls.__name__
        ADAPTER_REGISTRY[key] = cls
        cls._registry_name = key  # for export metadata
        return cls
    return _wrap


from .base import BaseAdapter
from .peft import PeftAdapter, get_linear_modules, count_peft_modules

__all__ = [
    "ADAPTER_REGISTRY",
    "register_adapter",
    "BaseAdapter",
    "PeftAdapter",
    "get_linear_modules",
    "count_peft_modules",
]
