from __future__ import annotations

import builtins
import json
from pathlib import Path

from chipcup.cli import main
from chipcup.exit_codes import ExitCode


def test_missing_runtime_module_returns_a_dedicated_exit_code(
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
        if name == "chipcup.runtime":
            raise ModuleNotFoundError("No module named 'chipcup.runtime'")
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
    assert code == int(ExitCode.MODULE_NOT_FOUND)
    assert payload["failure"] == "module-not-found"


def test_cli_returns_selected_receipt_exit_code(monkeypatch, capsys, tmp_path):
    import chipcup.runtime

    report = {
        "passed": False,
        "receipts": {
            name: {"state": "PASS", "evidence": {}, "issues": []}
            for name in (
                "build", "licenses", "types", "markers", "deprecations",
                "imports", "versions", "build_cycle_closure",
            )
        },
    }
    report["receipts"]["deprecations"] = {
        "state": "FAIL", "evidence": {}, "issues": ["warning missing"]
    }
    report["receipts"]["build"] = {
        "state": "FAIL", "evidence": {}, "issues": ["wheel metadata differs"]
    }
    monkeypatch.setattr(chipcup.runtime, "run_receipt_cycle", lambda **_: report)

    matrix = tmp_path / "matrix.json"
    matrix.write_text("[]", encoding="utf-8")
    warnings = tmp_path / "warnings.json"
    warnings.write_text("[]", encoding="utf-8")

    code = main(
        [
            "--sdist", str(tmp_path / "chipcup.tar.gz"),
            "--wheel", str(tmp_path / "chipcup.whl"),
            "--matrix", str(matrix),
            "--warning-evidence", str(warnings),
        ]
    )

    printed = json.loads(capsys.readouterr().out)
    assert printed == report
    assert code == int(ExitCode.BUILD_DIVERGENT)
