"""PEP 508 marker evaluation over explicit, reproducible audit rows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence, cast

from packaging.markers import Marker, default_environment
from packaging.specifiers import SpecifierSet
from packaging.version import InvalidVersion, Version

from chipcup._contracts import (
    AuditReceipt, BoundaryReceipt, MatrixRow as MarkerRow,
    ReceiptState, unavailable,
)

__all__ = [
    "MarkerEvaluation",
    "MarkerMatrixResult",
    "MarkerPolicy",
    "MarkerRow",
    "evaluate_matrix",
    "degraded_receipt",
    "receipt_from_types",
]


@dataclass(frozen=True, slots=True)
class MarkerEvaluation:
    row: str
    expression: str
    result: bool
    stub_set: str
    log_line: str


@dataclass(frozen=True, slots=True)
class MarkerMatrixResult:
    evaluations: tuple[MarkerEvaluation, ...]

    @property
    def selected_rows(self) -> tuple[str, ...]:
        return tuple(item.row for item in self.evaluations if item.result)

    @property
    def selected_stub_sets(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(
            item.stub_set for item in self.evaluations if item.result
        ))

    @property
    def passed(self) -> bool:
        return bool(self.evaluations) and bool(self.selected_stub_sets)


@dataclass(frozen=True, slots=True)
class MarkerPolicy:
    expression: str
    extras: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        Marker(self.expression)

    def evaluate(self, environment: Mapping[str, str] | None = None) -> bool:
        base: dict[str, str] = dict(cast(Mapping[str, str], default_environment()))
        if environment:
            base.update(environment)
        selected_extras = self.extras or ("",)
        marker = Marker(self.expression)
        return any(
            marker.evaluate({**base, "extra": extra})
            for extra in selected_extras
        )

    def admits(
        self,
        candidate: object,
        protocol: type[object] = AuditReceipt,
        environment: Mapping[str, str] | None = None,
    ) -> bool:
        return self.evaluate(environment) and accepts_protocol(candidate, protocol)


def accepts_protocol(candidate: object, protocol: type[object]) -> bool:
    try:
        return isinstance(candidate, protocol)
    except TypeError:
        return False


def evaluate_matrix(
    rows: Sequence[MarkerRow],
    *,
    environment: Mapping[str, str] | None = None,
) -> MarkerMatrixResult:
    evaluations: list[MarkerEvaluation] = []
    for row in rows:
        merged = dict(row.environment)
        if environment:
            merged.update(environment)
        extras = (row.extra,) if row.extra is not None else ()
        result = MarkerPolicy(row.expression, extras=extras).evaluate(merged)
        log_line = f"marker-eval row={row.name} result={result}"
        evaluations.append(
            MarkerEvaluation(row.name, row.expression, result, row.stub_set, log_line)
        )
    return MarkerMatrixResult(tuple(evaluations))

def receipt_from_types(
    type_receipt: BoundaryReceipt | None,
    *,
    rows: Sequence[MarkerRow],
    candidate_version: str,
) -> BoundaryReceipt:
    """Select only marker rows permitted by PEP 440 and typed contracts."""
    if type_receipt is None or type_receipt.state is not ReceiptState.PASS:
        return unavailable(
            "markers", "MARKER_MATRIX",
            "verified type-contract receipt is absent",
        )
    try:
        version = Version(candidate_version)
        raw_sets = type_receipt.evidence.get("contract_sets")
        if not isinstance(raw_sets, dict):
            raise ValueError("type receipt has no contract-set manifest")
        available_sets = set(str(name) for name in raw_sets)
        in_scope = tuple(
            row for row in rows
            if SpecifierSet(row.version_specifier).contains(version)
        )
        result = evaluate_matrix(in_scope)
        unknown = tuple(
            row.stub_set for row in in_scope if row.stub_set not in available_sets
        )
        if unknown:
            return BoundaryReceipt(
                "markers", "MARKER_MATRIX", ReceiptState.FAIL,
                {"evaluations": [item.log_line for item in result.evaluations]},
                ("marker rows selected unknown type contract sets: " + ", ".join(unknown),),
            )
        if not result.selected_rows:
            return BoundaryReceipt(
                "markers", "MARKER_MATRIX", ReceiptState.UNVERIFIED,
                {"evaluations": [item.log_line for item in result.evaluations]},
                ("no marker row was selected; platform coverage is unverified",),
            )
        return BoundaryReceipt(
            "markers", "MARKER_MATRIX", ReceiptState.PASS,
            {
                "selected_rows": list(result.selected_rows),
                "selected_stub_sets": list(result.selected_stub_sets),
                "evaluations": [item.log_line for item in result.evaluations],
                "row_platforms": {
                    row.name: str(row.environment.get("sys_platform", ""))
                    for row in in_scope
                },
            },
        )
    except (InvalidVersion, ValueError, TypeError, KeyError) as error:
        return BoundaryReceipt(
            "markers", "MARKER_MATRIX", ReceiptState.FAIL, {},
            (f"marker matrix cannot be evaluated: {type(error).__name__}: {error}",),
        )


def degraded_receipt() -> BoundaryReceipt:
    return unavailable("markers", "MARKER_MATRIX", "typed stub contract receipt is unavailable")
