from pathlib import Path

from chipcup.deprecations import WarningObservation
from chipcup.gate import GateRequest, evaluate_release


def test_release_gate_reports_seven_independent_results(artifact_pair):
    sdist, wheel = artifact_pair
    root = Path(__file__).resolve().parents[1]

    observations = tuple(
        WarningObservation("0.1.0", row, True, True, 1)
        for row in ("linux", "windows", "macos")
    )
    report = evaluate_release(
        GateRequest(
            sdist_path=sdist,
            wheel_path=wheel,
            project_root=root,
            warning_observations=observations,
        )
    )

    assert report.passed
    assert report.imports.passed
    assert report.versions.passed
    assert report.markers.passed
    assert report.types.passed
    assert report.build.passed
    assert report.licenses.passed
    assert report.deprecations.passed

    assert set(report.markers.selected_stub_sets) == {"posix", "windows", "gpu"}
    assert report.deprecations.effective_warning_releases["legacy_parse_version"] == "0.1.0"
    assert report.sdist_sha256
    assert report.wheel_sha256

    serialized = report.to_dict()
    assert set(serialized) == {
        "passed",
        "imports",
        "versions",
        "markers",
        "types",
        "build",
        "licenses",
        "deprecations",
        "artifacts",
    }


def test_release_gate_exposes_individual_failure_algebras(artifact_pair):
    from dataclasses import replace

    sdist, wheel = artifact_pair
    root = Path(__file__).resolve().parents[1]
    request = GateRequest(
        sdist_path=sdist,
        wheel_path=wheel,
        project_root=root,
        version_specifier=">=9.0",
    )

    report = evaluate_release(request)

    assert not report.versions.passed
    # The remaining report fields are still available for diagnosis rather
    # than being replaced by a single first-failure score.
    assert report.imports.passed
    assert report.build.passed
