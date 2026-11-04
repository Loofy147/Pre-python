"""PEP 508 marker logic evaluated against explicit environments and extras."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Type

from packaging.markers import Marker, default_environment


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
        return any(marker.evaluate({**base, "extra": extra}) for extra in selected_extras)

    def admits(
        self,
        candidate: object,
        protocol: Type[object],
        environment: Mapping[str, str] | None = None,
    ) -> bool:
        if not self.evaluate(environment):
            return False
        from chipcup.types import accepts_protocol

        return accepts_protocol(candidate, protocol)
