from pathlib import Path

import pytest

from chipcup.deprecations import DeprecationSchedule
from chipcup.licenses import (
    DEFAULT_LICENSE_REFS,
    DEFAULT_LICENSE_REF_SUBJECTS,
    license_references,
    parse_license_expression,
    validate_compatibility,
)


def test_spdx_boolean_expression_and_custom_reference():
    tree = parse_license_expression("MIT AND LicenseRef-Fixture-Dual")
    assert tree.kind == "and"
    assert license_references(tree) == ("LicenseRef-Fixture-Dual",)


def test_with_exception_has_distinct_precedence():
    tree = parse_license_expression(
        "GPL-2.0-only WITH Classpath-exception-2.0 OR MIT"
    )
    assert tree.kind == "or"
    assert tree.children[0].kind == "with"


def test_invalid_expression_fails_closed():
    with pytest.raises(ValueError):
        parse_license_expression("MIT AND OR Apache-2.0")


def test_custom_license_ref_needs_declared_text_file(tmp_path: Path):
    (tmp_path / "LICENSE").write_text("MIT", encoding="utf-8")
    dual = tmp_path / "LICENSES" / "Fixture-Dual.txt"
    dual.parent.mkdir()
    dual.write_text("fixture is MIT OR Apache-2.0", encoding="utf-8")
    fixture = tmp_path / "fixtures" / "chip.dat"
    fixture.parent.mkdir()
    fixture.write_bytes(b"CHIPCUP_FIXTURE_V1\\n")

    result = validate_compatibility(
        "MIT",
        {
            "sdist": (
                "chipcup-0.1.0/PKG-INFO",
                "chipcup-0.1.0/LICENSE",
                "chipcup-0.1.0/LICENSES/Fixture-Dual.txt",
                "chipcup-0.1.0/fixtures/chip.dat",
            ),
            "wheel": (
                "chipcup-0.1.0.dist-info/METADATA",
                "chipcup-0.1.0.dist-info/licenses/LICENSE",
                "chipcup-0.1.0.dist-info/licenses/Fixture-Dual.txt",
                "chipcup/fixtures/chip.dat",
            ),
        },
        ("LICENSE", "LICENSES/Fixture-Dual.txt"),
        root=tmp_path,
        license_refs=DEFAULT_LICENSE_REFS,
        license_ref_subjects=DEFAULT_LICENSE_REF_SUBJECTS,
    )
    assert result.passed
    assert result.reference_subjects["LicenseRef-Fixture-Dual"] == ("fixtures/chip.dat",)
    assert not result.missing_subject_artifact_files
    assert result.references == ("LicenseRef-Fixture-Dual",)


def test_unresolved_custom_ref_blocks_deprecation_schedule(tmp_path: Path):
    (tmp_path / "LICENSE").write_text("MIT", encoding="utf-8")
    schedule = DeprecationSchedule(
        "legacy_shim",
        removal_release=None,
        required_matrix_rows=("linux",),
        required_license_refs=("LicenseRef-Unresolved",),
    )
    result = validate_compatibility(
        "MIT",
        {"wheel": ("chipcup-0.1.0.dist-info/licenses/LICENSE",)},
        ("LICENSE",),
        root=tmp_path,
        license_refs={},
        deprecations=(schedule,),
    )
    assert not result.passed
    assert result.dependency_issues


def test_custom_license_ref_must_be_declared_as_a_license_file(tmp_path: Path):
    (tmp_path / "LICENSE").write_text("MIT", encoding="utf-8")
    dual = tmp_path / "LICENSES" / "Fixture-Dual.txt"
    dual.parent.mkdir()
    dual.write_text("fixture alternative license", encoding="utf-8")
    fixture = tmp_path / "fixtures" / "chip.dat"
    fixture.parent.mkdir()
    fixture.write_bytes(b"CHIPCUP_FIXTURE_V1")
    result = validate_compatibility(
        "MIT",
        {"wheel": (
            "x.dist-info/licenses/LICENSE",
            "x.dist-info/licenses/Fixture-Dual.txt",
            "chipcup/fixtures/chip.dat",
        )},
        ("LICENSE",),
        root=tmp_path,
        license_refs=DEFAULT_LICENSE_REFS,
    )
    assert not result.passed
    assert any("not declared as License-File" in issue for issue in result.issues)



def test_custom_license_ref_requires_its_subject_in_each_archive(tmp_path: Path):
    (tmp_path / "LICENSE").write_text("MIT", encoding="utf-8")
    dual = tmp_path / "LICENSES" / "Fixture-Dual.txt"
    dual.parent.mkdir()
    dual.write_text("fixture alternative license", encoding="utf-8")
    fixture = tmp_path / "fixtures" / "chip.dat"
    fixture.parent.mkdir()
    fixture.write_bytes(b"CHIPCUP_FIXTURE_V1")

    result = validate_compatibility(
        "MIT",
        {
            "sdist": (
                "chipcup-0.1.0/PKG-INFO",
                "chipcup-0.1.0/LICENSE",
                "chipcup-0.1.0/LICENSES/Fixture-Dual.txt",
            ),
            "wheel": (
                "chipcup-0.1.0.dist-info/METADATA",
                "chipcup-0.1.0.dist-info/licenses/LICENSE",
                "chipcup-0.1.0.dist-info/licenses/Fixture-Dual.txt",
                "chipcup/fixtures/chip.dat",
            ),
        },
        ("LICENSE", "LICENSES/Fixture-Dual.txt"),
        root=tmp_path,
        license_refs=DEFAULT_LICENSE_REFS,
        license_ref_subjects=DEFAULT_LICENSE_REF_SUBJECTS,
    )

    assert not result.passed
    assert result.missing_subject_artifact_files["LicenseRef-Fixture-Dual"]["sdist"] == (
        "fixtures/chip.dat",
    )
