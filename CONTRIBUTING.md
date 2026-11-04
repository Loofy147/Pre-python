# Contributing

## Local checks

    python -m pip install -e ".[test]"
    python -m pytest
    python -m mypy
    python -m build
    python -m twine check dist/*

## Boundary rules

- Keep each formal system in its own subpackage.
- Cross-subpackage calls must be lazy function-level imports. Do not create sibling imports at module import time.
- Preserve the distinction between static typing and runtime protocol checks.
- Keep build metadata static unless a documented use case requires a dynamic field.
- A license expression and its declared license files must be validated separately.
- Deprecation schedules must be checked against published release history.
- Add a failing test before changing a boundary contract.

## Changes and releases

Use PEP 440 versions. A regular removal needs at least two distinct published minor releases between the first warning release and the removal release. Soft deprecations do not carry an automatic removal release.

The release workflow builds the sdist and wheel from a version tag and creates a GitHub Release with both artifacts.
