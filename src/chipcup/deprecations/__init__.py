"""Warning evidence and project-owned removal windows.

This module deliberately does not import chipcup.imports. The CLI entry point
composes the audit in a fresh process and is the cycle-closing boundary.
"""

from __future__ import annotations

import sys
import warnings
from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from packaging.version import Version

from chipcup._contracts import (
    BoundaryReceipt, ReceiptState, WarningObservation, unavailable,
)

__all__ = [
    "DeprecationAuditResult",
    "DeprecationSchedule",
    "WarningObservation",
    "capture_warning_observation",
    "validate_license_dependencies",
    "validate_schedules",
    "warn_deprecated",
]


@dataclass(frozen=True, slots=True)
class DeprecationSchedule:
    public_name: str
    removal_release: str | None
    required_matrix_rows: tuple[str, ...] = ()
    required_license_refs: tuple[str, ...] = ()
    soft: bool = False

    def __post_init__(self) -> None:
        if self.soft and self.removal_release is not None:
            raise ValueError("soft deprecations cannot schedule automatic removal")
        if (
            not self.soft
            and self.removal_release is not None
            and not self.required_matrix_rows
        ):
            raise ValueError("a hard removal schedule must name its required marker rows")


@dataclass(frozen=True, slots=True)
class DeprecationAuditResult:
    effective_warning_releases: Mapping[str, str]
    missing_warning_rows: Mapping[str, tuple[str, ...]]
    issues: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.issues


def warn_deprecated(
    public_name: str,
    *,
    message: str | None = None,
    category: type[Warning] = DeprecationWarning,
    stacklevel: int = 2,
) -> None:
    warnings.warn(
        message or f"{public_name} is deprecated",
        category,
        stacklevel=stacklevel,
    )


def capture_warning_observation(
    release: str,
    matrix_row: str,
    marker_selected: bool,
    invoke: Callable[[], object],
    *,
    platform: str | None = None,
) -> WarningObservation:
    """Record an actual warning only when the marker row selected the API."""
    observed_platform = platform or sys.platform
    if not marker_selected:
        return WarningObservation(release, matrix_row, False, False, 0, observed_platform)
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always", DeprecationWarning)
        invoke()
    count = sum(
        1 for item in recorded if issubclass(item.category, DeprecationWarning)
    )
    return WarningObservation(release, matrix_row, True, count > 0, count, observed_platform)


def validate_license_dependencies(
    schedules: Sequence[DeprecationSchedule],
    resolved_license_refs: Mapping[str, str],
    declared_license_files: Sequence[str],
) -> tuple[str, ...]:
    issues: list[str] = []
    declared = set(declared_license_files)
    for schedule in schedules:
        for reference in schedule.required_license_refs:
            path = resolved_license_refs.get(reference)
            if path is None:
                issues.append(
                    f"{schedule.public_name}: unresolved license reference {reference}"
                )
            elif path not in declared:
                issues.append(
                    f"{schedule.public_name}: {reference} maps to {path}, "
                    "which is not declared as License-File"
                )
    return tuple(issues)


def validate_schedules(
    schedules: Sequence[DeprecationSchedule],
    published_releases: Sequence[str],
    observations: Sequence[WarningObservation],
    *,
    row_platforms: Mapping[str, str] | None = None,
) -> DeprecationAuditResult:
    """Derive starts only from published warning evidence on matching native rows."""
    effective: dict[str, str] = {}
    missing_rows: dict[str, tuple[str, ...]] = {}
    issues: list[str] = []
    published = {Version(item) for item in published_releases}

    for schedule in schedules:
        if schedule.soft:
            continue

        by_row: dict[str, Version] = {}
        for observation in observations:
            if observation.matrix_row not in schedule.required_matrix_rows:
                continue
            release = Version(observation.release)
            if release not in published:
                issues.append(
                    f"{schedule.public_name}: warning evidence refers to "
                    f"unpublished release {observation.release}"
                )
                continue
            if row_platforms is not None and observation.matrix_row not in row_platforms:
                issues.append(
                    f"{schedule.public_name}: row {observation.matrix_row} "
                    "was not selected by the current version matrix"
                )
                continue
            expected_platform = (
                row_platforms.get(observation.matrix_row)
                if row_platforms is not None
                else None
            )
            if expected_platform is not None and observation.platform != expected_platform:
                issues.append(
                    f"{schedule.public_name}: row {observation.matrix_row} "
                    f"requires native platform {expected_platform}, "
                    f"not {observation.platform or 'unspecified'}"
                )
                continue
            if observation.marker_selected and observation.emitted:
                current = by_row.get(observation.matrix_row)
                if current is None or release < current:
                    by_row[observation.matrix_row] = release

        absent = tuple(
            row for row in schedule.required_matrix_rows if row not in by_row
        )
        if absent:
            missing_rows[schedule.public_name] = absent
            issues.append(
                f"{schedule.public_name}: no emitted DeprecationWarning for "
                f"selected marker rows {', '.join(absent)}"
            )
            continue

        # A public API's global clock starts after all required supported rows
        # have actually emitted the warning, not merely after a version shipped.
        start = max(by_row.values())
        effective[schedule.public_name] = str(start)
        if schedule.removal_release is None:
            continue

        removal = Version(schedule.removal_release)
        if removal <= start:
            issues.append(
                f"{schedule.public_name}: removal release must follow "
                "the effective warning release"
            )
            continue

        intervening_minor_releases: set[tuple[int, int]] = set()
        for raw in published_releases:
            release = Version(raw)
            if start < release < removal and len(release.release) >= 2:
                intervening_minor_releases.add(
                    (release.release[0], release.release[1])
                )
        if not intervening_minor_releases:
            issues.append(
                f"{schedule.public_name}: removal requires one published "
                "project minor release after the warning was observed on "
                "all required marker rows"
            )

    return DeprecationAuditResult(effective, missing_rows, tuple(issues))

def receipt_from_markers(
    marker_receipt: BoundaryReceipt | None,
    *,
    observations: Sequence[WarningObservation],
    published_releases: Sequence[str],
    row_platforms: Mapping[str, str],
) -> BoundaryReceipt:
    """Start removal clocks only from selected rows with real warning observations."""
    if marker_receipt is None or marker_receipt.state is not ReceiptState.PASS:
        return unavailable(
            "deprecations", "DEPRECATION_WINDOW",
            "selected marker matrix is absent or unverified",
        )
    selected = tuple(str(item) for item in marker_receipt.evidence.get("selected_rows", []))
    required = tuple(
        row for row in selected
        if row_platforms.get(row) in {"linux", "win32", "darwin"}
    )
    if not required:
        return unavailable(
            "deprecations", "DEPRECATION_WINDOW",
            "no supported native platform row was selected",
        )
    schedule = DeprecationSchedule(
        public_name="legacy_parse_version",
        removal_release=None,
        required_matrix_rows=required,
    )
    result = validate_schedules(
        (schedule,), published_releases, observations,
        row_platforms={row: row_platforms[row] for row in required},
    )
    state = ReceiptState.PASS if result.passed else ReceiptState.FAIL
    return BoundaryReceipt(
        "deprecations", "DEPRECATION_WINDOW", state,
        {
            "required_rows": list(required),
            "effective_warning_releases": dict(result.effective_warning_releases),
            "missing_warning_rows": {
                key: list(value) for key, value in result.missing_warning_rows.items()
            },
        },
        result.issues,
    )


def degraded_receipt() -> BoundaryReceipt:
    return unavailable("deprecations", "DEPRECATION_WINDOW", "selected marker rows or native warning evidence are unavailable")
