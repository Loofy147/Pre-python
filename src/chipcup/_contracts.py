"""Shared, evaluator-neutral contracts for the seven audit boundaries.

This module deliberately imports no chipcup evaluator. Receipts carry facts
between boundaries without creating Python import edges between them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Protocol, runtime_checkable


class AuditVerdict(str, Enum):
    """Closed vocabulary for every named boundary and fixture verdict."""

    BUILD_PROVENANCE = "BUILD_PROVENANCE"
    BUILD_RELEASE_IDENTITY = "BUILD_RELEASE_IDENTITY"
    LICENSE_COVERAGE = "LICENSE_COVERAGE"
    TYPE_SURFACE = "TYPE_SURFACE"
    MARKER_MATRIX = "MARKER_MATRIX"
    DEPRECATION_WINDOW = "DEPRECATION_WINDOW"
    IMPORT_AUDIT = "IMPORT_AUDIT"
    VERSION_HISTORY = "VERSION_HISTORY"
    FIXTURE_GEOMETRY_WITHIN_TOLERANCE = "FIXTURE_GEOMETRY_WITHIN_TOLERANCE"
    FIXTURE_GEOMETRY_OUT_OF_TOLERANCE = "FIXTURE_GEOMETRY_OUT_OF_TOLERANCE"


class ReceiptState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNVERIFIED = "UNVERIFIED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True, slots=True)
class BoundaryReceipt:
    boundary: str
    verdict: AuditVerdict
    state: ReceiptState
    evidence: Mapping[str, object] = field(default_factory=dict)
    issues: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.verdict, AuditVerdict):
            raise TypeError("verdict must be an AuditVerdict member")

    @property
    def passed(self) -> bool:
        return self.state in {ReceiptState.PASS, ReceiptState.NOT_APPLICABLE}

    def to_dict(self) -> dict[str, object]:
        return {
            "boundary": self.boundary,
            "verdict": self.verdict.value,
            "state": self.state.value,
            "evidence": dict(self.evidence),
            "issues": list(self.issues),
        }


def unavailable(boundary: str, verdict: AuditVerdict, reason: str) -> BoundaryReceipt:
    return BoundaryReceipt(
        boundary=boundary,
        verdict=verdict,
        state=ReceiptState.UNVERIFIED,
        issues=(reason,),
    )


@runtime_checkable
class AuditReceipt(Protocol):
    @property
    def source_digest(self) -> str: ...

    @property
    def passed(self) -> bool: ...


@dataclass(frozen=True, slots=True)
class BuildEvidence:
    source_digest: str
    passed: bool
    receipt_kind: str = "typing-audit"


@dataclass(frozen=True, slots=True)
class MatrixRow:
    name: str
    expression: str
    stub_set: str
    version_specifier: str = ">=0"
    environment: Mapping[str, str] = field(default_factory=dict)
    extra: str | None = None

@dataclass(frozen=True, slots=True)
class WarningObservation:
    release: str
    matrix_row: str
    marker_selected: bool
    emitted: bool
    warning_count: int
    platform: str = ""
