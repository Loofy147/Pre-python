"""Typed public API contracts and matrix-selected structural stub checks."""

from __future__ import annotations

from dataclasses import dataclass
from types import ModuleType
import json
from pathlib import Path
from typing import Any, Mapping, Protocol, TypeVar, runtime_checkable

from chipcup._contracts import (
    AuditReceipt, AuditVerdict, BoundaryReceipt, BuildEvidence, ReceiptState, unavailable,
)

__all__ = [
    "AuditReceipt",
    "BuildEvidence",
    "Reader",
    "TypeAuditResult",
    "accepts_protocol",
    "audit_public_surface",
    "audit_stub_sets",
    "is_any",
    "load",
    "prepare_build_receipt",
    "degraded_type_receipt",
    "receipt_from_license",
]

T_co = TypeVar("T_co", covariant=True)


class Reader(Protocol[T_co]):
    def read(self) -> T_co:
        """Return a value without mutating the reader."""


@runtime_checkable
class PosixStubContract(Protocol):
    def read_bytes(self, count: int = -1) -> bytes:
        ...


@runtime_checkable
class WindowsStubContract(Protocol):
    def read_text(self, encoding: str = "utf-8") -> str:
        ...


@dataclass(frozen=True, slots=True)
class TypeAuditResult:
    selected_stub_sets: tuple[str, ...]
    loaded_stub_contracts: Mapping[str, tuple[str, ...]]
    unknown_stub_sets: tuple[str, ...]
    typed_public_names: Mapping[str, tuple[str, ...]]
    missing_wheel_exports: Mapping[str, tuple[str, ...]]
    reader_is_covariant: bool

    @property
    def passed(self) -> bool:
        return (
            not self.unknown_stub_sets
            and not any(self.missing_wheel_exports.values())
            and self.reader_is_covariant
        )


STUB_SETS: Mapping[str, tuple[type[object], ...]] = {
    "base": (AuditReceipt, Reader),
    "posix": (PosixStubContract, Reader),
    "windows": (WindowsStubContract, Reader),
    "gpu": (AuditReceipt, Reader),
}


def accepts_protocol(candidate: object, protocol: type[object]) -> bool:
    try:
        return isinstance(candidate, protocol)
    except TypeError:
        return False


def is_any(annotation: object) -> bool:
    return annotation is Any


def load(stub_set: str) -> tuple[type[object], ...]:
    """Load the actual protocol contracts selected by a PEP 508 matrix row."""
    try:
        return STUB_SETS[stub_set]
    except KeyError as error:
        raise ValueError(f"unknown chipcup stub set {stub_set!r}") from error


def audit_stub_sets(selected: tuple[str, ...]) -> tuple[str, ...]:
    """Return unknown stub-set names selected by the evaluated marker matrix."""
    return tuple(name for name in selected if name not in STUB_SETS)


def audit_public_surface(
    modules: Mapping[str, ModuleType],
    wheel_exports: Mapping[str, tuple[str, ...]],
    selected_stub_sets: tuple[str, ...],
) -> TypeAuditResult:
    typed_names: dict[str, tuple[str, ...]] = {}
    missing: dict[str, tuple[str, ...]] = {}
    for module_name, module in modules.items():
        names = tuple(getattr(module, "__all__", ()))
        typed_names[module_name] = names
        artifact_names = set(wheel_exports.get(module_name, ()))
        missing[module_name] = tuple(name for name in names if name not in artifact_names)
    loaded_contracts = {
        name: tuple(contract.__name__ for contract in load(name))
        for name in selected_stub_sets
        if name in STUB_SETS
    }
    return TypeAuditResult(
        selected_stub_sets=selected_stub_sets,
        loaded_stub_contracts=loaded_contracts,
        unknown_stub_sets=audit_stub_sets(selected_stub_sets),
        typed_public_names=typed_names,
        missing_wheel_exports=missing,
        reader_is_covariant=_reader_is_covariant(),
    )


def _reader_is_covariant() -> bool:
    parameters: object = getattr(Reader, "__parameters__", ())
    if not isinstance(parameters, tuple) or not parameters:
        return False
    return bool(getattr(parameters[0], "__covariant__", False))


def prepare_build_receipt(receipt: object) -> BuildEvidence:
    """Validate a structural receipt using only the neutral contract."""
    if not isinstance(receipt, AuditReceipt):
        raise TypeError("receipt does not satisfy the AuditReceipt protocol")
    digest = receipt.source_digest
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("source_digest must be a 64-character SHA-256 digest")
    try:
        int(digest, 16)
    except ValueError as error:
        raise ValueError("source_digest is not hexadecimal") from error
    if receipt.passed is not True:
        raise ValueError("failed type audit cannot enter the build boundary")
    return BuildEvidence(source_digest=digest.lower(), passed=True)


def receipt_from_license(
    license_receipt: BoundaryReceipt | None,
    *,
    root: str | Path,
) -> BoundaryReceipt:
    """Accept stub contracts only when their files are licensed and shipped."""
    if license_receipt is None or license_receipt.state is not ReceiptState.PASS:
        return unavailable(
            "types", AuditVerdict.TYPE_SURFACE,
            "verified license receipt is absent; stub contract scope is unverified",
        )
    manifest_path = Path(root) / "src" / "chipcup" / "stub-contracts.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or manifest.get("schema") != "chipcup-stub-contracts/v1":
            raise ValueError("stub contract manifest has an invalid schema")
        sets = manifest.get("contract_sets")
        if not isinstance(sets, dict) or not sets:
            raise ValueError("stub contract manifest has no contract sets")
        raw_wheel_members = license_receipt.evidence.get("wheel_members")
        if not isinstance(raw_wheel_members, list):
            raise ValueError("license receipt has no wheel manifest")
        wheel_members = set(str(item) for item in raw_wheel_members)
        contracts: dict[str, list[str]] = {}
        missing: list[str] = []
        for name, paths in sets.items():
            if not isinstance(name, str) or not isinstance(paths, list):
                raise ValueError("stub contract entries must be arrays of paths")
            contracts[name] = []
            for raw_path in paths:
                if not isinstance(raw_path, str):
                    raise ValueError("stub contract path must be a string")
                package_path = "chipcup/" + raw_path.lstrip("/")
                if package_path not in wheel_members:
                    missing.append(package_path)
                if not (Path(root) / "src" / "chipcup" / raw_path).is_file():
                    missing.append("source:" + raw_path)
                contracts[name].append(package_path)
        if "chipcup/py.typed" not in wheel_members:
            missing.append("chipcup/py.typed")
        ok = not missing
        return BoundaryReceipt(
            "types", AuditVerdict.TYPE_SURFACE,
            ReceiptState.PASS if ok else ReceiptState.FAIL,
            {"contract_sets": contracts, "wheel_stub_files": sorted(wheel_members.intersection(
                path for paths in contracts.values() for path in paths
            ))},
            tuple("missing stub contract file: " + item for item in missing),
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        return BoundaryReceipt(
            "types", AuditVerdict.TYPE_SURFACE, ReceiptState.FAIL, {},
            (f"stub contract audit failed: {type(error).__name__}: {error}",),
        )


def degraded_type_receipt() -> BoundaryReceipt:
    return unavailable("types", AuditVerdict.TYPE_SURFACE, "license receipt or typed stub manifest is unavailable")
