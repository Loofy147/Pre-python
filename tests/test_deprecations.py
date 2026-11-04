import pytest

from chipcup.deprecations import (
    DeprecationSchedule,
    resolve_shim,
    validate_schedules,
)


def test_removal_requires_two_published_minor_releases():
    schedule = DeprecationSchedule("old_api", "1.0", "1.3")
    validate_schedules((schedule,), ("1.0", "1.1", "1.2", "1.3"))
    with pytest.raises(ValueError):
        validate_schedules((schedule,), ("1.0", "1.2", "1.3"))


def test_soft_deprecation_has_no_automatic_removal():
    schedule = DeprecationSchedule("soft_api", "1.0", soft=True)
    schedule.validate(())


def test_lazy_shim_warns_and_resolves_canonical_symbol():
    with pytest.warns(DeprecationWarning):
        value = resolve_shim("old_parse", "chipcup.versions", "parse_version")
    assert str(value("1.0")) == "1.0"
