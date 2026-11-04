"""Import identity and lazy entry-point discovery (Python import machinery)."""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass, field
from importlib.metadata import EntryPoint, entry_points
from types import ModuleType


@dataclass(frozen=True, slots=True)
class ModuleIdentity:
    name: str
    object_id: int
    origin: str | None
    is_namespace: bool


@dataclass(frozen=True, slots=True)
class EntryPointRef:
    group: str
    name: str
    value: str
    distribution_version: str | None
    _entry_point: EntryPoint = field(repr=False, compare=False)

    def load(self) -> object:
        """Import the plugin only when the caller explicitly loads it."""
        return self._entry_point.load()


def load_module(name: str) -> ModuleType:
    """Load a module by canonical import name."""
    return importlib.import_module(name)


def module_identity(name: str) -> ModuleIdentity:
    """Return the current sys.modules identity without importing the module."""
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
        is_namespace=origin is None and locations is not None,
    )


def assert_module_identity(name: str, expected: ModuleType) -> ModuleIdentity:
    actual = sys.modules.get(name)
    if actual is not expected:
        raise ImportError(f"module identity for {name!r} changed after import")
    return module_identity(name)


def discover_compatible_entry_points(
    group: str = "chipcup.plugins",
    version_specifier: str = ">=0",
) -> tuple[EntryPointRef, ...]:
    """Find compatible plugins without importing their target modules."""
    from chipcup.versions import VersionPolicy

    policy = VersionPolicy(version_specifier)
    selected = entry_points().select(group=group)
    refs: list[EntryPointRef] = []
    for point in selected:
        distribution = point.dist
        version = distribution.version if distribution is not None else None
        if version is not None and policy.accepts(version):
            refs.append(
                EntryPointRef(
                    group=group,
                    name=point.name,
                    value=point.value,
                    distribution_version=version,
                    _entry_point=point,
                )
            )
    return tuple(sorted(refs, key=lambda item: item.name))
