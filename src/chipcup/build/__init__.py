"""PEP 517/621 build-artifact inspection and source-to-wheel comparison."""

from __future__ import annotations

import ast
import hashlib
import tarfile
import zipfile
from dataclasses import dataclass
from email.parser import BytesParser
from email.policy import default
from pathlib import Path, PurePosixPath
from typing import Iterable, Mapping

from packaging.utils import canonicalize_name
from packaging.version import Version

from chipcup.licenses import check_artifact_license_coverage
from chipcup.types import AuditReceipt

__all__ = [
    "ArtifactComparison",
    "ArtifactInfo",
    "BuildEvidence",
    "accept_type_receipt",
    "compare_artifacts",
    "inspect_artifact",
    "require_license_coverage",
]


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
    requires_dist: tuple[str, ...]
    license_expression: str | None
    license_files: tuple[str, ...]
    top_level_names: tuple[str, ...]
    public_exports: Mapping[str, tuple[str, ...]]
    build_backend: str | None = None
    dynamic_version: bool = False
    version_hook: str | None = None
    version_hook_deterministic: bool = False


@dataclass(frozen=True, slots=True)
class ArtifactComparison:
    name: str
    version: str
    requires_dist_equal: bool
    top_level_names_equal: bool
    public_exports_equal: bool
    license_metadata_equal: bool
    build_backend: str | None
    dynamic_version: bool
    version_hook: str | None
    version_hook_deterministic: bool

    @property
    def passed(self) -> bool:
        return (
            self.requires_dist_equal
            and self.top_level_names_equal
            and self.public_exports_equal
            and self.license_metadata_equal
            and self.build_backend is not None
            and self.version_hook_deterministic
        )


def accept_type_receipt(receipt: object) -> BuildEvidence:
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


def _metadata_info(data: bytes) -> tuple[
    str, str, tuple[str, ...], str | None, tuple[str, ...]
]:
    message = BytesParser(policy=default).parsebytes(data)
    name = message.get("Name")
    version = message.get("Version")
    if not name or not version:
        raise ValueError("artifact metadata must contain Name and Version")
    Version(version)
    requires_dist = tuple(sorted(message.get_all("Requires-Dist", [])))
    license_expression = message.get("License-Expression")
    license_files = tuple(sorted(message.get_all("License-File", [])))
    return str(name), str(version), requires_dist, license_expression, license_files


def _literal_public_names(source: bytes, path: str) -> tuple[str, ...]:
    try:
        tree = ast.parse(source.decode("utf-8"), filename=path)
    except (SyntaxError, UnicodeDecodeError):
        return ()
    for node in tree.body:
        value: ast.expr | None = None
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
                value = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == "__all__":
                value = node.value
        if value is not None:
            try:
                result = ast.literal_eval(value)
            except (ValueError, TypeError):
                return ()
            if isinstance(result, (tuple, list)) and all(isinstance(item, str) for item in result):
                return tuple(result)
            return ()
    return ()


def _package_exports(files: Mapping[str, bytes]) -> tuple[
    tuple[str, ...], dict[str, tuple[str, ...]]
]:
    names: set[str] = set()
    exports: dict[str, tuple[str, ...]] = {}
    for path, content in files.items():
        normalized = path.replace("\\", "/")
        marker = "/chipcup/"
        if marker not in f"/{normalized}" or not normalized.endswith("/__init__.py"):
            continue
        start = f"/{normalized}".find(marker) + len(marker)
        package_path = f"/{normalized}"[start : -len("/__init__.py")]
        module = "chipcup" if not package_path else "chipcup." + package_path.replace("/", ".")
        names.add(module)
        exports[module] = _literal_public_names(content, normalized)
    return tuple(sorted(names)), exports


