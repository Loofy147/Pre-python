# chipcup

**Evidence-driven Python release assurance — research prototype / Alpha.**

The GitHub repository is named **Pre-python**; the Python distribution and import package are named **chipcup**.

chipcup is exploring a specific engineering problem: whether a Python distribution release satisfies its declared compatibility and release policy, with evidence tied to the source revision, build artifacts, supported environments, and release history.

The intended product is not another wheel checker. It is an **evidence coordinator and policy evaluator** that connects specialist tools and preserves why a release decision was made.

> **Status honesty:** the current repository is an Alpha prototype. It contains a working seven-boundary receipt experiment, but it does not yet implement the complete product described in the target architecture. In particular, cross-release API comparison, durable evidence history, independent provenance verification, a complete policy engine, and a comparative benchmark are not implemented.

## Why this problem matters

A release can pass its unit tests and still violate a compatibility promise. A public symbol may disappear without a warning window. A warning may be emitted on Linux but not on another supported platform. An sdist and wheel can have matching metadata but different implementation files. A release tag can identify a different version from the artifact it publishes.

Existing tools already solve important parts of this problem. chipcup should coordinate and connect their evidence rather than reimplement them:

- Griffe compares API snapshots and detects breaking changes.
- pydistcheck and related distribution tools inspect archive structure and portability.
- Twine checks whether distribution descriptions render correctly on PyPI.
- packaging implements Python version and environment marker semantics.
- SPDX publishes the authoritative license identifier data.
- PyPI attestations provide cryptographically verifiable publishing and build-provenance evidence.

The proposed improvement is the relationship between these facts: **which exact evidence supports each release claim, which policy evaluated it, and what remains unknown or contradictory?**

## Current implementation

The current CLI runs a receipt cycle:

    build → licenses → types → markers → deprecations → imports → versions → build-cycle-closure

The cycle has distinct receipt states: PASS, FAIL, UNVERIFIED, and NOT_APPLICABLE. Named verdicts use a closed AuditVerdict string enum. The teacup fixture is a load-bearing artifact: its measured notch depth is 2.40 mm and its five-percent tolerance is 0.12 mm. Source, sdist, and wheel copies are checked against a golden geometry reference.

Current mechanisms include:

- sdist and wheel metadata inspection;
- selected package-name and literal __all__ comparisons;
- fixture and golden-reference checks;
- License-File and supplemental LicenseRef coverage checks;
- stub-manifest and file-presence checks;
- PEP 440 version and PEP 508 marker evaluation;
- actual warning observations captured on native CI platforms;
- lazy CLI loading and static evaluator-import-boundary checks;
- unit tests, cross-version CI, native-platform CI, and an artifact audit.

These are real foundations, but their current limits matter. See [Status and implementation truth](docs/STATUS.md).

## What is not implemented yet

The current source must not be described as providing these capabilities:

- Griffe-based API diffing across Git tags or published releases;
- a persistent release-history or evidence ledger;
- proof that a caller-supplied build-isolation Boolean is true;
- verification of PyPI PEP 740 or SLSA attestations;
- complete source-to-sdist-to-wheel file-content equivalence;
- semantic checking that stub files match runtime contracts;
- a complete deprecation-removal decision based on multiple published releases;
- an authoritative, version-pinned SPDX license and exception identifier registry;
- installation and audit of the exact wheel produced from the sdist in a clean environment;
- a reusable GitHub Action or other CI integration product.

The current receipt cycle also coexists with a separate legacy evaluation path in gate.py. The project needs one authoritative execution architecture before it expands.

## Quick start: inspect the current prototype

Use Python 3.10 or newer. From a clone of this repository:

    python -m pip install -e ".[test]"
    python -m pytest
    python -m mypy
    python scripts/check_import_boundary.py

Build a source distribution and then build the wheel from that source distribution:

    python -m build --sdist --outdir dist
    python -m build --wheel dist/chipcup-0.1.0.tar.gz --outdir dist/wheel-from-sdist

Validate distribution descriptions:

    python -m twine check dist/*

Capture warning evidence on each required native platform. Run the following command separately on Linux, Windows, and macOS CI workers; the script identifies the current native platform:

    python scripts/capture_warning_evidence.py --release 0.1.0 --matrix fixtures/audit-matrix.json --output warning-evidence/native.json

Run the receipt audit after placing the native evidence JSON files in the warning-evidence directory:

    python -m chipcup.cli --sdist dist/chipcup-0.1.0.tar.gz --wheel dist/wheel-from-sdist/chipcup-0.1.0-py3-none-any.whl --matrix fixtures/audit-matrix.json --warning-evidence warning-evidence/ --project-root . --build-isolation-verified

The final flag is a **caller assertion**, not cryptographic proof. It tells the current prototype to treat build isolation as verified. Do not use that Boolean as a production provenance control.

The exact output paths depend on the build command and environment. Inspect the generated files rather than assuming a wheel filename.

## Product direction

The target architecture has six layers:

1. Release inputs: source revision, tags, policy, sdist, wheel, installed distribution, and published index records.
2. Evidence adapters: API diff, archive inspection, license validation, warning observations, version and marker evaluation, and attestation verification.
3. A versioned evidence model: stable subjects, digests, producer identity, timestamps, platform scope, and provenance.
4. A relationship engine: claims supported by, derived from, contradicted by, or superseded by evidence.
5. A policy evaluator: explicit, versioned rules with no hidden score or silent promotion of missing evidence.
6. A release decision: ALLOW, DENY, or APPROVAL_REQUIRED, accompanied by a reproducible explanation.

The evidence and policy layers are the intended differentiator. The current seven evaluators are implementation experiments, not a requirement that the finished product must retain exactly seven modules.

## Documentation

Start at [the documentation index](docs/README.md).

- [Status and implementation truth](docs/STATUS.md)
- [Python API reference](docs/API_REFERENCE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Evidence model](docs/EVIDENCE_MODEL.md)
- [Policy model](docs/POLICY_MODEL.md)
- [CLI reference](docs/CLI_REFERENCE.md)
- [Integrations and ecosystem boundaries](docs/INTEGRATIONS.md)
- [Security and trust model](docs/SECURITY.md)
- [Validation and comparative benchmark](docs/VALIDATION_AND_BENCHMARK.md)
- [Roadmap and release gates](docs/ROADMAP.md)
- [Design rationale](docs/DESIGN_RATIONALE.md)
- [Open decisions](docs/OPEN_QUESTIONS.md)

## Project status at the documentation review

The review snapshot is based on main commit 7ef2c82fb2ebdf2e08376b154bd6e9f112b6a5ca, dated 2026-11-05. The main-branch CI run 42054977699 completed successfully. An open pull request proposes a richer exit-code contract, but it is not part of that main commit and is not documented as shipped behavior here.

No GitHub Release or Git tag was present in the inspected repository snapshot. A passing CI run is evidence that the configured jobs passed for that commit; it is not proof that the broader target product is complete or that every adversarial case is covered.

## Development stage

The package metadata classifies chipcup as Alpha. Treat it as an experimental engineering project, not as a production release gate. The project should not claim a unique market or technical advantage until the comparative benchmark in docs/VALIDATION_AND_BENCHMARK.md demonstrates incremental defect detection against an explicit baseline toolchain.
