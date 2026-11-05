from chipcup.versions import VersionPolicy, parse_version


def test_pep440_versions_are_totally_ordered():
    assert parse_version("1!1.0a1") < parse_version("1!1.0rc1")
    assert parse_version("1.0") < parse_version("1.0.post1")
    assert parse_version("1.0+linux") > parse_version("1.0")


def test_specifier_satisfaction_includes_local_version_for_public_equality():
    assert VersionPolicy("==1.0").accepts("1.0+local")


def test_specifier_satisfaction_and_matrix_selection():
    policy = VersionPolicy(">=1.0rc1,<2")
    assert policy.accepts("1.0rc2")
    assert not policy.accepts("2.0")


def test_imported_version_must_equal_installed_metadata():
    policy = VersionPolicy(">=0.1,<1")
    consistent = policy.audit_distribution("0.1.0", "0.1.0")
    drifted = policy.audit_distribution("0.1.0", "0.1.1")

    assert consistent.passed
    assert not drifted.metadata_matches_import
    assert not drifted.passed
