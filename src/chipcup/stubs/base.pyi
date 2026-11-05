from typing import Protocol, TypeVar

T_co = TypeVar("T_co", covariant=True)

class Reader(Protocol[T_co]):
    def read(self) -> T_co: ...

class AuditReceipt(Protocol):
    @property
    def source_digest(self) -> str: ...
    @property
    def passed(self) -> bool: ...