def _parse_sdist_pyproject(
    files: Mapping[str, bytes],
) -> tuple[str | None, bool, str | None, str | None]:
    candidates = [
        (path, content)
        for path, content in files.items()
        if path.replace("\\", "/").endswith("/pyproject.toml")
    ]
    if len(candidates) != 1:
        raise ValueError("sdist must contain exactly one root pyproject.toml")
    raw = candidates[0][1].decode("utf-8")
    try:
        import tomllib  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[import-not-found]
    document = tomllib.loads(raw)
    build_system = document.get("build-system", {})
    project = document.get("project", {})
    backend = build_system.get("build-backend")
    dynamic = project.get("dynamic", [])
    if not isinstance(backend, str):
        raise ValueError("sdist pyproject.toml must declare build-system.build-backend")
    if not isinstance(dynamic, list):
        raise ValueError("project.dynamic must be an array")
    static_version = project.get("version")
    if static_version is not None and not isinstance(static_version, str):
        raise ValueError("project.version must be a string")
    if "version" in dynamic and static_version is not None:
        raise ValueError("project.version cannot be both static and dynamic")
    if "version" not in dynamic and static_version is None:
        raise ValueError("project.version must be static or generated by a declared hook")
    hook: str | None = None
    if "version" in dynamic:
        tool = document.get("tool", {})
        setuptools_config = tool.get("setuptools", {}) if isinstance(tool, dict) else {}
        dynamic_config = (
            setuptools_config.get("dynamic", {})
            if isinstance(setuptools_config, dict)
            else {}
        )
        version_config = (
            dynamic_config.get("version")
            if isinstance(dynamic_config, dict)
            else None
        )
        if isinstance(version_config, dict):
            attr = version_config.get("attr")
            file = version_config.get("file")
            if isinstance(attr, str) and not file:
                hook = f"attr:{attr}"
            elif isinstance(file, str) and not attr:
                hook = f"file:{file}"
    return backend, "version" in dynamic, static_version, hook


