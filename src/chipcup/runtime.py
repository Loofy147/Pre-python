"""Receipt-cycle orchestrator.

Importing this module does not import any evaluator. Evaluators are imported
inside run_receipt_cycle, after the console entry point has entered main().
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping, Sequence


def run_receipt_cycle(
    *,
    sdist_path: str | Path,
    wheel_path: str | Path,
    project_root: str | Path,
    marker_rows: Sequence[object],
    warning_observations: Sequence[object],
    version_specifier: str = ">=0.1.0,<1.0.0",
    published_releases: Sequence[str] = ("0.1.0",),
    build_isolation_verified: bool = True,
) -> dict[str, object]:
    """Run build→licenses→types→markers→deprecations→imports→versions→build."""
    from chipcup.build import close_version_cycle, evaluate_artifact_receipt
    from chipcup.deprecations import receipt_from_markers
    from chipcup.imports import receipt_from_deprecations
    from chipcup.licenses import receipt_from_build
    from chipcup.markers import receipt_from_types
    from chipcup.types import receipt_from_license
    from chipcup.versions import receipt_from_imports

    root = Path(project_root)
    build = evaluate_artifact_receipt(
        sdist_path=Path(sdist_path),
        wheel_path=Path(wheel_path),
        project_root=root,
        build_isolation_verified=build_isolation_verified,
    )
    licenses = receipt_from_build(build, root=root)
    types = receipt_from_license(licenses, root=root)
    markers = receipt_from_types(
        types,
        rows=marker_rows,
        candidate_version=str(build.evidence.get("version", "")),
    )
    platform_rows = {
        getattr(row, "name", ""): str(
            getattr(row, "environment", {}).get("sys_platform", "")
        )
        for row in marker_rows
    }
    deprecations = receipt_from_markers(
        markers,
        observations=warning_observations,
        published_releases=published_releases,
        row_platforms=platform_rows,
    )
    imports = receipt_from_deprecations(deprecations, module_name="chipcup")
    versions = receipt_from_imports(
        imports, version_specifier=version_specifier, package_name="chipcup"
    )
    build_closed = close_version_cycle(build, versions)

    receipts = {
        "build": build.to_dict(),
        "licenses": licenses.to_dict(),
        "types": types.to_dict(),
        "markers": markers.to_dict(),
        "deprecations": deprecations.to_dict(),
        "imports": imports.to_dict(),
        "versions": versions.to_dict(),
        "build_cycle_closure": build_closed.to_dict(),
    }
    states = [
        item["state"]
        for item in (
            receipts["build"],
            receipts["licenses"],
            receipts["types"],
            receipts["markers"],
            receipts["deprecations"],
            receipts["imports"],
            receipts["versions"],
            receipts["build_cycle_closure"],
        )
    ]
    return {
        "dependency_order": [
            "build", "licenses", "types", "markers",
            "deprecations", "imports", "versions", "build",
        ],
        "passed": all(state in {"PASS", "NOT_APPLICABLE"} for state in states),
        "receipts": receipts,
    }


def degraded_operation_matrix() -> Mapping[str, str]:
    """CI-visible names for the seven absence verdicts."""
    return {
        "build": "BUILD_PROVENANCE",
        "licenses": "LICENSE_COVERAGE",
        "types": "TYPE_SURFACE",
        "markers": "MARKER_MATRIX",
        "deprecations": "DEPRECATION_WINDOW",
        "imports": "IMPORT_AUDIT",
        "versions": "VERSION_HISTORY",
    }
