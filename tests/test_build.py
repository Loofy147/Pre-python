import tarfile
import zipfile
from io import BytesIO

import pytest

from chipcup.build import compare_artifacts, inspect_artifact

METADATA = b"Metadata-Version: 2.4\nName: chipcup\nVersion: 0.1.0\nLicense-Expression: MIT\n\n"


def test_inspect_and_compare_wheel_and_sdist(tmp_path):
    wheel = tmp_path / "chipcup-0.1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("chipcup-0.1.0.dist-info/METADATA", METADATA)
        archive.writestr("chipcup-0.1.0.dist-info/licenses/LICENSE", "MIT")
    sdist = tmp_path / "chipcup-0.1.0.tar.gz"
    with tarfile.open(sdist, "w:gz") as archive:
        for name, content in (
            ("chipcup-0.1.0/PKG-INFO", METADATA),
            ("chipcup-0.1.0/LICENSE", b"MIT"),
        ):
            info = tarfile.TarInfo(name)
            info.size = len(content)
            archive.addfile(info, BytesIO(content))

    sdist_info = inspect_artifact(sdist)
    wheel_info = inspect_artifact(wheel)
    assert compare_artifacts(sdist_info, wheel_info) == ("chipcup", "0.1.0")
    assert sdist_info.kind == "sdist"
    assert wheel_info.kind == "wheel"


def test_artifact_identity_mismatch_is_rejected(tmp_path):
    artifact = tmp_path / "wrong.whl"
    with zipfile.ZipFile(artifact, "w") as archive:
        archive.writestr(
            "wrong-1.dist-info/METADATA",
            b"Metadata-Version: 2.4\nName: other\nVersion: 1\n\n",
        )
    with pytest.raises(ValueError):
        inspect_artifact(artifact)
