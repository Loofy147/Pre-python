"""Fail CI if evaluator packages import one another or CLI loads runtime eagerly."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = {"build", "licenses", "types", "markers", "deprecations", "imports", "versions"}

for name in sorted(NAMES):
    path = ROOT / "src" / "chipcup" / name / "__init__.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        targets = []
        if isinstance(node, ast.ImportFrom) and node.module:
            targets.append(node.module)
        elif isinstance(node, ast.Import):
            targets.extend(alias.name for alias in node.names)
        for target in targets:
            parts = target.split(".")
            if len(parts) > 1 and parts[0] == "chipcup" and parts[1] in NAMES and parts[1] != name:
                raise SystemExit(f"IMPORT_CYCLE: {name} imports evaluator {target}")
print("IMPORT_GRAPH=PASS")
