from __future__ import annotations

import tarfile
import zipfile
from io import BytesIO
from pathlib import Path

import pytest

from chipcup.build import compare_artifacts, inspect_artifact


def test_realistic_sdist_and_wheel_are_consistent(artifact_pair):
    sdist, wheel = artifact_pair
    source = inspect_artifact(sdist)
    binary = inspect_artifact(wheel)

    comparison = compare_artifacts(source, binary)

    assert comparison.passed
    assert comparison.name == "chipcup"
    assert comparison.version == "0.1.0"
    assert comparison.build_backend == "setuptools.build_meta"
    assert comparison.requires_dist_equal
    assert comparison.top_level_names_equal
    assert comparison.public_exports_equal
    assert comparison.license_metadata_equal
    assert "chipcup" in source.top_level_names
    assert source.public_exports["chipcup"] == binary.public_exports["chipcup"]


def test_wheel_directory_identity_must_match_core_metadata(tmp_path: Path):
    path = tmp_path / "wrong-0.1.0-py3-none-any.whl"
    metadata = (
        b"Metadata-Version: 2.4\nName: different-name\nVersion: 0.1.0\n\n"
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("wrong-0.1.0.dist-info/METADATA", metadata)
    with pytest.raises(ValueError, match="directory name"):
        inspect_artifact(path)


def test_sdist_root_identity_must_match_pkg_info(tmp_path: Path):
    path = tmp_path / "chipcup-0.1.0.tar.gz"
    metadata = b"Metadata-Version: 2.4\nName: chipcup\nVersion: 0.1.0\n\n"
    with tarfile.open(path, "w:gz") as archive:
        for name, content in (
            ("different-0.1.0/PKG-INFO", metadata),
            ("different-0.1.0/pyproject.toml", b"[build-system]\nrequires=['setuptools>=77']\nbuild-backend='setuptools.build_meta'\n\n[project]\nname='chipcup'\nversion='0.1.0'\ndynamic=[]\n"),
        ):
            info = tarfile.TarInfo(name)
            info.size = len(content)
            archive.addfile(info, BytesIO(content))
    with pytest.raises(ValueError, match="directory name"):
        inspect_artifact(path)


def test_dynamic_version_with_matching_literal_hook_is_reproducible(artifact_pair, tmp_path):
    sdist, wheel = artifact_pair
    dynamic_sdist = tmp_path / "chipcup-0.1.0.tar.gz"
    rewritten_members: list[tuple[str, bytes]] = []
    with tarfile.open(sdist, "r:gz") as source:
        for member in source.getmembers():
            if not member.isfile():
                continue
            stream = source.extractfile(member)
            if stream is None:
                continue
            data = stream.read()
            if member.name.endswith("/pyproject.toml"):
                data = data.replace(
                    b'version = "0.1.0"\ndynamic = []',
                    b'dynamic = ["version"]\n\n[tool.setuptools.dynamic]\nversion = { attr = "chipcup.__version__" }',
                )
            rewritten_members.append((member.name, data))

    with tarfile.open(dynamic_sdist, "w:gz") as output:
        for name, data in rewritten_members:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            output.addfile(info, BytesIO(data))
    result = compare_artifacts(
        inspect_artifact(dynamic_sdist),
        inspect_artifact(wheel),
    )
    assert result.dynamic_version
    assert result.version_hook == "attr:chipcup.__version__"
    assert result.version_hook_deterministic
    assert result.passed



def test_nested_egg_info_pkg_info_does_not_shadow_root_metadata(
    artifact_pair, tmp_path: Path
):
    sdist, _ = artifact_pair
    candidate = tmp_path / "nested-pkg-info.tar.gz"
    with tarfile.open(sdist, "r:gz") as source:
        files: list[tuple[str, bytes]] = []
        for member in source.getmembers():
            if not member.isfile():
                continue
            stream = source.extractfile(member)
            if stream is not None:
                files.append((member.name, stream.read()))
    files.append(
        (
            "chipcup-0.1.0/src/chipcup.egg-info/PKG-INFO",
            b"Metadata-Version: 2.4\\nName: wrong\\nVersion: 9.9\\n\\n",
        )
    )
    with tarfile.open(candidate, "w:gz") as output:
        for name, data in files:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            output.addfile(info, BytesIO(data))

    artifact = inspect_artifact(candidate)
    assert artifact.name == "chipcup"
    assert artifact.version == "0.1.0"
