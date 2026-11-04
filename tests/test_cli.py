from __future__ import annotations

import builtins
import json
from pathlib import Path

from chipcup.cli import main


def test_missing_gate_module_returns_exit_code_three(
    monkeypatch, capsys, tmp_path: Path
):
    original_import = builtins.__import__

    def import_without_gate(
        name: str,
        globals: object = None,
        locals: object = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> object:
        if name == "chipcup.gate":
            raise ModuleNotFoundError("No module named 'chipcup.gate'")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_without_gate)

    code = main(
        [
            "--sdist",
            str(tmp_path / "chipcup.tar.gz"),
            "--wheel",
            str(tmp_path / "chipcup.whl"),
            "--warning-evidence",
            str(tmp_path / "warnings"),
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert code == 3
    assert payload["failure"] == "module-not-found"
