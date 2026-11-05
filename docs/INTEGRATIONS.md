# Integrations and ecosystem boundaries

## Principle

Coordinate specialist evidence; do not clone every specialist tool. A command that runs is not a complete adapter. It must bind output to exact subjects, preserve raw results, validate output, and expose limitations.

## Existing tools and standards

| Tool / standard | Existing responsibility | Proposed role | Current chipcup status |
|---|---|---|---|
| Griffe | Python API inspection and snapshot comparison | Base/candidate API compatibility evidence | NOT IMPLEMENTED |
| packaging | PEP 440 and PEP 508 semantics | Deterministic version and marker semantics | USED |
| pytest | Python test execution | Test result and environment evidence | USED IN CI |
| mypy | Static type checking | Development quality evidence, not a substitute for API/runtime analysis | USED IN CI |
| pydistcheck | Distribution structure and portability checks | Archive-quality evidence | NOT IMPLEMENTED |
| Twine | Distribution-description rendering check | Keep its narrow validation result | USED IN CI |
| SPDX License List | Versioned license and exception identifier data | Pinned identifier validation | PARTIAL CUSTOM PARSER; NO AUTHORITATIVE LIST PIN |
| PyPI PEP 740 / Integrity API | Published artifact attestations | Verify subject, issuer, publisher/workflow, predicate | NOT IMPLEMENTED |
| SLSA provenance | Source/build provenance model | Verify build inputs, builder, source, and output subject | NOT IMPLEMENTED |
| GitHub Actions | CI jobs, matrix, artifacts, workflow identity | First CI provider adapter | REPOSITORY WORKFLOW ONLY |
| GitHub CodeQL / code scanning | Security and quality findings on pull requests | Import SARIF/native check evidence | NOT IMPLEMENTED |
| OpenTelemetry | Vendor-neutral telemetry instrumentation | Possible runtime evidence later | DEFERRED |
| GUAC | Software supply-chain metadata graph | Optional external relationship source later | DEFERRED |

## Adjacent capabilities — do not clone

Public documentation review on 2026-11-05 identified:
- GitHub Copilot, Qodo, and Graphite in AI PR review and suggestions;
- Sourcegraph in code graphs and code context;
- Launchable in predictive test selection;
- GitHub CodeQL/code scanning in PR security findings;
- GUAC in supply-chain relationships.

This is not an independent performance study or exhaustive competitive review. It is sufficient to reject these categories as standalone product differentiation until benchmarking demonstrates otherwise.

References:
- https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/copilot-code-review
- https://docs.github.com/en/code-security/concepts/code-scanning/code-scanning-on-pull-requests
- https://www.qodo.ai/formerly-qodo-merge/
- https://www.graphite.com/docs/ai-reviews
- https://help.launchableinc.com/features/predictive-test-selection/
- https://sourcegraph.com/docs/cody/core-concepts/code-graph
- https://docs.guac.sh/guac/
- https://slsa.dev/spec/v1.2/tracks

## Adapter priorities

### Priority 0 — subject and evidence contracts

Define repository/commit/artifact identity and the versioned evidence envelope before adding analyzers. Every integration depends on these contracts.

### Priority 1 — Python vertical slice

1. Griffe for base/candidate API snapshots.
2. Python package/build inspectors for source, sdist, and wheel manifests.
3. packaging for version and marker semantics.
4. pytest and mypy results with environment identity.
5. Twine description-rendering result with its exact scope.
6. Version-pinned SPDX License List validation.
7. PyPI PEP 740/SLSA provenance verification where source/publisher supports it.

### Priority 2 — CI and security findings

- GitHub workflow/run/job identity;
- native matrix observations;
- CodeQL or existing security scanner outputs;
- SARIF/native check ingestion where available;
- GitHub check/status publication bound to exact commit.

### Deferred

- Launchable-style test prioritization;
- GUAC ingestion or graph federation;
- OpenTelemetry/runtime correlation;
- other SCM/CI providers;
- second-language analyzers.

## Adapter contract

Every adapter declares:
- adapter ID/version;
- supported evidence schema versions;
- supported languages, artifacts, and environments;
- required input subjects;
- normalized invocation/configuration digest;
- producer identity and tool version/container digest;
- output schema and normalization version;
- raw output digest and durable reference;
- findings and completeness state;
- timeout, resource, retry, and failure semantics;
- known limitations and unsupported cases.

Adapter outputs are evidence; they do not own final policy or approval.

## Integration acceptance tests

Each adapter must test valid positive output, findings, malformed output, wrong-subject output, stale/replayed output, unavailable/timeout/error, incomplete scan, deterministic replay, and raw/normalized digest consistency.

“No findings” is distinct from a failed, timed-out, or partial scan.

## Build-versus-integrate rule

Implement a new analyzer only when a required use case is not covered by established tools, the gap is demonstrated by counterexample or benchmark, the project can define a testable semantic contract, ongoing maintenance is justified, and the output can participate in the evidence model without overstating certainty.
