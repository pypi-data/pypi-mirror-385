from importlib import metadata

__version__ = metadata.version("clgenomics")

# Ensure metrics (and custom losses) are imported so any registry decorators run
from . import metrics  # noqa: F401

__all__ = [
    "__version__",
    "tutorials",
]
