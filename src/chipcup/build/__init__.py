"""PEP 517/621 artifact inspection and source-bound build evidence."""

from __future__ import annotations

import hashlib
import tarfile
import zipfile
from dataclasses import dataclass
from email.parser import BytesParser
from email.policy import default
from pathlib import Path
from typing import Iterable

from packaging.utils import canonicalize_name
from packaging.version import Version


@dataclass(frozen=True, slots=True)
class BuildEvidence:
    source_digest: str
    passed: bool
    receipt_kind: str = "typing-audit"


@dataclass(frozen=True, slots=True)
class ArtifactInfo:
    path: Path
    kind: str
    name: str
    version: str
    sha256: str
    members: tuple[str, ...]


def accept_type_receipt(receipt: object) -> BuildEvidence:
    from chipcup.types import AuditReceipt

    if not isinstance(receipt, AuditReceipt):
        raise TypeError("build requires an AuditReceipt")
    digest = receipt.source_digest
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("source_digest must be a 64-character SHA-256 hex digest")
    try:
        int(digest, 16)
    except ValueError as error:
        raise ValueError("source_digest is not hexadecimal") from error
    if receipt.passed is not True:
        raise ValueError("failed type audit cannot enter the build boundary")
    return BuildEvidence(source_digest=digest.lower(), passed=True)


def _metadata_info(data: bytes) -> tuple[str, str]:
    message = BytesParser(policy=default).parsebytes(data)
    name = message.get("Name")
    version = message.get("Version")
    if not name or not version:
        raise ValueError("artifact metadata must contain Name and Version")
    Version(version)
    return str(name), str(version)


def inspect_artifact(path: str | Path) -> ArtifactInfo:
    artifact = Path(path)
    raw = artifact.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if artifact.name.endswith(".whl"):
        with zipfile.ZipFile(artifact) as archive:
            members = tuple(sorted(archive.namelist()))
            metadata_names = [name for name in members if name.endswith(".dist-info/METADATA")]
            if len(metadata_names) != 1:
                raise ValueError("wheel must contain exactly one dist-info/METADATA")
            name, version = _metadata_info(archive.read(metadata_names[0]))
        kind = "wheel"
    elif artifact.name.endswith((".tar.gz", ".tar.bz2", ".tar.xz")):
        with tarfile.open(artifact, "r:*") as archive:
            members = tuple(sorted(member.name for member in archive.getmembers()))
            metadata_members = [
                member for member in archive.getmembers()
                if member.isfile() and member.name.endswith("/PKG-INFO")
            ]
            if len(metadata_members) != 1:
                raise ValueError("sdist must contain exactly one PKG-INFO")
            stream = archive.extractfile(metadata_members[0])
            if stream is None:
                raise ValueError("could not read sdist PKG-INFO")
            name, version = _metadata_info(stream.read())
        kind = "sdist"
    else:
        raise ValueError(f"unsupported artifact type: {artifact.name}")
    return ArtifactInfo(artifact, kind, name, version, digest, members)


def compare_artifacts(sdist: ArtifactInfo, wheel: ArtifactInfo) -> tuple[str, str]:
    if sdist.kind != "sdist" or wheel.kind != "wheel":
        raise ValueError("expected one sdist followed by one wheel")
    if canonicalize_name(sdist.name) != canonicalize_name(wheel.name):
        raise ValueError("sdist and wheel project names differ")
    if Version(sdist.version) != Version(wheel.version):
        raise ValueError("sdist and wheel versions differ")
    return sdist.name, sdist.version


def require_license_coverage(
    artifact: ArtifactInfo, license_files: Iterable[str]
) -> tuple[str, ...]:
    from chipcup.licenses import check_artifact_license_coverage

    return check_artifact_license_coverage(artifact.members, license_files)
