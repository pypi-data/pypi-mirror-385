"""Public Bantam API with lazy imports to keep optional deps optional."""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "BantamConfig",
    "BantamModel",
    "BantamForCausalLM",
    "BantamPreTrainedModel",
    "BantamTokenizer",
    "BantamFastTokenizer",
    "TrainingArgs",
    "BantamTrainer",
    "BantamChat",
    "GenerateConfig",
]

_LAZY_IMPORTS = {
    "BantamConfig": (".configuration_bantam", "BantamConfig"),
    "BantamModel": (".modeling_bantam", "BantamModel"),
    "BantamForCausalLM": (".modeling_bantam", "BantamForCausalLM"),
    "BantamPreTrainedModel": (".modeling_bantam", "BantamPreTrainedModel"),
    "BantamTokenizer": (".tokenization_bantam", "BantamTokenizer"),
    "BantamFastTokenizer": (".tokenization_bantam", "BantamFastTokenizer"),
    "TrainingArgs": (".trainer", "TrainingArgs"),
    "BantamTrainer": (".trainer", "BantamTrainer"),
    "BantamChat": (".bantam_chat", "BantamChat"),
    "GenerateConfig": (".bantam_chat", "GenerateConfig"),
}


def __getattr__(name: str) -> Any:
    if name not in _LAZY_IMPORTS:
        raise AttributeError(f"module 'bantam' has no attribute '{name}'")
    module_name, attr = _LAZY_IMPORTS[name]
    module = import_module(module_name, package=__name__)
    value = getattr(module, attr)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + __all__)
