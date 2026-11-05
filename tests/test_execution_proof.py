from __future__ import annotations

import ast
import importlib
import json
import subprocess
import sys

import pytest
from pathlib import Path
from typing import cast

from chipcup._contracts import AuditVerdict, BoundaryReceipt, ReceiptState, unavailable
from chipcup.build import measure_notch, validate_notch_profile
from chipcup.runtime import degraded_operation_matrix


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "fixtures" / "chip.dat"
REFERENCE = ROOT / "fixtures" / "golden-profile.json"


def test_teacup_notch_is_load_bearing_and_sets_tolerance():
    profile = PROFILE.read_bytes()
    golden = json.loads(REFERENCE.read_text(encoding="utf-8"))
    measured = measure_notch(profile)
    assert measured["notch_depth_mm"] == 2.4
    assert measured["tolerance_mm"] == 0.12
    assert validate_notch_profile(profile, golden)["passed"] is True


def test_notch_perturbation_uses_derived_tolerance():
    golden = json.loads(REFERENCE.read_text(encoding="utf-8"))
    base = json.loads(PROFILE.read_text(encoding="utf-8"))

    within = json.loads(json.dumps(base))
    within["notch"]["apex"][1] -= 0.05
    assert validate_notch_profile(
        json.dumps(within).encode(), golden
    )["passed"] is True

    outside = json.loads(json.dumps(base))
    outside["notch"]["apex"][1] -= 0.13
    verdict = validate_notch_profile(json.dumps(outside).encode(), golden)
    assert verdict["passed"] is False
    assert verdict["verdict"] == "FIXTURE_GEOMETRY_OUT_OF_TOLERANCE"


def test_each_boundary_has_an_explicit_degraded_verdict():
    from chipcup.build import degraded_build_receipt as build_degraded
    from chipcup.deprecations import degraded_deprecation_receipt as deprecations_degraded
    from chipcup.imports import degraded_import_receipt as imports_degraded
    from chipcup.licenses import degraded_license_receipt as licenses_degraded
    from chipcup.markers import degraded_marker_receipt as markers_degraded
    from chipcup.types import degraded_type_receipt as types_degraded
    from chipcup.versions import degraded_version_receipt as versions_degraded

    actual = {
        "build": build_degraded(),
        "licenses": licenses_degraded(),
        "types": types_degraded(),
        "markers": markers_degraded(),
        "deprecations": deprecations_degraded(),
        "imports": imports_degraded(),
        "versions": versions_degraded(),
    }
    assert set(actual) == set(degraded_operation_matrix())
    for key, receipt in actual.items():
        assert receipt.state is ReceiptState.UNVERIFIED
        assert isinstance(receipt.verdict, AuditVerdict)
        assert receipt.verdict is degraded_operation_matrix()[key]
        assert receipt.to_dict()["verdict"] == receipt.verdict.value


def test_subpackage_public_surfaces_are_disjoint_and_complete():
    packages = (
        "build", "licenses", "types", "markers",
        "deprecations", "imports", "versions",
    )
    owner_by_name: dict[str, str] = {}
    for package in packages:
        module = importlib.import_module(f"chipcup.{package}")
        for name in module.__all__:
            assert name not in owner_by_name, (
                f"public name {name!r} is exported by both "
                f"{owner_by_name.get(name)!r} and {package!r}"
            )
            owner_by_name[name] = package
    assert owner_by_name["BuildEvidence"] == "types"
    assert {
        "VersionAudit", "VersionPolicy", "parse_version",
        "degraded_receipt", "receipt_from_imports",
    }.issubset(set(importlib.import_module("chipcup.versions").__all__))
    assert not hasattr(importlib.import_module("chipcup.build"), "BuildEvidence")


def test_boundary_verdict_vocabulary_is_closed_and_serialization_stable():
    expected = {
        "BUILD_PROVENANCE", "BUILD_RELEASE_IDENTITY", "LICENSE_COVERAGE",
        "TYPE_SURFACE", "MARKER_MATRIX", "DEPRECATION_WINDOW",
        "IMPORT_AUDIT", "VERSION_HISTORY",
        "FIXTURE_GEOMETRY_WITHIN_TOLERANCE",
        "FIXTURE_GEOMETRY_OUT_OF_TOLERANCE",
    }
    assert {item.value for item in AuditVerdict} == expected
    assert isinstance(AuditVerdict.BUILD_PROVENANCE, str)
    with pytest.raises(TypeError, match="verdict must be an AuditVerdict member"):
        BoundaryReceipt(
            "probe", cast(AuditVerdict, "UNREGISTERED"), ReceiptState.FAIL
        )


