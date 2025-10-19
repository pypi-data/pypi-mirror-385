from __future__ import annotations
from typing import Any, TYPE_CHECKING
from torch import nn

from . import register_adapter, BaseAdapter
from ..utils import require_pkg


if TYPE_CHECKING:
    # Editor/linter-only imports; no runtime import of optional deps
    import peft
    from peft import PeftConfig


@register_adapter("peft")
class PeftAdapter(nn.Module, BaseAdapter):
    """
    PEFT-based adapter using the `peft` library.
    """

    def __init__(self, base: nn.Module):
        super().__init__()
        require_pkg("peft", "peft")
        import peft

        self.name2cfg: dict[str, dict] = {}
        self.active_adapter: str | None = None
        self._base: nn.Module = base

    @classmethod
    def default_config(cls) -> dict:
        import peft

        return {
            "peft_type": "LORA",
            "task_type": peft.TaskType.FEATURE_EXTRACTION,
            "r": 8,
            "lora_alpha": 16,
            "lora_dropout": 0.05,
            "bias": "none",  # "none", "all", or "lora_only"
            "target_modules": "all-linear",  # doesn't include torch.nn.Conv1d
            # "exclude_modules": ["heads", "head"],
        }

    @property
    def adapter_names(self) -> list[str]:
        return list(self.name2cfg.keys())

    def _build_peft_config(self, cfg: dict | "PeftConfig") -> "PeftConfig":
        from peft import get_peft_config, PeftConfig

        if isinstance(cfg, PeftConfig):
            return cfg
        if "peft_type" not in cfg:
            raise ValueError("cfg must include 'peft_type' (e.g., 'LORA')")
        cfg["peft_type"] = cfg["peft_type"].upper()  # Follow peft convention
        return get_peft_config(cfg)

    def add_adapter(self, adapter_name: str, cfg: dict | "PeftConfig", activate: bool = True):
        """
        Inject PEFT adapter into a base model, returning the modified model.
        Instead of returning a PeftModel wrapper, this modifies the base model in-place.
        """
        from peft import inject_adapter_in_model

        # --- Pre-checks (NO SIDE EFFECTS) ---
        if adapter_name in self.adapter_names:
            raise ValueError(f"Adapter for '{adapter_name}' already exists.")
        if not activate and self.active_adapter is None:
            raise ValueError(
                "PeftAdapter requires active_adapter. Set activate=True for the first adapter."
            )

        # ---- Mutations start here ----
        peft_cfg = self._build_peft_config(cfg)
        inject_adapter_in_model(
            peft_config=peft_cfg,
            model=self._base,
            adapter_name=adapter_name,
        )
        self.name2cfg[adapter_name] = peft_cfg.to_dict()
        if activate:
            self.active_adapter = adapter_name
        else:
            self.activate_adapter(self.active_adapter)

    def delete_adapter(self, adapter_name: str, **kwargs):  # TODO: prefix
        from peft.tuners.tuners_utils import delete_adapter as _delete_adapter

        if adapter_name not in self.adapter_names:
            raise ValueError(f"Adapter for '{adapter_name}' does not exist.")
        prefix = kwargs.pop("prefix", "lora_")
        _delete_adapter(model=self._base, adapter_name=adapter_name, prefix=prefix)
        self.name2cfg.pop(adapter_name)
        if self.active_adapter == adapter_name:
            self.active_adapter = None

    def activate_adapter(self, adapter_name: str):
        """
        Specify which adapter to use for forward passes.
        This also sets requires_grad = True for the adapter parameters.
        """
        from peft.tuners.tuners_utils import set_adapter as _set_adapter

        if adapter_name not in self.adapter_names:
            raise ValueError(f"Adapter for '{adapter_name}' does not exist.")
        _set_adapter(model=self._base, adapter_name=adapter_name, inference_mode=False)
        self.active_adapter = adapter_name

    def freeze_adapter(self, adapter_names: str | list[str]):
        self._set_adapter_trainable(
            model=self._base, adapter_names=adapter_names, requires_grad=False
        )

    def unfreeze_adapter(self, adapter_names: str | list[str]):
        self._set_adapter_trainable(
            model=self._base, adapter_names=adapter_names, requires_grad=True
        )

    def _set_adapter_trainable(
        self, model: nn.Module, adapter_names: str | list[str], requires_grad: bool
    ):
        from peft.tuners.tuners_utils import set_requires_grad as _set_requires_grad

        if isinstance(adapter_names, str):
            adapter_names = [adapter_names]
        if any(name not in self.adapter_names for name in adapter_names):
            missing = [name for name in adapter_names if name not in self.adapter_names]
            raise ValueError(f"Adapter(s) for '{missing}' do not exist.")
        _set_requires_grad(model=model, adapter_names=adapter_names, requires_grad=requires_grad)

    def to_config(self):
        """
        Serializable adapter metadata:
        - 'cls': registry name (for reconstructing the adapter type)
        - 'adapters': {name: peft_config_dict}
        - 'active': active adapter name (for convenience)
        """
        return {
            "cls": getattr(self, "_registry_name", self.__class__.__name__),
            "name2cfg": self.name2cfg,
            "active": self.active_adapter,
        }

    def load_from_meta(self, meta: dict[str, Any]) -> None:
        for name, cfg in meta.get("name2cfg", {}).items():
            self.add_adapter(adapter_name=name, cfg=cfg)
        active_adapter = meta.get("active")
        if active_adapter is not None:
            self.activate_adapter(adapter_name=active_adapter)


# -------------------------------------------------------------------------------------------------
#  Utility functions
# -------------------------------------------------------------------------------------------------


# Adapted from huggingface/peft
# https://github.com/huggingface/peft/blob/8d8aa0b71652b14b63c265f4d1a39e73a4672441/src/peft/tuners/tuners_utils.py#L1669
def get_linear_modules(model: nn.Module, include_conv=True) -> list[str]:
    require_pkg("peft", "peft")
    from peft.tuners.tuners_utils import BaseTunerLayer

    linear_layers = (nn.Linear, nn.Conv1d) if include_conv else (nn.Linear, )  # modified
    linear_names = ("Linear",)
    linear_module_names = set()
    for name, module in model.named_modules():
        # match with all linear classes.
        if isinstance(module, linear_layers):
            if include_conv and isinstance(module, nn.Conv1d):
                if module.groups != 1:  # depthwise conv, skip
                    continue
            linear_module_names.add(name)
        elif isinstance(module, BaseTunerLayer) and any(
            n in type(module).__name__ for n in linear_names
        ):
            # If the model already has adapter layers applied, then the "linear" layer is actually
            # an adapter layer, e.g. lora.Linear, and not nn.Linear. To target this layer, we don't
            # want to check the layer type, as there are many possible layer types (one for each
            # PEFT method) and the list would quickly get out of date. Thus we rely on the name of
            # the layer class, which by convention is something like "Linear", "Linear4bit",
            # "HqqLoraLinear", ... in PEFT. It's not pretty but should generally work.
            # See 2390
            linear_module_names.add(name)
    return list(linear_module_names)


def count_peft_modules(model: nn.Module) -> int:
    require_pkg("peft", "peft")
    from peft.tuners.tuners_utils import BaseTunerLayer

    return sum(1 for m in model.modules() if isinstance(m, BaseTunerLayer))
