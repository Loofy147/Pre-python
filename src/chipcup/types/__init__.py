"""Typed public API contracts and matrix-selected structural stub checks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Protocol, TypeVar, runtime_checkable
from types import ModuleType

if TYPE_CHECKING:
    from chipcup.build import BuildEvidence

__all__ = [
    "AuditReceipt",
    "BuildEvidence",
    "Reader",
    "TypeAuditResult",
    "accepts_protocol",
    "audit_public_surface",
    "audit_stub_sets",
    "is_any",
    "prepare_build_receipt",
]

T_co = TypeVar("T_co", covariant=True)


class Reader(Protocol[T_co]):
    def read(self) -> T_co:
        """Return a value without mutating the reader."""


@runtime_checkable
class AuditReceipt(Protocol):
    @property
    def source_digest(self) -> str:
        ...

    @property
    def passed(self) -> bool:
        ...


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


def __getattr__(name: str) -> object:
    """PEP 562 lazy re-export that breaks the types/build import-time cycle."""
    if name == "BuildEvidence":
        from chipcup.build import BuildEvidence

        globals()[name] = BuildEvidence
        return BuildEvidence
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def accepts_protocol(candidate: object, protocol: type[object]) -> bool:
    try:
        return isinstance(candidate, protocol)
    except TypeError:
        return False


def is_any(annotation: object) -> bool:
    return annotation is Any


def audit_stub_sets(selected: tuple[str, ...]) -> tuple[str, ...]:
    """Return unknown stub-set names; importing each set also verifies its shape."""
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
    return TypeAuditResult(
        selected_stub_sets=selected_stub_sets,
        unknown_stub_sets=audit_stub_sets(selected_stub_sets),
        typed_public_names=typed_names,
        missing_wheel_exports=missing,
        reader_is_covariant=bool(T_co.__covariant__),
    )


def prepare_build_receipt(receipt: object) -> BuildEvidence:
    """Resolve BuildEvidence through this module's PEP 562 __getattr__."""
    if not isinstance(receipt, AuditReceipt):
        raise TypeError("receipt does not satisfy the AuditReceipt protocol")
    from chipcup.types import BuildEvidence
    from chipcup.build import accept_type_receipt

    evidence = accept_type_receipt(receipt)
    if not isinstance(evidence, BuildEvidence):
        raise TypeError("build returned an invalid BuildEvidence value")
    return evidence
