import tarfile
import zipfile
from io import BytesIO

import pytest

from chipcup.build import compare_artifacts, inspect_artifact

METADATA = (
    b"Metadata-Version: 2.4\n"
    b"Name: chipcup\n"
    b"Version: 0.1.0\n"
    b"License-Expression: MIT\n"
    b"Requires-Dist: packaging>=24.2\n"
    b"\n"
)


def _write_sdist(path, metadata=METADATA, project_root="chipcup-0.1.0"):
    with tarfile.open(path, "w:gz") as archive:
        for name, content in (
            (f"{project_root}/PKG-INFO", metadata),
            (f"{project_root}/LICENSE", b"MIT"),
        ):
            info = tarfile.TarInfo(name)
            info.size = len(content)
            archive.addfile(info, BytesIO(content))


def _write_wheel(path, metadata=METADATA, dist_info="chipcup-0.1.0.dist-info"):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(f"{dist_info}/METADATA", metadata)
        archive.writestr(f"{dist_info}/licenses/LICENSE", "MIT")


def test_inspect_and_compare_wheel_and_sdist(tmp_path):
    wheel = tmp_path / "chipcup-0.1.0-py3-none-any.whl"
    _write_wheel(wheel)
    sdist = tmp_path / "chipcup-0.1.0.tar.gz"
    _write_sdist(sdist)

    sdist_info = inspect_artifact(sdist)
    wheel_info = inspect_artifact(wheel)
    assert compare_artifacts(sdist_info, wheel_info) == ("chipcup", "0.1.0")
    assert sdist_info.kind == "sdist"
    assert wheel_info.kind == "wheel"
    assert sdist_info.requires_dist == ("packaging>=24.2",)


def test_artifact_identity_mismatch_is_rejected(tmp_path):
    artifact = tmp_path / "wrong.whl"
    metadata = (
        b"Metadata-Version: 2.4\n"
        b"Name: other\n"
        b"Version: 1\n"
        b"\n"
    )
    _write_wheel(artifact, metadata=metadata, dist_info="wrong-1.dist-info")
    with pytest.raises(ValueError, match="directory project name"):
        inspect_artifact(artifact)


def test_sdist_root_must_match_metadata_identity(tmp_path):
    artifact = tmp_path / "chipcup-0.1.0.tar.gz"
    _write_sdist(artifact, project_root="other-1")
    with pytest.raises(ValueError, match="directory project name"):
        inspect_artifact(artifact)


def test_sdist_and_wheel_requires_dist_must_match(tmp_path):
    sdist = tmp_path / "chipcup-0.1.0.tar.gz"
    wheel = tmp_path / "chipcup-0.1.0-py3-none-any.whl"
    wheel_metadata = METADATA.replace(
        b"Requires-Dist: packaging>=24.2",
        b"Requires-Dist: packaging>=25",
    )
    _write_sdist(sdist)
    _write_wheel(wheel, metadata=wheel_metadata)

    with pytest.raises(ValueError, match="Requires-Dist"):
        compare_artifacts(inspect_artifact(sdist), inspect_artifact(wheel))
