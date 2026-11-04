"""Console entry point for the chipcup distribution audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping, Sequence, cast

from chipcup.deprecations import WarningObservation
from chipcup.gate import GateRequest, evaluate_release
from chipcup.markers import MarkerRow


def _string(
    values: Mapping[str, object], key: str, default: str | None = None
) -> str:
    value = values.get(key, default)
    if not isinstance(value, str):
        raise ValueError(f"matrix field {key!r} must be a string")
    return value


def _environment(values: Mapping[str, object]) -> Mapping[str, str]:
    raw = values.get("environment", {})
    if not isinstance(raw, dict):
        raise ValueError("matrix environment must be an object")
    result: dict[str, str] = {}
    for key, value in cast(Mapping[object, object], raw).items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("matrix environment keys and values must be strings")
        result[key] = value
    return result


def load_matrix(path: Path) -> tuple[MarkerRow, ...]:
    decoded: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(decoded, list):
        raise ValueError("marker matrix must be a JSON array")
    rows: list[MarkerRow] = []
    for raw in cast(list[object], decoded):
        if not isinstance(raw, dict):
            raise ValueError("each marker matrix row must be an object")
        values = cast(Mapping[str, object], raw)
        extra_value = values.get("extra")
        if extra_value is not None and not isinstance(extra_value, str):
            raise ValueError("matrix extra must be a string when supplied")
        rows.append(
            MarkerRow(
                name=_string(values, "name"),
                expression=_string(values, "expression"),
                stub_set=_string(values, "stub_set"),
                version_specifier=_string(values, "version_specifier", ">=0"),
                environment=_environment(values),
                extra=extra_value,
            )
        )
    return tuple(rows)


def load_warning_observations(path: Path) -> tuple[WarningObservation, ...]:
    files = sorted(path.glob('*.json')) if path.is_dir() else [path]
    observations: list[WarningObservation] = []
    for item in files:
        decoded: object = json.loads(item.read_text(encoding='utf-8'))
        values = decoded if isinstance(decoded, list) else [decoded]
        for raw in cast(list[object], values):
            if not isinstance(raw, dict):
                raise ValueError(f'warning evidence in {item} must contain JSON objects')
            record = cast(Mapping[str, object], raw)
            release = _string(record, 'release')
            row = _string(record, 'matrix_row')
            platform = _string(record, 'platform')
            selected = record.get('marker_selected')
            emitted = record.get('emitted')
            count = record.get('warning_count')
            if not isinstance(selected, bool) or not isinstance(emitted, bool):
                raise ValueError('warning evidence selection and emission fields must be Boolean')
            if not isinstance(count, int) or count < 0:
                raise ValueError('warning_count must be a non-negative integer')
            observations.append(WarningObservation(release, row, selected, emitted, count, platform))
    return tuple(observations)

def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chipcup.audit",
        description="Audit the public API and release metadata of a Python distribution.",
    )
    parser.add_argument("--sdist", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, default=Path("fixtures/audit-matrix.json"))
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--warning-evidence", type=Path, required=True, help="JSON file or directory of native-platform warning observations")
    parser.add_argument(
        "--version-specifier", default=">=0.1.0,<1.0.0",
        help="PEP 440 specifier required for the installed distribution",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        rows = load_matrix(args.matrix)
        report = evaluate_release(
            GateRequest(
                sdist_path=args.sdist,
                wheel_path=args.wheel,
                project_root=args.project_root,
                version_specifier=args.version_specifier,
                marker_rows=rows,
                warning_observations=load_warning_observations(args.warning_evidence),
            )
        )
    except ModuleNotFoundError as error:
        print(json.dumps({
            "passed": False,
            "failure": "module-not-found",
            "message": str(error),
        }, indent=2))
        return 3
    except Exception as error:
        print(json.dumps({
            "passed": False,
            "failure": "audit-error",
            "message": f"{type(error).__name__}: {error}",
        }, indent=2))
        return 1

    print(json.dumps(report.to_dict(), indent=2, default=str))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
