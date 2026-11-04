import importlib
import sys

import chipcup
from chipcup.imports import audit_module, discover_compatible_entry_points, load_module


def test_root_exports_are_lazy_and_resolve(monkeypatch):
    monkeypatch.delattr(chipcup, "parse_version", raising=False)
    assert "parse_version" not in chipcup.__dict__
    assert str(chipcup.parse_version("1.2rc1")) == "1.2rc1"
    assert "parse_version" not in chipcup.__dict__
    assert chipcup.parse_version is chipcup.parse_version


def test_module_identity_is_first_import_wins():
    first = load_module("chipcup.versions")
    second = load_module("chipcup.versions")

    assert first is second
    assert audit_module("chipcup.versions").same_object_on_repeat_import


def test_pep420_plugins_namespace_exists():
    spec = importlib.util.find_spec("chipcup.plugins")
    assert spec is not None
    assert spec.origin is None
    assert spec.submodule_search_locations is not None


def test_pep420_namespace_search_path_order_and_submodule_shadowing(
    tmp_path, monkeypatch
):
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    (first_root / "chipcup_probe").mkdir(parents=True)
    (second_root / "chipcup_probe").mkdir(parents=True)
    (first_root / "chipcup_probe" / "choice.py").write_text(
        "VALUE = 'first'\n", encoding="utf-8"
    )
    (second_root / "chipcup_probe" / "choice.py").write_text(
        "VALUE = 'second'\n", encoding="utf-8"
    )

    monkeypatch.syspath_prepend(str(second_root))
    monkeypatch.syspath_prepend(str(first_root))
    namespace = importlib.import_module("chipcup_probe")
    selected = importlib.import_module("chipcup_probe.choice")

    assert namespace.__spec__.origin is None
    assert selected.VALUE == "first"
    assert selected is sys.modules["chipcup_probe.choice"]


def test_entry_point_discovery_does_not_import_plugin():
    found = discover_compatible_entry_points()
    demo = next(item for item in found if item.name == "demo")
    assert demo.value == "chipcup.plugins.demo:DemoPlugin"
    assert callable(demo.load)
