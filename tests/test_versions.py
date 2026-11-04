from chipcup.versions import VersionPolicy, parse_version


def test_pep440_total_order_and_labels():
    assert parse_version("1!1.0a1") < parse_version("1!1.0rc1")
    assert parse_version("1.0") < parse_version("1.0.post1")
    assert parse_version("1.0+linux") > parse_version("1.0")


def test_specifier_satisfaction_and_environment_handoff():
    policy = VersionPolicy(">=1.0rc1,<2")
    assert policy.accepts("1.0rc2")
    assert not policy.accepts("2.0")
    assert policy.accepts_for("1.2", 'python_version >= "3.10"')
    assert not policy.accepts_for("1.2", 'python_version < "3.10"')
