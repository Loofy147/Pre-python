"""Shared, evaluator-neutral contracts for the seven audit boundaries.

This module deliberately imports no chipcup evaluator. Receipts carry facts
between boundaries without creating Python import edges between them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Protocol, runtime_checkable


class ReceiptState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNVERIFIED = "UNVERIFIED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True, slots=True)
class BoundaryReceipt:
    boundary: str
    verdict: str
    state: ReceiptState
    evidence: Mapping[str, object] = field(default_factory=dict)
    issues: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return self.state in {ReceiptState.PASS, ReceiptState.NOT_APPLICABLE}

    def to_dict(self) -> dict[str, object]:
        return {
            "boundary": self.boundary,
            "verdict": self.verdict,
            "state": self.state.value,
            "evidence": dict(self.evidence),
            "issues": list(self.issues),
        }


def unavailable(boundary: str, verdict: str, reason: str) -> BoundaryReceipt:
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
