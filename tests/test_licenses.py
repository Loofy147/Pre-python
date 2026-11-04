import pytest

from chipcup.licenses import (
    check_artifact_license_coverage,
    license_references,
    parse_license_expression,
)


def test_spdx_boolean_expression_and_licenseref():
    tree = parse_license_expression("MIT AND (Apache-2.0 OR LicenseRef-Commercial)")
    assert tree.kind == "and"
    assert license_references(tree) == ("LicenseRef-Commercial",)


def test_with_exception_has_distinct_precedence():
    tree = parse_license_expression(
        "GPL-2.0-only WITH Classpath-exception-2.0 OR MIT"
    )
    assert tree.kind == "or"
    assert tree.children[0].kind == "with"


def test_invalid_expression_fails_closed():
    with pytest.raises(ValueError):
        parse_license_expression("MIT AND OR Apache-2.0")


def test_license_file_coverage_is_artifact_specific():
    members = ("pkg-1.dist-info/METADATA", "pkg-1.dist-info/licenses/LICENSE")
    assert check_artifact_license_coverage(members, ("LICENSE",)) == ()
    assert check_artifact_license_coverage(members, ("NOTICE",)) == ("NOTICE",)
