# Utility to check for optional dependencies

from importlib.util import find_spec


def require_pkg(pkg: str, extra: str):
    if find_spec(pkg) is None:
        raise ModuleNotFoundError(
            f"Optional dependency '{pkg}' is required for this feature. "
            f"Install with: uv add clgenomics[{extra}]"
            f" or pip install 'clgenomics[{extra}]'"
        )
