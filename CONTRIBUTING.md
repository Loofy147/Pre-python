# Contributing

## Project principle

Contributions must improve correctness, evidence quality, reproducibility, or practical adoption. Do not add a module solely to extend the seven-boundary taxonomy.

Keep current implementation separate from target design. Documentation, comments, tests, and release notes must not advertise a planned capability as already shipped.

## Local checks

    python -m pip install -e ".[test]"
    python -m pytest
    python -m mypy
    python scripts/check_import_boundary.py
    python -m build --sdist
    python -m twine check dist/*

The CI workflow contains additional cross-version, native-platform, warning-evidence, and build-audit steps. Run the applicable checks for the files you change.

## Boundary rules

- Keep evaluator logic isolated behind explicit contracts; do not create import-time evaluator cycles.
- Prefer one authoritative orchestration path. Changes to runtime.py and gate.py must preserve or deliberately migrate the public behavior.
- Keep evidence, claim status, receipt state, and release decision as separate concepts.
- Missing, stale, contradictory, or untrusted evidence must not become PASS.
- A digest proves content identity, not origin. Caller-supplied Booleans are assertions, not provenance.
- Never inspect an untrusted archive by extracting it into a shared working directory.
- Execute candidate package code only in a disposable, restricted environment.
- Validate SPDX identifiers against an explicitly versioned authoritative list.
- Bind every observation to its exact source, release, artifact, platform, and policy scope.
- Add a failing adversarial test before repairing a false-pass path.
- Keep raw evidence and normalized results linked; do not discard the original finding.

## Evidence requirement for a change

A substantive change should include:

1. the claim being improved;
2. the source or mechanism governing the claim;
3. an explicit failure mode or counterexample;
4. tests that reproduce the failure and prove the correction;
5. the CI or artifact evidence that re-checks the result;
6. updated documentation and limitations.

A passing test must not be used to claim broader properties that the test does not cover.

## Release changes

Use PEP 440 versions. The repository's own deprecation period is a project policy and must be explicitly configured; do not describe it as a requirement imposed by PEP 387.

The release workflow must validate tag/version identity, build from the reviewed source, install/audit the exact produced artifacts in a clean environment, and verify provenance before publishing. The current workflow does not yet satisfy every part of this target contract.

See docs/README.md for the documentation index and docs/STATUS.md for the implementation truth.
