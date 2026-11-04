"""PEP 387 warning windows, soft deprecations and lazy compatibility shims."""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Iterable, Sequence

from packaging.version import Version


@dataclass(frozen=True, slots=True)
class DeprecationSchedule:
    public_name: str
    first_warning_release: str
    removal_release: str | None = None
    soft: bool = False

    def validate(self, published_releases: Iterable[str]) -> None:
        if self.soft:
            if self.removal_release is not None:
                raise ValueError("soft deprecations cannot have an automatic removal release")
            return
        if self.removal_release is None:
            return
        first = Version(self.first_warning_release)
        removal = Version(self.removal_release)
        if removal <= first:
            raise ValueError("removal release must follow the first warning release")
        intervening: set[tuple[int, int]] = set()
        for raw in published_releases:
            release = Version(raw)
            if first < release < removal and len(release.release) >= 2:
                intervening.add((release.release[0], release.release[1]))
        if len(intervening) < 2:
            raise ValueError(
                "regular deprecation requires two distinct published minor releases "
                "between warning and removal"
            )


def validate_schedules(
    schedules: Sequence[object], published_releases: Sequence[str]
) -> None:
    for schedule in schedules:
        if not isinstance(schedule, DeprecationSchedule):
            raise TypeError("deprecation entries must be DeprecationSchedule values")
        schedule.validate(published_releases)


def warn_deprecated(
    public_name: str,
    *,
    message: str | None = None,
    category: type[Warning] = DeprecationWarning,
    stacklevel: int = 2,
) -> None:
    warnings.warn(message or f"{public_name} is deprecated", category, stacklevel=stacklevel)


def resolve_shim(
    old_name: str,
    target_module: str,
    target_symbol: str,
    *,
    message: str | None = None,
) -> object:
    """Warn, then delegate canonical resolution to the import boundary."""
    warn_deprecated(old_name, message=message, stacklevel=3)
    from chipcup.imports import load_module

    module = load_module(target_module)
    try:
        return getattr(module, target_symbol)
    except AttributeError as error:
        raise AttributeError(
            f"compatibility target {target_module}.{target_symbol} is unavailable"
        ) from error
