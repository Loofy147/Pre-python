from __future__ import annotations

import tarfile
import zipfile
from io import BytesIO
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "chipcup"
VERSION = "0.1.0"
NAME = "chipcup"
DIST = f"{NAME}-{VERSION}"
METADATA = (
    "Metadata-Version: 2.4\n"
    "Name: chipcup\n"
    "Version: 0.1.0\n"
    "Requires-Dist: packaging>=24.2\n"
    "Requires-Dist: tomli>=2; python_version < '3.11'\n"
    "License-Expression: MIT\n"
    "License-File: LICENSE\n"
    "License-File: LICENSES/Fixture-Dual.txt\n"
    "\n"
).encode()
PYPROJECT = b"""[build-system]
requires = ["setuptools>=77", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "chipcup"
version = "0.1.0"
dynamic = []
"""


@pytest.fixture
def artifact_pair(tmp_path: Path) -> tuple[Path, Path]:
    sdist = tmp_path / f"{DIST}.tar.gz"
    wheel = tmp_path / f"{DIST}-py3-none-any.whl"
    source_files = sorted(SRC.rglob("*.py"))
    package_data_files = sorted(
        [*SRC.rglob("*.pyi"), *SRC.rglob("*.json")]
    )
    with tarfile.open(sdist, "w:gz") as archive:
        for source in [*source_files, *package_data_files]:
            relative = source.relative_to(ROOT)
            name = f"{DIST}/{relative.as_posix()}"
            content = source.read_bytes()
            info = tarfile.TarInfo(name)
            info.size = len(content)
            archive.addfile(info, BytesIO(content))
        extra_files = {
            f"{DIST}/PKG-INFO": METADATA,
            f"{DIST}/pyproject.toml": PYPROJECT,
            f"{DIST}/LICENSE": (ROOT / "LICENSE").read_bytes(),
            f"{DIST}/LICENSES/Fixture-Dual.txt": (
                ROOT / "LICENSES" / "Fixture-Dual.txt"
            ).read_bytes(),
            f"{DIST}/fixtures/chip.dat": (
                ROOT / "fixtures" / "chip.dat"
            ).read_bytes(),
            f"{DIST}/fixtures/golden-profile.json": (
                ROOT / "fixtures" / "golden-profile.json"
            ).read_bytes(),
        }
        for name, content in extra_files.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            archive.addfile(info, BytesIO(content))

    with zipfile.ZipFile(wheel, "w") as archive:
        for source in [*source_files, *package_data_files]:
            relative = source.relative_to(SRC)
            archive.writestr(f"chipcup/{relative.as_posix()}", source.read_bytes())
        archive.writestr("chipcup/py.typed", b"")
        archive.writestr(
            f"{DIST}.dist-info/METADATA", METADATA
        )
        archive.writestr(
            f"{DIST}.dist-info/licenses/LICENSE",
            (ROOT / "LICENSE").read_bytes(),
        )
        archive.writestr(
            f"{DIST}.dist-info/licenses/Fixture-Dual.txt",
            (ROOT / "LICENSES" / "Fixture-Dual.txt").read_bytes(),
        )
        archive.writestr(
            "chipcup/fixtures/chip.dat",
            (ROOT / "fixtures" / "chip.dat").read_bytes(),
        )
        archive.writestr(
            "chipcup/fixtures/golden-profile.json",
            (ROOT / "fixtures" / "golden-profile.json").read_bytes(),
        )
    return sdist, wheel
