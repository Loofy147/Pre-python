"""Public package surface with deliberate PEP 562 lazy exports."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chipcup.gate import GateRequest, GateReport, evaluate_release
    from chipcup.markers import MarkerPolicy
    from chipcup.versions import VersionPolicy, parse_version

__version__ = "0.1.0"

_EXPORTS: dict[str, tuple[str, str]] = {
    "VersionPolicy": ("chipcup.versions", "VersionPolicy"),
    "parse_version": ("chipcup.versions", "parse_version"),
    "MarkerPolicy": ("chipcup.markers", "MarkerPolicy"),
    "evaluate_release": ("chipcup.gate", "evaluate_release"),
    "GateRequest": ("chipcup.gate", "GateRequest"),
    "GateReport": ("chipcup.gate", "GateReport"),
}

__all__ = [
    "__version__",
    "VersionPolicy",
    "parse_version",
    "MarkerPolicy",
    "evaluate_release",
    "GateRequest",
    "GateReport",
    "legacy_parse_version",
]


def __getattr__(name: str) -> object:
    target = _EXPORTS.get(name)
    if target is not None:
        module = import_module(target[0])
        value = getattr(module, target[1])
        globals()[name] = value
        return value
    if name == "legacy_parse_version":
        from chipcup.deprecations import warn_deprecated

        warn_deprecated(
            name,
            message="legacy_parse_version is deprecated; use parse_version",
            stacklevel=2,
        )
        # Deliberately do not cache this alias: each use must emit a warning.
        return getattr(import_module("chipcup.versions"), "parse_version")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