def _verify_version_hook(
    files: Mapping[str, bytes],
    hook: str | None,
    expected_version: str,
) -> bool:
    if hook is None:
        return False
    if hook.startswith("attr:"):
        qualified = hook[len("attr:") :]
        module_name, separator, attribute = qualified.rpartition(".")
        if not separator or attribute != "__version__" or not module_name:
            return False
        package_path = module_name.replace(".", "/")
        candidates = [
            content
            for path, content in files.items()
            if path.replace("\\", "/").endswith(f"/src/{package_path}/__init__.py")
            or path.replace("\\", "/").endswith(f"/{package_path}/__init__.py")
        ]
        if len(candidates) != 1:
            return False
        try:
            tree = ast.parse(candidates[0].decode("utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            return False
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == attribute
                for target in node.targets
            ):
                try:
                    value = ast.literal_eval(node.value)
                except (ValueError, TypeError):
                    return False
                return isinstance(value, str) and Version(value) == Version(expected_version)
        return False
    if hook.startswith("file:"):
        filename = hook[len("file:") :].replace("\\", "/").lstrip("./")
        candidates = [
            content
            for path, content in files.items()
            if path.replace("\\", "/").endswith("/" + filename)
        ]
        if len(candidates) != 1:
            return False
        try:
            value = candidates[0].decode("utf-8").strip()
            return Version(value) == Version(expected_version)
        except (UnicodeDecodeError, ValueError):
            return False
    return False


def _read_wheel(path: Path) -> tuple[dict[str, bytes], bytes, str]:
    with zipfile.ZipFile(path) as archive:
        members = tuple(archive.namelist())
        files = {
            name: archive.read(name)
            for name in members
            if name.startswith("chipcup/") and name.endswith(".py")
        }
        metadata_names = [
            name for name in members if name.endswith(".dist-info/METADATA")
        ]
        if len(metadata_names) != 1:
            raise ValueError("wheel must contain exactly one dist-info/METADATA")
        return files, archive.read(metadata_names[0]), metadata_names[0]


def _read_sdist(path: Path) -> tuple[dict[str, bytes], bytes, str]:
    with tarfile.open(path, "r:*") as archive:
        members = archive.getmembers()
        files: dict[str, bytes] = {}
        for member in members:
            if not member.isfile():
                continue
            stream = archive.extractfile(member)
            if stream is not None:
                files[member.name] = stream.read()
        metadata_names = [
            name for name in files if name.endswith("/PKG-INFO")
        ]
        if len(metadata_names) != 1:
            raise ValueError("sdist must contain exactly one PKG-INFO")
        return files, files[metadata_names[0]], metadata_names[0]


def inspect_artifact(path: str | Path) -> ArtifactInfo:
    artifact = Path(path)
    raw = artifact.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if artifact.name.endswith(".whl"):
        with zipfile.ZipFile(artifact) as archive:
            members = tuple(sorted(archive.namelist()))
        files, metadata, metadata_path = _read_wheel(artifact)
        kind = "wheel"
        backend = None
        dynamic_version = False
        static_version = None
        version_hook = None
        version_hook_deterministic = False
    elif artifact.name.endswith((".tar.gz", ".tar.bz2", ".tar.xz")):
        with tarfile.open(artifact, "r:*") as archive:
            members = tuple(sorted(member.name for member in archive.getmembers()))
        files, metadata, metadata_path = _read_sdist(artifact)
        kind = "sdist"
        backend, dynamic_version, static_version, version_hook = _parse_sdist_pyproject(files)
    else:
        raise ValueError(f"unsupported artifact type: {artifact.name}")

    name, version, requires_dist, expression, license_files = _metadata_info(metadata)
    metadata_parts = PurePosixPath(metadata_path)
    if kind == "wheel":
        if len(metadata_parts.parts) != 2 or not metadata_parts.parts[0].endswith(".dist-info"):
            raise ValueError("wheel METADATA must be directly inside a dist-info directory")
        directory_stem = metadata_parts.parts[0][:-len(".dist-info")]
    else:
        if len(metadata_parts.parts) != 2 or metadata_parts.parts[1] != "PKG-INFO":
            raise ValueError("sdist PKG-INFO must be at the source root")
        directory_stem = metadata_parts.parts[0]
    try:
        directory_name, directory_version = directory_stem.rsplit("-", 1)
    except ValueError as error:
        raise ValueError("artifact directory does not contain a name-version identity") from error
    if canonicalize_name(directory_name) != canonicalize_name(name):
        raise ValueError(f"artifact directory name {directory_name!r} differs from metadata name {name!r}")
    if Version(directory_version) != Version(version):
        raise ValueError(f"artifact directory version {directory_version!r} differs from metadata version {version!r}")
    if kind == "sdist":
        if not dynamic_version:
            if Version(static_version or "") != Version(version):
                raise ValueError("static pyproject.toml version differs from artifact metadata version")
            version_hook_deterministic = True
        else:
            version_hook_deterministic = (
                backend in {"setuptools.build_meta", "setuptools.build_meta:__legacy__"}
                and _verify_version_hook(files, version_hook, version)
            )
    package_names, public_exports = _package_exports(files)
    return ArtifactInfo(
        path=artifact,
        kind=kind,
        name=name,
        version=version,
        sha256=digest,
        members=members,
        requires_dist=requires_dist,
        license_expression=expression,
        license_files=license_files,
        top_level_names=package_names,
        public_exports=public_exports,
        build_backend=backend,
        dynamic_version=dynamic_version,
        version_hook=version_hook,
        version_hook_deterministic=version_hook_deterministic,
    )


def compare_artifacts(sdist: ArtifactInfo, wheel: ArtifactInfo) -> ArtifactComparison:
    if sdist.kind != "sdist" or wheel.kind != "wheel":
        raise ValueError("expected one sdist followed by one wheel")
    if canonicalize_name(sdist.name) != canonicalize_name(wheel.name):
        raise ValueError("sdist and wheel project names differ")
    if Version(sdist.version) != Version(wheel.version):
        raise ValueError("sdist and wheel versions differ")
    if sdist.requires_dist != wheel.requires_dist:
        raise ValueError("sdist and wheel Requires-Dist metadata differ")
    if sdist.top_level_names != wheel.top_level_names:
        raise ValueError("sdist and wheel top-level package names differ")
    if dict(sdist.public_exports) != dict(wheel.public_exports):
        raise ValueError("sdist and wheel public __all__ surfaces differ")
    if (
        sdist.license_expression != wheel.license_expression
        or sdist.license_files != wheel.license_files
    ):
        raise ValueError("sdist and wheel PEP 639 license metadata differs")
    return ArtifactComparison(
        name=sdist.name,
        version=sdist.version,
        requires_dist_equal=sdist.requires_dist == wheel.requires_dist,
        top_level_names_equal=sdist.top_level_names == wheel.top_level_names,
        public_exports_equal=dict(sdist.public_exports) == dict(wheel.public_exports),
        license_metadata_equal=(
            sdist.license_expression == wheel.license_expression
            and sdist.license_files == wheel.license_files
        ),
        build_backend=sdist.build_backend,
        dynamic_version=sdist.dynamic_version,
        version_hook=sdist.version_hook,
        version_hook_deterministic=sdist.version_hook_deterministic,
    )


def require_license_coverage(
    artifact: ArtifactInfo, license_files: Iterable[str] | None = None
) -> tuple[str, ...]:
    declared = artifact.license_files if license_files is None else tuple(license_files)
    return check_artifact_license_coverage(artifact.members, declared)
