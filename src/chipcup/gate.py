"""Ordered seven-boundary distribution audit with a multi-sorted report."""

from __future__ import annotations

import importlib
from dataclasses import asdict, dataclass, field
from importlib.metadata import version as installed_distribution_version
from pathlib import Path
from typing import Mapping, Sequence

from chipcup.build import (
    ArtifactComparison,
    ArtifactInfo,
    compare_artifacts,
    inspect_artifact,
)
from chipcup.deprecations import (
    DeprecationAuditResult,
    DeprecationSchedule,
    WarningObservation,
    capture_warning_observation,
    validate_schedules,
)
from chipcup.imports import ImportAudit, audit_module
from chipcup.licenses import (
    DEFAULT_LICENSE_REFS,
    LicenseAuditResult,
    validate_compatibility,
)
from chipcup.markers import MarkerMatrixResult, MarkerRow, evaluate_matrix
from chipcup.types import TypeAuditResult, audit_public_surface
from chipcup.versions import VersionAudit, VersionPolicy

__all__ = ["GateReport", "GateRequest", "evaluate_release"]

_DEFAULT_DEPRECATIONS = (
    DeprecationSchedule(
        public_name="legacy_parse_version",
        removal_release=None,
        required_matrix_rows=("linux", "windows", "macos"),
    ),
)


@dataclass(frozen=True, slots=True)
class GateRequest:
    sdist_path: Path
    wheel_path: Path
    project_root: Path = Path(".")
    package_name: str = "chipcup"
    version_specifier: str = ">=0.1.0,<1.0.0"
    marker_rows: tuple[MarkerRow, ...] = ()
    environment: Mapping[str, str] = field(default_factory=dict)
    license_refs: Mapping[str, str] = field(
        default_factory=lambda: dict(DEFAULT_LICENSE_REFS)
    )
    deprecations: tuple[DeprecationSchedule, ...] = _DEFAULT_DEPRECATIONS
    published_releases: tuple[str, ...] = ("0.1.0",)
    warning_observations: tuple[WarningObservation, ...] = ()


@dataclass(frozen=True, slots=True)
class GateReport:
    imports: ImportAudit
    versions: VersionAudit
    markers: MarkerMatrixResult
    types: TypeAuditResult
    build: ArtifactComparison
    licenses: LicenseAuditResult
    deprecations: DeprecationAuditResult
    sdist_sha256: str
    wheel_sha256: str

    @property
    def passed(self) -> bool:
        """Convenience gate, not a replacement for the typed boundary results."""
        return all(
            result.passed
            for result in (
                self.imports,
                self.versions,
                self.markers,
                self.types,
                self.build,
                self.licenses,
                self.deprecations,
            )
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "imports": asdict(self.imports),
            "versions": asdict(self.versions),
            "markers": asdict(self.markers),
            "types": asdict(self.types),
            "build": asdict(self.build),
            "licenses": asdict(self.licenses),
            "deprecations": asdict(self.deprecations),
            "artifacts": {
                "sdist_sha256": self.sdist_sha256,
                "wheel_sha256": self.wheel_sha256,
            },
        }


def _audit_modules(package_name: str) -> Mapping[str, object]:
    names = (
        package_name,
        f"{package_name}.imports",
        f"{package_name}.versions",
        f"{package_name}.markers",
        f"{package_name}.types",
        f"{package_name}.build",
        f"{package_name}.licenses",
        f"{package_name}.deprecations",
    )
    return {name: importlib.import_module(name) for name in names}


def _typed_modules(package_name: str) -> Mapping[str, object]:
    return _audit_modules(package_name)


def _observe_deprecations(
    package_module: object,
    release: str,
    matrix_result: MarkerMatrixResult,
) -> tuple[WarningObservation, ...]:
    observations: list[WarningObservation] = []
    for evaluation in matrix_result.evaluations:
        observations.append(
            capture_warning_observation(
                release,
                evaluation.row,
                evaluation.result,
                lambda: getattr(package_module, "legacy_parse_version"),
            )
        )
    return tuple(observations)


def evaluate_release(request: GateRequest) -> GateReport:
    """Run each formal-system audit and preserve its own result structure."""
    import_result = audit_module(request.package_name)
    package_module = importlib.import_module(request.package_name)

    installed = installed_distribution_version(request.package_name)
    imported = getattr(package_module, "__version__")
    version_policy = VersionPolicy(request.version_specifier)
    version_result = version_policy.audit_distribution(
        str(imported), installed, specifier=request.version_specifier
    )

    selected_rows = version_policy.select_matrix_rows(
        version_result.installed, request.marker_rows
    )
    marker_result = evaluate_matrix(
        selected_rows, environment=request.environment
    )

    # Inspect both artifacts before the type verdict so the typed source API
    # can be compared with the actual wheel export surface.
    sdist = inspect_artifact(request.sdist_path)
    wheel = inspect_artifact(request.wheel_path)

    modules = _typed_modules(request.package_name)
    type_result = audit_public_surface(
        modules, wheel.public_exports, marker_result.selected_stub_sets
    )

    build_result = compare_artifacts(sdist, wheel)

    expression = wheel.license_expression or ""
    license_result = validate_compatibility(
        expression,
        {"sdist": sdist.members, "wheel": wheel.members},
        wheel.license_files,
        root=request.project_root,
        license_refs=request.license_refs,
        deprecations=request.deprecations,
    )

    observations = request.warning_observations or _observe_deprecations(
        package_module, str(version_result.imported), marker_result
    )
    deprecation_result = validate_schedules(
        request.deprecations,
        request.published_releases,
        observations,
    )

    return GateReport(
        imports=import_result,
        versions=version_result,
        markers=marker_result,
        types=type_result,
        build=build_result,
        licenses=license_result,
        deprecations=deprecation_result,
        sdist_sha256=sdist.sha256,
        wheel_sha256=wheel.sha256,
    )
