import chipcup


def test_root_exports_are_lazy_and_resolve():
    assert "parse_version" not in chipcup.__dict__
    assert str(chipcup.parse_version("1.2rc1")) == "1.2rc1"
    assert "parse_version" in chipcup.__dict__


def test_pep420_plugins_namespace_exists():
    import importlib.util

    spec = importlib.util.find_spec("chipcup.plugins")
    assert spec is not None
    assert spec.origin is None
    assert spec.submodule_search_locations is not None


def test_entry_point_discovery_does_not_import_plugin():
    from chipcup.imports import discover_compatible_entry_points

    found = discover_compatible_entry_points()
    demo = next(item for item in found if item.name == "demo")
    assert demo.value == "chipcup.plugins.demo:DemoPlugin"
    assert callable(demo.load)
