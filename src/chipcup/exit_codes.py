"""Stable process exit codes for the seven-boundary audit.

Receipt states remain the authoritative per-boundary result. This module maps
those multi-sorted results to one deterministic process status without
collapsing or rewriting the JSON evidence.
"""
from __future__ import annotations

from enum import IntEnum
from typing import Mapping


class ExitCode(IntEnum):
    """Public, stable command-line exit-code contract."""

    OK = 0
    AUDIT_ERROR = 1
    DEPRECATION_UNPROVEN = 2
    LICENSE_UNRESOLVED = 3
    FIXTURE_GEOMETRY = 4
    TYPE_SURFACE_INVALID = 5
    BUILD_DIVERGENT = 6
    BUILD_UNAVAILABLE = 7
    MARKER_MATRIX_INVALID = 8
    IMPORT_AUDIT_FAILED = 9
    VERSION_MISMATCH = 10
    BUILD_RELEASE_IDENTITY = 11
    MODULE_NOT_FOUND = 12
    AUDIT_UNVERIFIED = 13


# Lower entries are less severe. Later entries win when multiple fatal
# conditions coexist. This order is intentionally independent of numeric
# exit-code order and is part of the public contract.
EXIT_PRECEDENCE: tuple[ExitCode, ...] = (
    ExitCode.AUDIT_ERROR,
    ExitCode.AUDIT_UNVERIFIED,
    ExitCode.DEPRECATION_UNPROVEN,
    ExitCode.TYPE_SURFACE_INVALID,
    ExitCode.MARKER_MATRIX_INVALID,
    ExitCode.IMPORT_AUDIT_FAILED,
    ExitCode.VERSION_MISMATCH,
    ExitCode.BUILD_RELEASE_IDENTITY,
    ExitCode.BUILD_DIVERGENT,
    ExitCode.LICENSE_UNRESOLVED,
    ExitCode.FIXTURE_GEOMETRY,
    ExitCode.BUILD_UNAVAILABLE,
)

_REQUIRED_RECEIPTS = (
    "build",
    "licenses",
    "types",
    "markers",
    "deprecations",
    "imports",
    "versions",
    "build_cycle_closure",
)

_BOUNDARY_FAILURES = {
    "licenses": ExitCode.LICENSE_UNRESOLVED,
    "types": ExitCode.TYPE_SURFACE_INVALID,
    "markers": ExitCode.MARKER_MATRIX_INVALID,
    "deprecations": ExitCode.DEPRECATION_UNPROVEN,
    "imports": ExitCode.IMPORT_AUDIT_FAILED,
    "versions": ExitCode.VERSION_MISMATCH,
    "build_cycle_closure": ExitCode.BUILD_RELEASE_IDENTITY,
}


def _fixture_failed(receipt: Mapping[str, object]) -> bool:
    evidence = receipt.get("evidence")
    if isinstance(evidence, Mapping):
        geometry = evidence.get("geometry")
        if isinstance(geometry, Mapping):
            return any(
                not isinstance(result, Mapping) or result.get("passed") is not True
                for result in geometry.values()
            )
    issues = receipt.get("issues", ())
    if isinstance(issues, (list, tuple)):
        message = " ".join(str(item) for item in issues).lower()
        return any(
            marker in message
            for marker in ("fixture", "notch", "golden-profile", "golden profile")
        )
    return False


def _receipt_exit_code(
    boundary: str, receipt: Mapping[str, object]
) -> ExitCode | None:
    state = receipt.get("state")
    if state == "PASS" or state == "NOT_APPLICABLE":
        return None
    if state == "UNVERIFIED":
        return (
            ExitCode.BUILD_UNAVAILABLE
            if boundary == "build"
            else ExitCode.AUDIT_UNVERIFIED
        )
    if state != "FAIL":
        return ExitCode.AUDIT_ERROR
    if boundary == "build":
        return (
            ExitCode.FIXTURE_GEOMETRY
            if _fixture_failed(receipt)
            else ExitCode.BUILD_DIVERGENT
        )
    return _BOUNDARY_FAILURES.get(boundary, ExitCode.AUDIT_ERROR)


def select_exit_code(report: Mapping[str, object]) -> ExitCode:
    """Select the deterministic process code from a complete receipt report.

    Every required receipt must be present. PASS and NOT_APPLICABLE are
    successful; FAIL and UNVERIFIED are non-zero. A skipped/missing receipt
    is never treated as success.
    """
    raw_receipts = report.get("receipts")
    if not isinstance(raw_receipts, Mapping):
        return ExitCode.AUDIT_ERROR

    failures: set[ExitCode] = set()
    for boundary in _REQUIRED_RECEIPTS:
        raw_receipt = raw_receipts.get(boundary)
        if not isinstance(raw_receipt, Mapping):
            failures.add(ExitCode.AUDIT_UNVERIFIED)
            continue
        code = _receipt_exit_code(boundary, raw_receipt)
        if code is not None:
            failures.add(code)

    if not failures and report.get("passed") is True:
        return ExitCode.OK
    if not failures:
        return ExitCode.AUDIT_ERROR
    return next(code for code in reversed(EXIT_PRECEDENCE) if code in failures)


__all__ = ["ExitCode", "EXIT_PRECEDENCE", "select_exit_code"]
