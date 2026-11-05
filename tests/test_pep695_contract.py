from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest


def test_pep695_generic_syntax_is_exercised_on_python_312_plus():
    source = "class Box[T]:\n    value: T\n"
    if sys.version_info < (3, 12):
        pytest.skip("PEP 695 syntax is parsed by the Python 3.12+ CI lane")
    tree = ast.parse(source, feature_version=(3, 12))
    assert isinstance(tree.body[0], ast.ClassDef)
    assert tree.body[0].name == "Box"
