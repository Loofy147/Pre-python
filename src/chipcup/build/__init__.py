"""PEP 517/621 artifact inspection and source-bound build evidence."""

from __future__ import annotations

import hashlib
import tarfile
import zipfile
from dataclasses import dataclass
from email.parser import BytesParser
from email.policy import default
from pathlib import Path, PurePosixPath
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
    requires_dist: tuple[str, ...] = ()


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


def _metadata_info(data: bytes) -> tuple[str, str, tuple[str, ...]]:
    message = BytesParser(policy=default).parsebytes(data)
    name = message.get("Name")
    version = message.get("Version")
    if not name or not version:
        raise ValueError("artifact metadata must contain Name and Version")
    Version(version)
    requires_dist = tuple(sorted(message.get_all("Requires-Dist", [])))
    return str(name), str(version), requires_dist


def _validate_distribution_directory(
    directory: str,
    suffix: str,
    name: str,
    version: str,
    *,
    kind: str,
) -> None:
    if suffix and not directory.endswith(suffix):
        raise ValueError(f"{kind} metadata is outside its expected distribution directory")
    stem = directory[: -len(suffix)] if suffix else directory
    try:
        directory_name, directory_version = stem.rsplit("-", 1)
    except ValueError as error:
        raise ValueError(f"{kind} distribution directory has no name-version boundary") from error
    if canonicalize_name(directory_name) != canonicalize_name(name):
        raise ValueError(
            f"{kind} directory project name {directory_name!r} "
            f"does not match metadata name {name!r}"
        )
    if Version(directory_version) != Version(version):
        raise ValueError(
            f"{kind} directory version {directory_version!r} "
            f"does not match metadata version {version!r}"
        )


def inspect_artifact(path: str | Path) -> ArtifactInfo:
    artifact = Path(path)
    raw = artifact.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if artifact.name.endswith(".whl"):
        with zipfile.ZipFile(artifact) as archive:
            members = tuple(sorted(archive.namelist()))
            metadata_names = [
                name for name in members if name.endswith(".dist-info/METADATA")
            ]
            if len(metadata_names) != 1:
                raise ValueError("wheel must contain exactly one dist-info/METADATA")
            metadata_path = PurePosixPath(metadata_names[0])
            if len(metadata_path.parts) != 2 or metadata_path.parts[1] != "METADATA":
                raise ValueError("wheel METADATA must be directly inside its dist-info directory")
            name, version, requires_dist = _metadata_info(archive.read(metadata_names[0]))
            _validate_distribution_directory(
                metadata_path.parts[0], ".dist-info", name, version, kind="wheel"
            )
        kind = "wheel"
    elif artifact.name.endswith((".tar.gz", ".tar.bz2", ".tar.xz")):
        with tarfile.open(artifact, "r:*") as archive:
            members = tuple(sorted(member.name for member in archive.getmembers()))
            metadata_members = [
                member
                for member in archive.getmembers()
                if member.isfile() and member.name.endswith("/PKG-INFO")
            ]
            if len(metadata_members) != 1:
                raise ValueError("sdist must contain exactly one PKG-INFO")
            metadata_path = PurePosixPath(metadata_members[0].name)
            if len(metadata_path.parts) != 2 or metadata_path.parts[1] != "PKG-INFO":
                raise ValueError("sdist PKG-INFO must be at the source root")
            stream = archive.extractfile(metadata_members[0])
            if stream is None:
                raise ValueError("could not read sdist PKG-INFO")
            name, version, requires_dist = _metadata_info(stream.read())
            _validate_distribution_directory(
                metadata_path.parts[0], "", name, version, kind="sdist"
            )
        kind = "sdist"
    else:
        raise ValueError(f"unsupported artifact type: {artifact.name}")
    return ArtifactInfo(
        artifact, kind, name, version, digest, members, requires_dist
    )


def compare_artifacts(sdist: ArtifactInfo, wheel: ArtifactInfo) -> tuple[str, str]:
    if sdist.kind != "sdist" or wheel.kind != "wheel":
        raise ValueError("expected one sdist followed by one wheel")
    if canonicalize_name(sdist.name) != canonicalize_name(wheel.name):
        raise ValueError("sdist and wheel project names differ")
    if Version(sdist.version) != Version(wheel.version):
        raise ValueError("sdist and wheel versions differ")
    if sdist.requires_dist != wheel.requires_dist:
        raise ValueError("sdist and wheel Requires-Dist metadata differ")
    return sdist.name, sdist.version


def require_license_coverage(
    artifact: ArtifactInfo, license_files: Iterable[str]
) -> tuple[str, ...]:
    from chipcup.licenses import check_artifact_license_coverage

    return check_artifact_license_coverage(artifact.members, license_files)
