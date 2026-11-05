"""PEP 440 version ordering, specifier matching and matrix-row selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from packaging.specifiers import SpecifierSet
from packaging.version import InvalidVersion, Version

from chipcup._contracts import AuditVerdict, BoundaryReceipt, MatrixRow as MarkerRow, ReceiptState, unavailable

__all__ = [
    "VersionAudit",
    "VersionPolicy",
    "parse_version",
    "degraded_version_receipt",
    "receipt_from_imports",
]


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

def receipt_from_imports(
    import_receipt: BoundaryReceipt | None,
    *,
    version_specifier: str,
    package_name: str,
) -> BoundaryReceipt:
    """Order and constrain the release only after canonical import is verified."""
    if import_receipt is None or import_receipt.state is not ReceiptState.PASS:
        return unavailable(
            "versions", AuditVerdict.VERSION_HISTORY,
            "canonical import receipt is absent or failed",
        )
    try:
        from importlib import import_module
        from importlib.metadata import version as installed_distribution_version

        module = import_module(package_name)
        imported = str(getattr(module, "__version__"))
        installed = installed_distribution_version(package_name)
        result = VersionPolicy(version_specifier).audit_distribution(
            imported, installed, specifier=version_specifier
        )
        return BoundaryReceipt(
            "versions", AuditVerdict.VERSION_HISTORY,
            ReceiptState.PASS if result.passed else ReceiptState.FAIL,
            {
                "imported_version": str(result.imported),
                "installed_version": str(result.installed),
                "order": result.order,
                "specifier": result.specifier,
                "specifier_matches": result.specifier_matches,
            },
            () if result.passed else (
                "imported and installed versions differ or installed version violates the specifier",
            ),
        )
    except Exception as error:
        return BoundaryReceipt(
            "versions", AuditVerdict.VERSION_HISTORY, ReceiptState.FAIL, {},
            (f"version identity could not be verified: {type(error).__name__}: {error}",),
        )


def degraded_version_receipt() -> BoundaryReceipt:
    return unavailable("versions", AuditVerdict.VERSION_HISTORY, "canonical import receipt or release metadata is unavailable")
