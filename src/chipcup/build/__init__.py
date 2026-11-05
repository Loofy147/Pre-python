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

import json
import math

from chipcup._contracts import (
    AuditReceipt, BoundaryReceipt, BuildEvidence, ReceiptState, unavailable,
)

__all__ = [
    "ArtifactComparison",
    "ArtifactInfo",
    "BuildEvidence",
    "accept_type_receipt",
    "compare_artifacts",
    "inspect_artifact",
    "require_license_coverage",
    "close_version_cycle",
    "degraded_receipt",
    "evaluate_artifact_receipt",
    "measure_notch",
    "read_artifact_member",
    "validate_notch_profile",
]


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
        if len(PurePosixPath(path.replace("\\", "/")).parts) == 2
        and PurePosixPath(path.replace("\\", "/")).name == "pyproject.toml"
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
            name
            for name in files
            if len(PurePosixPath(name).parts) == 2
            and PurePosixPath(name).name == "PKG-INFO"
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


def check_artifact_license_coverage(
    members: Iterable[str], license_files: Iterable[str]
) -> tuple[str, ...]:
    paths = tuple(member.replace("\\\\", "/").lstrip("./") for member in members)
    missing: list[str] = []
    for filename in license_files:
        target = filename.replace("\\\\", "/").lstrip("./")
        basename = Path(target).name
        if not any(
            member == target
            or member.endswith("/" + target)
            or member.endswith(".dist-info/licenses/" + basename)
            for member in paths
        ):
            missing.append(filename)
    return tuple(missing)


def require_license_coverage(
    artifact: ArtifactInfo, license_files: Iterable[str] | None = None
) -> tuple[str, ...]:
    declared = artifact.license_files if license_files is None else tuple(license_files)
    return check_artifact_license_coverage(artifact.members, declared)


def read_artifact_member(path: str | Path, suffix: str) -> bytes:
    """Read one named payload from an sdist or wheel without extracting it."""
    artifact = Path(path)
    normalized_suffix = suffix.replace("\\\\", "/").lstrip("./")
    if artifact.name.endswith(".whl"):
        with zipfile.ZipFile(artifact) as archive:
            candidates = [
                name for name in archive.namelist()
                if name.replace("\\\\", "/").endswith(normalized_suffix)
            ]
            if len(candidates) != 1:
                raise ValueError(
                    f"{artifact.name} must contain exactly one {normalized_suffix}"
                )
            return archive.read(candidates[0])
    with tarfile.open(artifact, "r:*") as archive:
        tar_candidates = [
            member for member in archive.getmembers()
            if member.isfile()
            and member.name.replace("\\\\", "/").endswith(normalized_suffix)
        ]
        if len(tar_candidates) != 1:
            raise ValueError(
                f"{artifact.name} must contain exactly one {normalized_suffix}"
            )
        stream = archive.extractfile(tar_candidates[0])
        if stream is None:
            raise ValueError(f"cannot read {normalized_suffix} from {artifact.name}")
        return stream.read()


def _point(value: object, label: str) -> tuple[float, float]:
    if (
        not isinstance(value, list)
        or len(value) != 2
        or not all(isinstance(item, (int, float)) for item in value)
    ):
        raise ValueError(f"{label} must be a two-coordinate millimetre point")
    return float(value[0]), float(value[1])


def _profile_points(document: Mapping[str, object]) -> tuple[
    tuple[float, float], tuple[float, float],
    tuple[float, float], tuple[float, float], tuple[float, float]
]:
    if document.get("schema") != "chipcup-rim-profile/v1":
        raise ValueError("fixture schema must be chipcup-rim-profile/v1")
    if document.get("unit") != "mm":
        raise ValueError("fixture geometry unit must be mm")
    rim = document.get("rim")
    notch = document.get("notch")
    if not isinstance(rim, dict) or not isinstance(notch, dict):
        raise ValueError("fixture must contain rim and notch geometry")
    return (
        _point(rim.get("left"), "rim.left"),
        _point(rim.get("right"), "rim.right"),
        _point(notch.get("left"), "notch.left"),
        _point(notch.get("apex"), "notch.apex"),
        _point(notch.get("right"), "notch.right"),
    )


