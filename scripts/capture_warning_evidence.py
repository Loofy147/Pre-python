"""Capture a deprecation warning on the current native CI platform."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Mapping, cast

import chipcup
from chipcup.deprecations import capture_warning_observation
from chipcup.markers import MarkerPolicy
from chipcup.versions import parse_version


_PLATFORM_ROWS = {
    "linux": "linux",
    "win32": "windows",
    "darwin": "macos",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", required=True)
    parser.add_argument("--matrix", type=Path, default=Path("fixtures/audit-matrix.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    row_name = _PLATFORM_ROWS.get(sys.platform)
    if row_name is None:
        raise SystemExit(f"unsupported native platform for warning evidence: {sys.platform}")

    rows: object = json.loads(args.matrix.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise SystemExit("marker matrix must be a JSON array")

    selected: Mapping[str, object] | None = None
    for raw in cast(list[object], rows):
        if isinstance(raw, dict) and raw.get("name") == row_name:
            selected = cast(Mapping[str, object], raw)
            break
    if selected is None:
        raise SystemExit(f"required marker row {row_name!r} is missing")

    expression = selected.get("expression")
    environment = selected.get("environment", {})
    if not isinstance(expression, str) or not isinstance(environment, dict):
        raise SystemExit("native marker row is malformed")
    env: dict[str, str] = {}
    for key, value in cast(Mapping[object, object], environment).items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise SystemExit("marker row environment must contain strings")
        env[key] = value

    extra = selected.get("extra")
    extras = (extra,) if isinstance(extra, str) else ()
    marker_selected = MarkerPolicy(expression, extras=extras).evaluate(env)
    observation = capture_warning_observation(
        args.release,
        row_name,
        marker_selected,
        lambda: getattr(chipcup, "legacy_parse_version"),
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(asdict(observation), indent=2) + "\n",
        encoding="utf-8",
    )
    if not observation.emitted:
        print(f"no DeprecationWarning observed for required row {row_name}")
        return 1
    print(f"warning evidence captured: {row_name} at {parse_version(args.release)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
