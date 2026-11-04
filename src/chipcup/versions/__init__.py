"""PEP 440 version ordering, specifier matching and matrix-row selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from packaging.specifiers import SpecifierSet
from packaging.version import InvalidVersion, Version

from chipcup.markers import MarkerRow

__all__ = ["VersionAudit", "VersionPolicy", "parse_version"]


@dataclass(frozen=True, slots=True)
class VersionAudit:
    imported: Version
    installed: Version
    order: int
    specifier: str
    specifier_matches: bool

    @property
    def metadata_matches_import(self) -> bool:
        return self.order == 0

    @property
    def passed(self) -> bool:
        return self.metadata_matches_import and self.specifier_matches


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

    def select_matrix_rows(
        self, candidate: str | Version, rows: Sequence[MarkerRow]
    ) -> tuple[MarkerRow, ...]:
        """A release specifier determines which marker rows are in scope."""
        return tuple(
            row
            for row in rows
            if SpecifierSet(row.version_specifier).contains(candidate)
        )

    def audit_distribution(
        self,
        imported_version: str,
        installed_version: str,
        *,
        specifier: str | None = None,
    ) -> VersionAudit:
        imported = Version(imported_version)
        installed = Version(installed_version)
        relation = 0 if imported == installed else (-1 if imported < installed else 1)
        accepted = VersionPolicy(specifier or self.specifier).accepts(installed)
        return VersionAudit(imported, installed, relation, specifier or self.specifier, accepted)
