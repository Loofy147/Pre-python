"""Public package surface with PEP 562 lazy exports."""

from __future__ import annotations

from importlib import import_module
from typing import Any

__version__ = "0.1.0"

_EXPORTS: dict[str, tuple[str, str]] = {
    "VersionPolicy": ("chipcup.versions", "VersionPolicy"),
    "parse_version": ("chipcup.versions", "parse_version"),
    "MarkerPolicy": ("chipcup.markers", "MarkerPolicy"),
    "evaluate_release": ("chipcup.gate", "evaluate_release"),
    "GateRequest": ("chipcup.gate", "GateRequest"),
}

__all__ = ["__version__", *_EXPORTS, "legacy_parse_version"]


def __getattr__(name: str) -> Any:
    target = _EXPORTS.get(name)
    if target is not None:
        module = import_module(target[0])
        value = getattr(module, target[1])
        globals()[name] = value
        return value
    if name == "legacy_parse_version":
        from chipcup.deprecations import resolve_shim

        value = resolve_shim(
            name,
            "chipcup.versions",
            "parse_version",
            message="legacy_parse_version is deprecated; use parse_version",
        )
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
