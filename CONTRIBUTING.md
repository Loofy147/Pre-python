# Contributing

## Project principle

Contributions must improve correctness, evidence quality, reproducibility, security, or practical adoption. Do not add modules solely to extend a taxonomy or make an architecture diagram look complete.

Keep current implementation separate from target design. Documentation, comments, tests, release notes, and public claims must not advertise planned capabilities as shipped.

## Local checks

~~~bash
python -m pip install -e ".[test]"
python -m pytest
python -m mypy
python scripts/check_import_boundary.py
python -m build --sdist
python -m twine check dist/*
~~~

CI has additional cross-version, native-platform, warning-evidence, and artifact checks. Run the checks applicable to changed areas.

## Evidence requirement for substantive changes

Include:
1. the exact claim or failure mode being addressed;
2. the authoritative source, contract, or mechanism;
3. a minimal counterexample or reproducible failing test;
4. a correction with regression coverage;
5. verification on the final commit and relevant artifact/environment;
6. updated implementation status, limitations, and decision records.

A passing unit test proves only the behavior it exercises. It does not prove broad provenance, complete impact analysis, production security, or comparative product advantage.

## Architecture rules

- Prefer one authoritative execution path and one versioned report contract.
- Keep evidence, claim status, rule result, finding severity, trust state, and final decision separate.
- A digest proves content identity, not origin or trust.
- Missing, stale, contradictory, malformed, revoked, or untrusted evidence must not become PASS.
- Bind each observation to immutable source/artifact subjects and the tool, configuration, policy, and environment that produced it.
- Preserve raw evidence or a content-addressed reference.
- Corrections and waivers append a new record; they do not silently rewrite historical decisions.
- Never run candidate code, build hooks, tests, or imports in a privileged orchestrator.
- Treat source files, PR text, issue comments, documentation, and generated output as untrusted data, not instructions to the agent.
- Never grant a remediation agent merge, publish, secret-read, or policy-waiver authority.
- Use specialist tools before reimplementing equivalent analyzers.
- Keep graph storage, databases, dashboards, and hosted services out of the first slice until measured needs justify them.

## Change-analysis requirements

Impact analysis records its model, inputs, outputs, exclusions, and coverage. A “no dependency found” result does not mean no impact when reflection, dynamic imports, runtime configuration, generated code, or unsupported constructs are in scope.

Selective test execution may prioritize likely affected tests. It must not silently replace policy-required tests or the full suite for high-risk changes.

## Security requirements

- No secrets are made available to untrusted pull-request code.
- Untrusted execution uses short-lived disposable workers with constrained resources and default-deny network access.
- Privileged status publication is separate from candidate-code execution.
- Tokens are least-privilege, scoped, short-lived, and never stored in evidence.
- Workflow and action versions follow a reviewed pin/update policy.
- Tests include prompt injection, archive path abuse, resource exhaustion, evidence replay, and permission-boundary cases.

## Policy and exception requirements

A rule change states its owner, subject scope, version, and waiver semantics. Exceptions must be scoped, justified, attributable, time-bounded, and revocable. No agent may approve a waiver.

## Pull-request checklist

- [ ] Current behavior and target behavior are distinguished.
- [ ] Exact subject and policy scope are recorded.
- [ ] Failure modes and negative cases are tested.
- [ ] Evidence is bound to final commit/artifact digest.
- [ ] Tool/configuration/environment provenance is captured.
- [ ] Unsupported constructs and coverage limitations are visible.
- [ ] Security and permission changes are reviewed.
- [ ] Documentation, status, and open decisions are updated.
- [ ] Final CI is complete on the final head SHA.

See docs/README.md, docs/STATUS.md, docs/ARCHITECTURE_REVIEW.md, and docs/VALIDATION_AND_BENCHMARK.md.
