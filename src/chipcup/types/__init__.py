"""Typing judgments: nominal and structural contracts plus explicit Any checks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from chipcup.build import BuildEvidence

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


def accepts_protocol(candidate: object, protocol: type[object]) -> bool:
    try:
        return isinstance(candidate, protocol)
    except TypeError:
        return False


def is_any(annotation: object) -> bool:
    return annotation is Any


def prepare_build_receipt(receipt: object) -> BuildEvidence:
    if not isinstance(receipt, AuditReceipt):
        raise TypeError("receipt does not satisfy the AuditReceipt protocol")
    from chipcup.build import accept_type_receipt

    return accept_type_receipt(receipt)