def measure_notch(profile: bytes | str) -> dict[str, float]:
    """Measure notch depth and derive the allowed geometric deviation."""
    decoded = json.loads(profile.decode("utf-8") if isinstance(profile, bytes) else profile)
    if not isinstance(decoded, dict):
        raise ValueError("fixture profile must be a JSON object")
    if decoded.get("object") != "teacup":
        raise ValueError("golden payload object must be a teacup")
    left, right, notch_left, apex, notch_right = _profile_points(decoded)
    if right[0] == left[0]:
        raise ValueError("rim reference line must have non-zero horizontal span")
    fraction = 0.05
    baseline_y = left[1] + (right[1] - left[1]) * (
        (apex[0] - left[0]) / (right[0] - left[0])
    )
    depth = baseline_y - apex[1]
    if depth <= 0:
        raise ValueError("notch apex must be below the rim reference line")
    return {
        "notch_depth_mm": round(depth, 6),
        "notch_width_mm": round(notch_right[0] - notch_left[0], 6),
        "tolerance_mm": round(depth * fraction, 6),
    }


def validate_notch_profile(
    profile: bytes | str, golden: Mapping[str, object]
) -> dict[str, object]:
    """Compare all three notch points against the golden geometry.

    The tolerance is five percent of the golden notch depth. For the shipped
    2.40 mm notch this is 0.12 mm.
    """
    decoded = json.loads(profile.decode("utf-8") if isinstance(profile, bytes) else profile)
    if not isinstance(decoded, dict):
        raise ValueError("fixture profile must be a JSON object")
    if decoded.get("object") != "teacup":
        raise ValueError("golden payload object must be a teacup")
    expected_document = dict(golden)
    expected_document["schema"] = "chipcup-rim-profile/v1"
    expected = _profile_points(expected_document)
    actual = _profile_points(decoded)
    rim_left, rim_right = expected[0], expected[1]
    apex_x = expected[3][0]
    if rim_right[0] == rim_left[0]:
        raise ValueError("golden rim reference line must have non-zero span")
    expected_rim_y = rim_left[1] + (rim_right[1] - rim_left[1]) * (
        (apex_x - rim_left[0]) / (rim_right[0] - rim_left[0])
    )
    expected_depth = expected_rim_y - expected[3][1]
    fraction = golden.get("tolerance_fraction_of_notch_depth", 0.05)
    if not isinstance(fraction, (int, float)) or fraction <= 0:
        raise ValueError("golden tolerance fraction must be positive")
    tolerance = round(expected_depth * float(fraction), 6)
    deviations = tuple(
        math.hypot(found[0] - target[0], found[1] - target[1])
        for found, target in zip(actual[2:], expected[2:])
    )
    maximum = max(deviations)
    return {
        "passed": maximum <= tolerance,
        "verdict": (
            "FIXTURE_GEOMETRY_WITHIN_TOLERANCE"
            if maximum <= tolerance
            else "FIXTURE_GEOMETRY_OUT_OF_TOLERANCE"
        ),
        "expected_notch_depth_mm": round(expected_depth, 6),
        "tolerance_mm": tolerance,
        "maximum_point_deviation_mm": round(maximum, 6),
        "point_deviations_mm": [round(item, 6) for item in deviations],
    }


