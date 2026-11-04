"""Fail-closed release gate coordinating the seven formal-system boundaries."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True, slots=True)
class GateRequest:
    sdist_path: Path
    wheel_path: Path
    audit_receipt: object
    project_root: Path = Path(".")
    module_name: str = "chipcup"
    version_specifier: str = ">=0.1.0,<1.0.0"
    marker: str = 'python_version >= "3.10"'
    extras: tuple[str, ...] = ()
    environment: Mapping[str, str] = field(default_factory=dict)
    license_expression: str = "MIT"
    license_files: tuple[str, ...] = ("LICENSE",)
    license_refs: Mapping[str, str] = field(default_factory=dict)
    deprecations: tuple[object, ...] = ()
    published_releases: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class GateStep:
    boundary: str
    passed: bool
    detail: str


@dataclass(frozen=True, slots=True)
class GateReport:
    passed: bool
    steps: tuple[GateStep, ...]

    @property
    def failed_boundary(self) -> str | None:
        for step in self.steps:
            if not step.passed:
                return step.boundary
        return None


def evaluate_release(request: GateRequest) -> GateReport:
    """Run each policy in order and stop at the first failed boundary."""
    steps: list[GateStep] = []

    def fail(boundary: str, error: Exception) -> GateReport:
        steps.append(GateStep(boundary, False, str(error)))
        return GateReport(False, tuple(steps))

    try:
        from chipcup.imports import load_module, module_identity

        module = load_module(request.module_name)
        identity = module_identity(request.module_name)
        steps.append(GateStep(
            "imports", True,
            f"{identity.name} object={identity.object_id} origin={identity.origin}"
        ))
    except Exception as error:
        return fail("imports", error)

    try:
        from chipcup.versions import VersionPolicy

        version = getattr(module, "__version__")
        policy = VersionPolicy(request.version_specifier)
        if not policy.accepts(version):
            raise ValueError(
                f"package version {version!r} does not satisfy {request.version_specifier!r}"
            )
        steps.append(GateStep("versions", True, f"{version} satisfies {request.version_specifier}"))
    except Exception as error:
        return fail("versions", error)

    try:
        from chipcup.markers import MarkerPolicy

        marker_policy = MarkerPolicy(request.marker, extras=request.extras)
        if not marker_policy.evaluate(request.environment):
            raise ValueError(f"environment does not satisfy marker {request.marker!r}")
        steps.append(GateStep("markers", True, request.marker))
    except Exception as error:
        return fail("markers", error)

    try:
        from chipcup.types import AuditReceipt, prepare_build_receipt

        if not isinstance(request.audit_receipt, AuditReceipt):
            raise TypeError("audit receipt does not satisfy the structural protocol")
        evidence = prepare_build_receipt(request.audit_receipt)
        steps.append(GateStep("types", True, f"accepted source digest {evidence.source_digest}"))
    except Exception as error:
        return fail("types", error)

    try:
        from chipcup.build import compare_artifacts, inspect_artifact

        sdist = inspect_artifact(request.sdist_path)
        wheel = inspect_artifact(request.wheel_path)
        name, artifact_version = compare_artifacts(sdist, wheel)
        if artifact_version != version:
            raise ValueError(
                f"artifact version {artifact_version!r} differs from package version {version!r}"
            )
        steps.append(GateStep(
            "build", True,
            f"{name} {artifact_version}; sdist={sdist.sha256}; wheel={wheel.sha256}"
        ))
    except Exception as error:
        return fail("build", error)

    try:
        from chipcup.build import require_license_coverage
        from chipcup.licenses import validate_compatibility

        for artifact in (sdist, wheel):
            missing = require_license_coverage(artifact, request.license_files)
            if missing:
                raise ValueError(
                    f"{artifact.kind} missing license files: {', '.join(missing)}"
                )
        validate_compatibility(
            request.license_expression,
            {"sdist": sdist.members, "wheel": wheel.members},
            request.license_files,
            root=request.project_root,
            license_refs=request.license_refs,
            deprecations=request.deprecations,
            published_releases=request.published_releases,
        )
        steps.append(GateStep(
            "licenses", True, f"SPDX syntax and file coverage: {request.license_expression}"
        ))
    except Exception as error:
        return fail("licenses", error)

    try:
        from chipcup.deprecations import validate_schedules

        validate_schedules(request.deprecations, request.published_releases)
        steps.append(GateStep(
            "deprecations", True,
            f"validated {len(request.deprecations)} deprecation schedule(s)"
        ))
    except Exception as error:
        return fail("deprecations", error)

    return GateReport(True, tuple(steps))
