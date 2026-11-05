# Pre-python — chipcup

**Working direction: a Change Assurance Engine.** The project is exploring how to make material software changes carry an auditable record of their impact, required checks, evidence, policy evaluation, and unresolved risk.

The strategic direction is broader than the code that exists today. The current distribution and import package, **chipcup**, is a Python Alpha prototype for release-lifecycle checks. It is not yet a general change-assurance product.

## Product hypothesis

A pull request or release should not be judged by a single AI review, a green test badge, or an opaque score. The system should:
1. identify the exact source change and the subjects it can affect;
2. state the coverage and uncertainty of that impact analysis;
3. compile applicable policy into explicit verification obligations;
4. collect evidence from specialist tools and controlled test environments;
5. bind each result to exact source, artifact, environment, tool, and policy identities;
6. produce an explainable decision and preserve the evidence needed to replay it.

The resulting record is an **assurance case**, not a mathematical proof of program correctness.

## Why the scope is narrow

AI code review, multi-repository context, code graphs, security scanning, and predictive test selection are already active product areas. The opportunity is not to clone those systems. The differentiation hypothesis is the relationship between change impact, policy obligations, exact-subject evidence, build/release identity, and replayable decisions.

That hypothesis is not yet experimentally established. The first implementation target is a complete Python change-to-release workflow. Additional languages, runtime monitoring, hosted governance, universal graph infrastructure, and autonomous remediation are gated on evidence from that first vertical slice.

See [Product strategy](docs/PRODUCT_STRATEGY.md) and [Architecture review](docs/ARCHITECTURE_REVIEW.md).

## What exists today

**Reviewed source baseline:** main commit 7ef2c82fb2ebdf2e08376b154bd6e9f112b6a5ca, reviewed 2026-11-05.

The 0.1.0 Alpha source contains:
- a seven-boundary receipt experiment for build, licensing, types, markers, deprecations, imports, and versions;
- sdist and wheel inspection with selected metadata, package-name, and public-export comparisons;
- a measured chipped-teacup fixture whose 2.40 mm notch depth defines a 0.12 mm tolerance;
- marker and warning-observation inputs;
- a lazy CLI/runtime import boundary;
- pytest coverage, mypy checks, Python 3.10–3.14 CI, and native Ubuntu/Windows/macOS warning-observation jobs.

The current implementation does **not** yet provide a general change model, cross-release API history, complete archive file-hash parity, trusted provenance verification, append-only evidence history, a unified public execution path, a complete policy engine, or a comparative differentiation benchmark.

The teacup is a measured regression fixture, not the product identity or organizing metaphor.

## Current development snapshot

- Repository: https://github.com/Loofy147/Pre-python
- Python distribution/import name: chipcup
- Version in reviewed main: 0.1.0
- Maturity: Alpha
- [PR #5 — documentation and architecture review](https://github.com/Loofy147/Pre-python/pull/5): open, not merged; this branch updates its documentation.
- [PR #4 — stable exit-code proposal](https://github.com/Loofy147/Pre-python/pull/4): open and separate; its proposed contract requires reconciliation with current type-surface and policy semantics.

A passing CI run proves only the checks that actually ran for that commit. It does not prove the future product direction.

## Run the current prototype

From the repository root, using Python 3.10 or newer:

~~~bash
python -m pip install -e ".[test]"
python -m pytest
python -m mypy
python scripts/check_import_boundary.py
~~~

The current CLI accepts an sdist, wheel, marker matrix, warning-evidence input, project root, and version specifier. It emits a JSON receipt report. Its current exit behavior is documented in [CLI reference](docs/CLI_REFERENCE.md); the different mapping proposed in PR #4 is not part of reviewed main.

## Design constraints

- Evidence and policy outcomes remain separate from claims and final decisions.
- Unknown, stale, contradictory, incomplete, or untrusted evidence never becomes a verified pass.
- Static impact analysis reports its limits; no analyzer claims complete impact without a declared model and coverage evidence.
- AI can propose risks and remediations; it cannot create trust, waive mandatory rules, approve, merge, publish, or certify its own work.
- Candidate code and build hooks are untrusted input and run only in disposable restricted workers.
- Existing specialist tools are integrated before equivalent analyzers are reimplemented.
- No single score hides evidence, exceptions, or unresolved obligations.
- Every shipped capability must exist in code, tests, and reproducible evidence on a named commit.

## Documentation

Start at [the documentation index](docs/README.md).

- [Product strategy](docs/PRODUCT_STRATEGY.md)
- [Architecture review](docs/ARCHITECTURE_REVIEW.md)
- [First vertical-slice specification](docs/MVP_SPEC.md)
- [Change taxonomy](docs/CHANGE_TAXONOMY.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Evidence model](docs/EVIDENCE_MODEL.md)
- [Policy model](docs/POLICY_MODEL.md)
- [Integrations](docs/INTEGRATIONS.md)
- [Security model](docs/SECURITY.md)
- [Validation and benchmark](docs/VALIDATION_AND_BENCHMARK.md)
- [Roadmap and gates](docs/ROADMAP.md)
- [Status](docs/STATUS.md)
- [Open decisions](docs/OPEN_QUESTIONS.md)
- [ADR-0001: Change Assurance scope](docs/DECISIONS/ADR-0001-change-assurance-scope.md)
- [Python API reference](docs/API_REFERENCE.md)
- [CLI reference](docs/CLI_REFERENCE.md)

## Project principle

Pre-python should not become a pile of scanners, agents, or dashboards. It should become a small, reliable system that connects change impact, explicit obligations, independently collected evidence, and accountable decisions. Whether this is a defensible product must be demonstrated.
