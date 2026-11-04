import tarfile
import zipfile
from dataclasses import dataclass
from io import BytesIO

from chipcup.gate import GateRequest, evaluate_release

METADATA = b"Metadata-Version: 2.4\nName: chipcup\nVersion: 0.1.0\nLicense-Expression: MIT\n\n"


@dataclass
class Receipt:
    source_digest: str = "c" * 64
    passed: bool = True


def test_release_gate_runs_all_seven_boundaries(tmp_path):
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
    (tmp_path / "LICENSE").write_text("MIT", encoding="utf-8")

    report = evaluate_release(
        GateRequest(
            sdist_path=sdist,
            wheel_path=wheel,
            audit_receipt=Receipt(),
            project_root=tmp_path,
        )
    )
    assert report.passed
    assert [step.boundary for step in report.steps] == [
        "imports", "versions", "markers", "types", "build", "licenses", "deprecations"
    ]


def test_release_gate_stops_at_failed_type_receipt(tmp_path):
    report = evaluate_release(
        GateRequest(
            sdist_path=tmp_path / "missing.tar.gz",
            wheel_path=tmp_path / "missing.whl",
            audit_receipt=object(),
            project_root=tmp_path,
        )
    )
    assert not report.passed
    assert report.failed_boundary == "types"
