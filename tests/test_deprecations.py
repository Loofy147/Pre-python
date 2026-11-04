import pytest

from chipcup.deprecations import (
    DeprecationSchedule,
    WarningObservation,
    capture_warning_observation,
    validate_schedules,
)


def test_warning_capture_requires_a_selected_row():
    called = False

    def invoke():
        nonlocal called
        called = True

    observation = capture_warning_observation("1.2", "linux", False, invoke)

    assert not called
    assert not observation.marker_selected
    assert not observation.emitted
    assert observation.warning_count == 0


def test_warning_capture_records_an_actually_emitted_warning():
    import warnings

    observation = capture_warning_observation(
        "1.2",
        "linux",
        True,
        lambda: warnings.warn("old_api is deprecated", DeprecationWarning),
    )

    assert observation.marker_selected
    assert observation.emitted
    assert observation.warning_count == 1


def test_removal_window_begins_after_every_required_row_emits():
    schedule = DeprecationSchedule(
        "old_api",
        removal_release="1.5",
        required_matrix_rows=("linux", "windows"),
    )
    observations = (
        WarningObservation("1.2", "linux", True, True, 1),
        WarningObservation("1.3", "windows", True, True, 1),
    )

    result = validate_schedules(
        (schedule,),
        ("1.0", "1.2", "1.3", "1.4", "1.5"),
        observations,
    )

    assert result.passed
    assert result.effective_warning_releases["old_api"] == "1.3"
    assert not result.missing_warning_rows


def test_unselected_or_unemitted_row_does_not_start_the_clock():
    schedule = DeprecationSchedule(
        "old_api",
        removal_release="1.5",
        required_matrix_rows=("linux", "windows"),
    )
    observations = (
        WarningObservation("1.2", "linux", True, True, 1),
        WarningObservation("1.1", "windows", False, False, 0),
        WarningObservation("1.4", "windows", True, False, 0),
    )

    result = validate_schedules(
        (schedule,),
        ("1.0", "1.2", "1.3", "1.4", "1.5"),
        observations,
    )

    assert not result.passed
    assert "windows" in result.missing_warning_rows["old_api"]
    assert "old_api" not in result.effective_warning_releases


def test_warning_shipped_but_never_observed_on_required_row_blocks_removal():
    schedule = DeprecationSchedule(
        "old_api",
        removal_release="2.0",
        required_matrix_rows=("linux",),
    )
    result = validate_schedules(
        (schedule,),
        ("1.0", "1.1", "1.2", "2.0"),
        (),
    )
    assert not result.passed
    assert "linux" in result.missing_warning_rows["old_api"]


def test_soft_deprecation_has_no_automatic_removal():
    schedule = DeprecationSchedule("soft_api", None, soft=True)
    result = validate_schedules((schedule,), ("1.0",), ())
    assert result.passed


def test_soft_deprecation_cannot_declare_a_removal_release():
    with pytest.raises(ValueError, match="soft deprecations"):
        DeprecationSchedule("soft_api", "2.0", soft=True)
