"""Import machinery audit: module identity, namespace search and entry points."""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass, field
from importlib.metadata import EntryPoint, entry_points
from types import ModuleType

from packaging.specifiers import SpecifierSet
from packaging.version import InvalidVersion, Version

from chipcup._contracts import AuditVerdict, BoundaryReceipt, ReceiptState, unavailable

__all__ = [
    "EntryPointRef",
    "ImportAudit",
    "ModuleIdentity",
    "assert_module_identity",
    "audit_module",
    "discover_compatible_entry_points",
    "load_module",
    "module_identity",
    "degraded_import_receipt",
    "receipt_from_deprecations",
]


@dataclass(frozen=True, slots=True)
class ModuleIdentity:
    name: str
    object_id: int
    origin: str | None
    namespace_locations: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ImportAudit:
    identity: ModuleIdentity
    same_object_on_repeat_import: bool
    public_names: tuple[str, ...]
    unresolved_public_names: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return self.same_object_on_repeat_import and not self.unresolved_public_names


@dataclass(frozen=True, slots=True)
class EntryPointRef:
    group: str
    name: str
    value: str
    distribution_version: str | None
    _entry_point: EntryPoint = field(repr=False, compare=False)

    def load(self) -> object:
        """Import the plugin only when explicitly requested by the caller."""
        return self._entry_point.load()


def load_module(name: str) -> ModuleType:
    """Import a module by its canonical name, honoring sys.modules caching."""
    return importlib.import_module(name)


def module_identity(name: str) -> ModuleIdentity:
    """Read the current module object recorded in sys.modules."""
    module = sys.modules.get(name)
    if module is None:
        raise ModuleNotFoundError(f"{name!r} is not present in sys.modules")
    spec = getattr(module, "__spec__", None)
    origin = getattr(spec, "origin", None)
    locations = getattr(spec, "submodule_search_locations", None)
    return ModuleIdentity(
        name=name,
        object_id=id(module),
        origin=origin,
        namespace_locations=tuple(str(item) for item in locations or ()),
    )


def assert_module_identity(name: str, expected: ModuleType) -> ModuleIdentity:
    actual = sys.modules.get(name)
    if actual is not expected:
        raise ImportError(f"module identity for {name!r} changed after import")
    return module_identity(name)


def audit_module(name: str) -> ImportAudit:
    """Verify first-import identity and resolve ordinary declared API names."""
    module = load_module(name)
    first = sys.modules[name]
    second = load_module(name)
    names = tuple(getattr(module, "__all__", ()))
    unresolved = tuple(
        item
        for item in names
        if item != "legacy_parse_version" and not hasattr(module, item)
    )
    identity = assert_module_identity(name, first)
    return ImportAudit(identity, first is second, names, unresolved)


def discover_compatible_entry_points(
    group: str = "chipcup.plugins",
    version_specifier: str = ">=0",
) -> tuple[EntryPointRef, ...]:
    """Filter entry points by distribution version without importing targets."""
    policy = SpecifierSet(version_specifier)
    refs: list[EntryPointRef] = []
    for point in entry_points().select(group=group):
        distribution = point.dist
        version = distribution.version if distribution is not None else None
        try:
            accepted = version is not None and policy.contains(Version(version))
        except InvalidVersion:
            accepted = False
        if accepted:
            refs.append(
                EntryPointRef(group, point.name, point.value, version, point)
            )
    return tuple(sorted(refs, key=lambda item: item.name))

def receipt_from_deprecations(
    deprecation_receipt: BoundaryReceipt | None,
    *,
    module_name: str = "chipcup",
) -> BoundaryReceipt:
    """Validate import identity only after the removal policy is verified."""
    if deprecation_receipt is None or deprecation_receipt.state is not ReceiptState.PASS:
        return unavailable(
            "imports", AuditVerdict.IMPORT_AUDIT,
            "deprecation policy receipt is absent or unresolved",
        )
    try:
        result = audit_module(module_name)
        evidence = {
            "module": module_name,
            "object_id": result.identity.object_id,
            "origin": result.identity.origin or "",
            "namespace_locations": list(result.identity.namespace_locations),
            "same_object_on_repeat_import": result.same_object_on_repeat_import,
            "public_names": list(result.public_names),
        }
        return BoundaryReceipt(
            "imports", AuditVerdict.IMPORT_AUDIT,
            ReceiptState.PASS if result.passed else ReceiptState.FAIL,
            evidence,
            tuple("unresolved public import name: " + item for item in result.unresolved_public_names),
        )
    except (ImportError, AttributeError, ModuleNotFoundError) as error:
        return BoundaryReceipt(
            "imports", AuditVerdict.IMPORT_AUDIT, ReceiptState.FAIL, {},
            (f"{type(error).__name__}: {error}",),
        )


def degraded_import_receipt() -> BoundaryReceipt:
    return unavailable("imports", AuditVerdict.IMPORT_AUDIT, "deprecation receipt or import target is unavailable")