def test_no_evaluator_imports_another_evaluator():
    packages = {
        "build", "licenses", "types", "markers",
        "deprecations", "imports", "versions",
    }
    source_root = ROOT / "src" / "chipcup"
    for package in packages:
        tree = ast.parse((source_root / package / "__init__.py").read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                parts = node.module.split(".")
                assert not (
                    len(parts) >= 2 and parts[0] == "chipcup"
                    and parts[1] in packages and parts[1] != package
                ), f"{package} imports evaluator {node.module}"
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    parts = alias.name.split(".")
                    assert not (
                        len(parts) >= 2 and parts[0] == "chipcup"
                        and parts[1] in packages and parts[1] != package
                    ), f"{package} imports evaluator {alias.name}"


def test_cli_module_does_not_import_runtime_until_main_entry(tmp_path):
    code = (
        "import sys; import chipcup.cli; "
        "assert 'chipcup.runtime' not in sys.modules; "
        "assert not any(n.startswith('chipcup.build') for n in sys.modules)"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


def test_reducibility_counterexamples_preserve_distinct_failure_modes():
    # Same marker truth, different warning chronology: markers cannot replace deprecations.
    from chipcup.deprecations import DeprecationSchedule, WarningObservation, validate_schedules
    schedule = DeprecationSchedule("old_api", None, ("linux",))
    missing = validate_schedules((schedule,), ("1.0",), ())
    observed = validate_schedules(
        (schedule,), ("1.0",),
        (WarningObservation("1.0", "linux", True, True, 1, "linux"),),
        row_platforms={"linux": "linux"},
    )
    assert not missing.passed and observed.passed

    # Same module identity, different PEP 440 predicate: imports cannot replace versions.
    from chipcup.imports import audit_module
    from chipcup.versions import VersionPolicy
    identity = audit_module("chipcup")
    assert identity.passed
    assert VersionPolicy(">=0").accepts("1.0")
    assert not VersionPolicy(">=2.0").accepts("1.0")

    # Same valid archive inventory, different SPDX declaration: build cannot replace licenses.
    from chipcup.licenses import parse_license_expression
    from chipcup.build import check_artifact_license_coverage
    members = ("x.dist-info/licenses/LICENSE",)
    assert check_artifact_license_coverage(members, ("LICENSE",)) == ()
    assert parse_license_expression("MIT").kind == "id"
    assert parse_license_expression("MIT OR Apache-2.0").kind == "or"


def test_absent_build_is_not_promoted_to_a_pass():
    from chipcup.licenses import receipt_from_build
    receipt = receipt_from_build(None, root=ROOT)
    assert receipt.state is ReceiptState.UNVERIFIED
    assert receipt.verdict == "LICENSE_COVERAGE"


def test_missing_predecessor_receipt_forces_boundary_specific_unverified(tmp_path):
    from chipcup.build import evaluate_artifact_receipt
    from chipcup.deprecations import receipt_from_markers
    from chipcup.imports import receipt_from_deprecations
    from chipcup.licenses import receipt_from_build
    from chipcup.markers import receipt_from_types
    from chipcup.types import receipt_from_license
    from chipcup.versions import receipt_from_imports

    results = {
        "build": evaluate_artifact_receipt(
            sdist_path=tmp_path / "absent.tar.gz",
            wheel_path=tmp_path / "absent.whl",
            project_root=tmp_path,
        ),
        "licenses": receipt_from_build(None, root=tmp_path),
        "types": receipt_from_license(None, root=tmp_path),
        "markers": receipt_from_types(
            None, rows=(), candidate_version="0.1.0"
        ),
        "deprecations": receipt_from_markers(
            None, observations=(), published_releases=(), row_platforms={}
        ),
        "imports": receipt_from_deprecations(None),
        "versions": receipt_from_imports(
            None, version_specifier=">=0", package_name="chipcup"
        ),
    }
    expected = {
        "build": "BUILD_PROVENANCE",
        "licenses": "LICENSE_COVERAGE",
        "types": "TYPE_SURFACE",
        "markers": "MARKER_MATRIX",
        "deprecations": "DEPRECATION_WINDOW",
        "imports": "IMPORT_AUDIT",
        "versions": "VERSION_HISTORY",
    }
    assert set(results) == set(expected)
    for boundary, receipt in results.items():
        assert receipt.state is ReceiptState.UNVERIFIED
        assert receipt.verdict == expected[boundary]


def test_build_without_isolation_attestation_is_unverified(artifact_pair):
    from chipcup.build import evaluate_artifact_receipt

    sdist, wheel = artifact_pair
    receipt = evaluate_artifact_receipt(
        sdist_path=sdist,
        wheel_path=wheel,
        project_root=ROOT,
        build_isolation_verified=False,
    )
    assert receipt.state is ReceiptState.UNVERIFIED
    assert receipt.verdict == "BUILD_PROVENANCE"
    # The degraded result retains artifact manifests for inspection.
    assert receipt.evidence["sdist_members"]
    assert receipt.evidence["wheel_members"]
    assert receipt.evidence["geometry"]["source"]["passed"] is True
