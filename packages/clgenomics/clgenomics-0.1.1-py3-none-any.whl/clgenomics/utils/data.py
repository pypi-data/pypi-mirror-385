from typing import Optional, Mapping, Sequence, Any, Dict
import torch
from torch import Tensor
from torch.utils.data import Dataset


class DatasetWrapper(Dataset):
    """
    Thin adapter that standardizes dataset samples into a dictionary with keys
    'x' and 'y'. Optionally permutes input arrays/tensors from shape (N, L, 4) to (N, 4, L).

    Parameters
    ----------
    dataset : torch.utils.data.Dataset
        Base dataset to wrap.
    x_key : str, optional
        Key used to extract input features when dataset samples are mappings.
        Defaults to ``"x"``.
    y_key : str, optional
        Key used to extract targets when dataset samples are mappings.
        Defaults to ``"y"``.
    permute_x : bool, default=False
        Whether to permute the input tensor dimensions:
        - ``(L, 4)`` → ``(4, L)``
        - ``(N, L, 4)`` → ``(N, 4, L)``
    permute_y : bool, default=False
        Whether to permute the target tensor dimensions using the same rules.

    Notes
    -----
    - Supports both mapping-style samples (e.g., {"x": ..., "y": ...})
      and sequence-style samples (e.g., (x, y, ...)).
    - Extra fields (beyond "x" and "y") are preserved in the output dict.
    """
    def __init__(
        self,
        dataset,
        x_key: Optional[str] = None,
        y_key: Optional[str] = None,
        permute_x: bool = False,
        permute_y: bool = False,
    ):
        self.dataset = dataset
        self.x_key = x_key or "x"
        self.y_key = y_key or "y"
        self.permute_x = bool(permute_x)
        self.permute_y = bool(permute_y)

    def __len__(self) -> int:
        return len(self.dataset)

    def _to_tensor(self, v: Any) -> Tensor:
        if isinstance(v, Tensor):
            return v
        # as_tensor handles numpy arrays and (nested) lists without copying when possible
        return torch.as_tensor(v)

    def _extract_xy(self, item: Any) -> tuple[Any, Any, Dict[str, Any]]:
        """
        Returns (x, y, rest), where rest are any remaining fields to merge back.
        """
        if isinstance(item, Mapping):
            # shallow copy to avoid mutating the original mapping from the base dataset
            rest = dict(item)
            if self.x_key not in rest:
                raise KeyError(f"Missing key '{self.x_key}' in dataset item.")
            if self.y_key not in rest:
                raise KeyError(f"Missing key '{self.y_key}' in dataset item.")
            x = rest.pop(self.x_key)
            y = rest.pop(self.y_key)
            return x, y, rest

        if isinstance(item, Sequence) and not isinstance(item, (str, bytes, bytearray)):
            if len(item) < 2:
                raise ValueError("Sequence samples must have at least two elements: (x, y, ...).")
            x, y = item[0], item[1]
            # No named extras; pack remaining fields as 'extras' for completeness
            rest = {}
            if len(item) > 2:
                rest["extras"] = item[2:]
            return x, y, rest

        raise TypeError(
            "Dataset item must be a Mapping (e.g., dict) with x/y keys "
            f"or a Sequence (x, y, ...). Got type: {type(item).__name__}"
        )

    def _maybe_permute(self, t: Tensor, flag: bool, name: str) -> Tensor:
        if not flag:
            return t
        if t.ndim == 2:
            return t.transpose(-2, -1).contiguous()
        if t.ndim == 3:
            return t.permute(0, 2, 1).contiguous()
        raise ValueError(f"permute_{name}=True expects {name}.ndim in {{2,3}}; got ndim={t.ndim}")

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        raw = self.dataset[idx]
        x, y, rest = self._extract_xy(raw)

        x = self._to_tensor(x)
        y = self._to_tensor(y)

        x = self._maybe_permute(x, self.permute_x, "x")
        y = self._maybe_permute(y, self.permute_y, "y")

        out = {"x": x, "y": y}
        out.update(rest)
        return out
