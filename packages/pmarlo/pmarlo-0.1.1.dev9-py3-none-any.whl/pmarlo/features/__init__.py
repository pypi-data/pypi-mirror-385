"""Feature (CV) layer: registry and built-in features.

The module used to eagerly import every deep learning helper, which pulled in
heavy optional dependencies such as PyTorch.  Tests in this kata only need the
balanced sampler utilities, so we expose everything lazily to keep
``import pmarlo.features`` lightweight.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any, Dict, Tuple

from . import builtins as _builtins  # noqa: F401 - ensure feature registration
from .base import FEATURE_REGISTRY, get_feature, register_feature

__all__ = ["FEATURE_REGISTRY", "get_feature", "register_feature"]

_OPTIONAL_EXPORTS: Dict[str, Tuple[str, str]] = {
    "CVModel": ("pmarlo.features.collective_variables", "CVModel"),
    "LaggedPairs": ("pmarlo.features.data_loaders", "LaggedPairs"),
    "make_loaders": ("pmarlo.features.data_loaders", "make_loaders"),
    "DeepTICAConfig": ("pmarlo.features.deeptica", "DeepTICAConfig"),
    "DeepTICAModel": ("pmarlo.features.deeptica", "DeepTICAModel"),
    "train_deeptica": ("pmarlo.features.deeptica", "train_deeptica"),
    "PairDiagItem": ("pmarlo.features.diagnostics", "PairDiagItem"),
    "PairDiagReport": ("pmarlo.features.diagnostics", "PairDiagReport"),
    "diagnose_deeptica_pairs": (
        "pmarlo.features.diagnostics",
        "diagnose_deeptica_pairs",
    ),
    "make_training_pairs_from_shards": (
        "pmarlo.features.pairs",
        "make_training_pairs_from_shards",
    ),
    "scaled_time_pairs": ("pmarlo.features.pairs", "scaled_time_pairs"),
    "RamachandranResult": ("pmarlo.features.ramachandran", "RamachandranResult"),
    "compute_ramachandran": ("pmarlo.features.ramachandran", "compute_ramachandran"),
    "compute_ramachandran_fes": (
        "pmarlo.features.ramachandran",
        "compute_ramachandran_fes",
    ),
    "periodic_hist2d": ("pmarlo.features.ramachandran", "periodic_hist2d"),
}

__all__.extend(sorted(_OPTIONAL_EXPORTS.keys()))


def __getattr__(name: str) -> Any:
    try:
        module_name, attr_name = _OPTIONAL_EXPORTS[name]
    except KeyError:  # pragma: no cover - defensive guard
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(__all__)