def evaluate_artifact_receipt(
    *,
    sdist_path: str | Path,
    wheel_path: str | Path,
    project_root: str | Path,
    build_isolation_verified: bool = True,
) -> BoundaryReceipt:
    """Create the build manifest receipt consumed by licenses."""
    root = Path(project_root)
    sdist = Path(sdist_path)
    wheel = Path(wheel_path)
    if not sdist.is_file() or not wheel.is_file():
        return unavailable(
            "build", "BUILD_PROVENANCE",
            "required sdist or wheel is absent; artifact provenance was not checked",
        )
    try:
        source_profile = (root / "fixtures" / "chip.dat").read_bytes()
        golden_bytes = (root / "fixtures" / "golden-profile.json").read_bytes()
        golden = json.loads(golden_bytes.decode("utf-8"))
        if not isinstance(golden, dict) or golden.get("schema") != "chipcup-golden-profile/v1":
            raise ValueError("golden profile schema is invalid")
        source_geometry = validate_notch_profile(source_profile, golden)
        sdist_profile = read_artifact_member(sdist, "fixtures/chip.dat")
        wheel_profile = read_artifact_member(wheel, "fixtures/chip.dat")
        sdist_golden = read_artifact_member(sdist, "fixtures/golden-profile.json")
        wheel_golden = read_artifact_member(wheel, "fixtures/golden-profile.json")
        golden_consistent = (
            json.loads(sdist_golden.decode("utf-8")) == golden
            and json.loads(wheel_golden.decode("utf-8")) == golden
        )
        geometries = {
            "source": source_geometry,
            "sdist": validate_notch_profile(sdist_profile, golden),
            "wheel": validate_notch_profile(wheel_profile, golden),
        }
        sdist_info = inspect_artifact(sdist)
        wheel_info = inspect_artifact(wheel)
        comparison = compare_artifacts(sdist_info, wheel_info)
        issues: list[str] = []
        if not comparison.passed:
            issues.append("sdist/wheel metadata, exports, or backend provenance differ")
        if not golden_consistent:
            issues.append("golden geometry reference differs across source and archives")
        for location, verdict in geometries.items():
            if not verdict["passed"]:
                issues.append(
                    f"{location} fixture notch exceeds {verdict['tolerance_mm']} mm tolerance"
                )
        evidence: dict[str, object] = {
            "version": sdist_info.version,
            "name": sdist_info.name,
            "sdist_sha256": sdist_info.sha256,
            "wheel_sha256": wheel_info.sha256,
            "sdist_members": list(sdist_info.members),
            "wheel_members": list(wheel_info.members),
            "license_expression": wheel_info.license_expression or "",
            "license_files": list(wheel_info.license_files),
            "top_level_names": list(wheel_info.top_level_names),
            "public_exports": {
                name: list(names) for name, names in wheel_info.public_exports.items()
            },
            "geometry": geometries,
            "golden_reference_consistent": golden_consistent,
            "build_backend": sdist_info.build_backend or "",
            "build_isolation_verified": build_isolation_verified,
        }
        if not build_isolation_verified:
            return BoundaryReceipt(
                "build", "BUILD_PROVENANCE", ReceiptState.UNVERIFIED,
                evidence, tuple(issues + [
                    "build isolation was unavailable; shipped artifacts were inspected but provenance is unverified"
                ]),
            )
        return BoundaryReceipt(
            "build", "BUILD_PROVENANCE",
            ReceiptState.FAIL if issues else ReceiptState.PASS,
            evidence, tuple(issues),
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        return BoundaryReceipt(
            "build", "BUILD_PROVENANCE", ReceiptState.FAIL, {},
            (f"{type(error).__name__}: {error}",),
        )


def close_version_cycle(
    build_receipt: BoundaryReceipt | None,
    version_receipt: BoundaryReceipt | None,
) -> BoundaryReceipt:
    """Close versions→build only when both upstream receipts are verified."""
    if build_receipt is None or version_receipt is None:
        return unavailable("build", "BUILD_RELEASE_IDENTITY", "version or build receipt is absent")
    if build_receipt.state is not ReceiptState.PASS or version_receipt.state is not ReceiptState.PASS:
        return unavailable(
            "build", "BUILD_RELEASE_IDENTITY",
            "upstream version or artifact evidence is not verified",
        )
    artifact_version = str(build_receipt.evidence.get("version", ""))
    installed_version = str(version_receipt.evidence.get("installed_version", ""))
    matches = bool(artifact_version and artifact_version == installed_version)
    return BoundaryReceipt(
        "build", "BUILD_RELEASE_IDENTITY",
        ReceiptState.PASS if matches else ReceiptState.FAIL,
        {"artifact_version": artifact_version, "installed_version": installed_version},
        () if matches else ("installed metadata version differs from built artifact version",),
    )


def degraded_receipt() -> BoundaryReceipt:
    return unavailable("build", "BUILD_PROVENANCE", "build inputs or provenance evidence are unavailable")
