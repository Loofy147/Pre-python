"""PEP 440 version parsing, total ordering and specifier satisfaction."""

from __future__ import annotations

from dataclasses import dataclass

from packaging.specifiers import SpecifierSet
from packaging.version import InvalidVersion, Version


def parse_version(value: str) -> Version:
    return Version(value)


@dataclass(frozen=True, slots=True)
class VersionPolicy:
    specifier: str

    def __post_init__(self) -> None:
        SpecifierSet(self.specifier)

    def accepts(
        self,
        candidate: str | Version,
        *,
        prereleases: bool | None = None,
    ) -> bool:
        try:
            version = candidate if isinstance(candidate, Version) else Version(candidate)
        except InvalidVersion:
            return False
        return SpecifierSet(self.specifier).contains(version, prereleases=prereleases)

    def accepts_for(
        self,
        candidate: str | Version,
        marker: str,
        *,
        extras: tuple[str, ...] = (),
        environment: dict[str, str] | None = None,
        prereleases: bool | None = None,
    ) -> bool:
        if not self.accepts(candidate, prereleases=prereleases):
            return False
        from chipcup.markers import MarkerPolicy

        return MarkerPolicy(marker, extras=extras).evaluate(environment)
