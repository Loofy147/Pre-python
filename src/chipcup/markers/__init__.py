"""PEP 508 marker evaluation over explicit, reproducible audit rows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from packaging.markers import Marker, default_environment

from chipcup.types import AuditReceipt, accepts_protocol

__all__ = [
    "MarkerEvaluation",
    "MarkerMatrixResult",
    "MarkerPolicy",
    "MarkerRow",
    "evaluate_matrix",
]


@dataclass(frozen=True, slots=True)
class MarkerRow:
    name: str
    expression: str
    stub_set: str
    version_specifier: str = ">=0"
    environment: Mapping[str, str] = field(default_factory=dict)
    extra: str | None = None


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
        base = default_environment()
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
