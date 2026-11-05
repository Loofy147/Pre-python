from __future__ import annotations

from chipcup.exit_codes import ExitCode, EXIT_PRECEDENCE, select_exit_code


def _healthy_report():
    names = (
        "build", "licenses", "types", "markers", "deprecations",
        "imports", "versions", "build_cycle_closure",
    )
    return {
        "passed": True,
        "receipts": {
            name: {"state": "PASS", "evidence": {}, "issues": []}
            for name in names
        },
    }


def _set(report, boundary, state, *, evidence=None, issues=None):
    report["passed"] = False
    report["receipts"][boundary] = {
        "state": state,
        "evidence": evidence or {},
        "issues": issues or [],
    }


def test_healthy_complete_receipt_report_exits_zero():
    assert select_exit_code(_healthy_report()) is ExitCode.OK


def test_each_boundary_failure_has_a_stable_exit_code():
    cases = (
        ("deprecations", ExitCode.DEPRECATION_UNPROVEN),
        ("licenses", ExitCode.LICENSE_UNRESOLVED),
        ("types", ExitCode.TYPE_SURFACE_INVALID),
        ("markers", ExitCode.MARKER_MATRIX_INVALID),
        ("imports", ExitCode.IMPORT_AUDIT_FAILED),
        ("versions", ExitCode.VERSION_MISMATCH),
        ("build_cycle_closure", ExitCode.BUILD_RELEASE_IDENTITY),
        ("build", ExitCode.BUILD_DIVERGENT),
    )
    for boundary, expected in cases:
        report = _healthy_report()
        _set(report, boundary, "FAIL")
        assert select_exit_code(report) is expected


def test_missing_required_receipt_is_never_success():
    report = _healthy_report()
    del report["receipts"]["markers"]
    assert select_exit_code(report) is ExitCode.AUDIT_UNVERIFIED


def test_unverified_required_receipt_is_nonzero():
    report = _healthy_report()
    _set(report, "markers", "UNVERIFIED")
    assert select_exit_code(report) is ExitCode.AUDIT_UNVERIFIED


def test_unavailable_build_has_its_own_fatal_exit():
    report = _healthy_report()
    _set(report, "build", "UNVERIFIED")
    assert select_exit_code(report) is ExitCode.BUILD_UNAVAILABLE


def test_fixture_geometry_failure_has_a_distinct_exit():
    report = _healthy_report()
    _set(
        report,
        "build",
        "FAIL",
        evidence={"geometry": {"wheel": {"passed": False}}},
    )
    assert select_exit_code(report) is ExitCode.FIXTURE_GEOMETRY


def test_malformed_receipt_state_returns_audit_error_without_raising():
    report = _healthy_report()
    report["receipts"]["markers"]["state"] = []
    assert select_exit_code(report) is ExitCode.AUDIT_ERROR


def test_exit_precedence_is_explicit_and_total_for_fatal_codes():
    assert len(EXIT_PRECEDENCE) == len(set(EXIT_PRECEDENCE))
    assert set(EXIT_PRECEDENCE) == {
        ExitCode.AUDIT_ERROR,
        ExitCode.AUDIT_UNVERIFIED,
        ExitCode.DEPRECATION_UNPROVEN,
        ExitCode.TYPE_SURFACE_INVALID,
        ExitCode.MARKER_MATRIX_INVALID,
        ExitCode.IMPORT_AUDIT_FAILED,
        ExitCode.VERSION_MISMATCH,
        ExitCode.BUILD_RELEASE_IDENTITY,
        ExitCode.BUILD_DIVERGENT,
        ExitCode.LICENSE_UNRESOLVED,
        ExitCode.FIXTURE_GEOMETRY,
        ExitCode.BUILD_UNAVAILABLE,
    }


def test_build_divergence_outranks_deprecation_unproven():
    report = _healthy_report()
    _set(report, "deprecations", "FAIL")
    _set(report, "build", "FAIL")
    assert select_exit_code(report) is ExitCode.BUILD_DIVERGENT


def test_license_failure_outranks_build_divergence():
    report = _healthy_report()
    _set(report, "deprecations", "FAIL")
    _set(report, "build", "FAIL")
    _set(report, "licenses", "FAIL")
    assert select_exit_code(report) is ExitCode.LICENSE_UNRESOLVED


def test_geometry_failure_outranks_license_failure():
    report = _healthy_report()
    _set(report, "licenses", "FAIL")
    _set(
        report,
        "build",
        "FAIL",
        evidence={"geometry": {"wheel": {"passed": False}}},
    )
    assert select_exit_code(report) is ExitCode.FIXTURE_GEOMETRY
