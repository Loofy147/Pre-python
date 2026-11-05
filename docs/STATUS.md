# Status and implementation truth

**Review snapshot:** 2026-11-05  
**Reviewed source branch:** main  
**Reviewed source commit:** 7ef2c82fb2ebdf2e08376b154bd6e9f112b6a5ca  
**Distribution version:** 0.1.0  
**Maturity:** Alpha

This document is the source of truth for current repository behavior and the state of the proposals. Target architecture documents do not change implementation status.

## 1. Repository evidence

| Item | Observed state |
|---|---|
| Repository | Loofy147/Pre-python |
| Default branch | main |
| Reviewed main commit | 7ef2c82fb2ebdf2e08376b154bd6e9f112b6a5ca |
| Main CI run | 42054977699, completed successfully |
| Python CI | 3.10–3.14 on Ubuntu |
| Native warning jobs | Ubuntu, Windows, macOS with Python 3.13 |
| Build audit | Builds sdist, wheel from sdist, runs Twine check, then current receipt cycle |
| GitHub Releases | None found at snapshot |
| Git tags | None found at snapshot |

Main CI proves only the jobs and tests configured for that commit.

## 2. Open pull requests

### PR #5 — documentation and architecture review

- URL: https://github.com/Loofy147/Pre-python/pull/5
- Base: main at 7ef2c82fb2ebdf2e08376b154bd6e9f112b6a5ca
- Previous reviewed head: 0560c36078e7c477f1a7e12958fb4c72932c044d
- State before this update: open, not merged, mergeable.
- Previous scope: documentation-only.
- CI run 42065922153 was queued at the previous head check. Test jobs and Ubuntu/Windows jobs had passed; macOS platform job was still queued.

This update adds documentation and must receive a new CI run. No claim is made here that the new head's CI has passed.

### PR #4 — stable exit-code proposal

- URL: https://github.com/Loofy147/Pre-python/pull/4
- Base: main at 7ef2c82fb2ebdf2e08376b154bd6e9f112b6a5ca
- Head commit: f3ac230a077f532d1dc3bf5edad022d7303653b1
- State at review: open, not merged, mergeable.
- CI run 42058135115: completed successfully for configured jobs.

Passing CI does not settle the public-contract concerns in ARCHITECTURE_REVIEW.md. The type-surface exit code must not imply semantic stub validation when the current subsystem primarily checks declarations and file presence. Fixture classification and precedence semantics also require review. PR #4 was not modified or merged by this documentation update.

## 3. Current capability register

| Capability | Status | Source-grounded statement |
|---|---|---|
| Seven-boundary receipt experiment | IMPLEMENTED, prototype | runtime.py composes build, licenses, types, markers, deprecations, imports, versions, and build-cycle closure |
| Closed verdict vocabulary | IMPLEMENTED | AuditVerdict is a string enum; BoundaryReceipt rejects unregistered verdict values |
| Measured teacup fixture | IMPLEMENTED, robustness defect | source, sdist, and wheel fixture copies are checked against golden profile and tolerance |
| Basic sdist/wheel comparison | PARTIAL | selected metadata, package names, literal public exports, and license metadata are compared |
| Complete source/sdist/wheel file parity | NOT IMPLEMENTED | no canonical hash comparison of every distributable package member |
| Custom SPDX expression parser | PARTIAL | handles a subset of expression grammar and LicenseRef mapping |
| Pinned authoritative SPDX identifiers | NOT IMPLEMENTED | no pinned SPDX License List validation |
| License file/subject coverage | PARTIAL | checks declared license files and configured subjects |
| Stub manifest/file presence | PARTIAL | checks configured declarations and presence; does not prove runtime semantic agreement |
| API snapshot comparison across releases | NOT IMPLEMENTED | no Griffe adapter or baseline snapshot store |
| Version/marker evaluation | IMPLEMENTED, prototype | uses packaging semantics |
| Native warning capture | IMPLEMENTED, limited | captures DeprecationWarning observations in native platform CI jobs |
| Warning evidence authenticity | NOT IMPLEMENTED | editable JSON is not independently authenticated or bound to trusted collector identity |
| Historical removal eligibility | NOT IMPLEMENTED end-to-end | CLI hardcodes published releases to 0.1.0 and uses a no-removal schedule |
| Durable evidence history | NOT IMPLEMENTED | evidence is file input/output, not append-only ledger |
| Independent provenance verification | NOT IMPLEMENTED | caller flag controls isolation assertion; no attestation verification |
| Exact installed-wheel audit | NOT IMPLEMENTED | CI does not install and audit the exact newly produced wheel in a clean environment |
| Unified execution path | INCONSISTENT | runtime.py receipt pipeline and gate.py GateRequest/GateReport remain separate |
| General change classification/impact | NOT IMPLEMENTED | no cross-file change model or coverage semantics |
| Policy-derived obligation compiler | NOT IMPLEMENTED | no deterministic target policy engine |
| Change Assurance Dossier | NOT IMPLEMENTED | no target evidence/decision schema in code |
| PR status-check product | NOT IMPLEMENTED | repository CI exists, not reusable product integration |
| Autonomous repair/runtime assurance | NOT IMPLEMENTED | no such product capability exists |

## 4. Current high-priority code defects

### P0 — Numeric and geometry input safety

Geometry parsing accepts invalid numeric forms including non-finite values and Boolean-as-number cases. Reject NaN, positive/negative infinity, booleans, invalid tolerance fractions, zero/negative dimensions, and malformed coordinates before arithmetic.

### P0 — Provenance false assurance

The direct artifact receipt API defaults build isolation to true, while the CLI flag defaults false. A caller assertion is not provenance verification. The API must fail closed and keep the assertion untrusted until a trusted attestation is verified.

### P0 — Dual execution paths

runtime.py and gate.py perform separate compositions and report formats. Select one authoritative path; migrate or retire the other with a tested compatibility policy.

### P1 — Artifact completeness

Metadata and public-export equality do not prove file-content parity. Define canonical path normalization, generated-file policy, archive limits, and hash comparison across source, sdist, and wheel.

### P1 — Exact artifact validation

Install and audit the exact wheel built from the sdist in a clean environment. Verify import origin, metadata, and tested behavior against that artifact.

### P1 — Type subsystem claims

The current stub manifest and file checks do not prove .pyi/runtime semantic agreement. The GPU stub/runtime contract mismatch is a concrete counterexample. Either remove the unsupported stub guarantee or implement and test semantic validation.

### P1 — Marker scope

Validate contract-set availability for selected marker rows, while separately checking policy-required matrix declarations. False marker rows must not be treated as active selections.

### P1 — Warning evidence trust

Reject inconsistent emitted/count fields, booleans as integers, duplicate observations, stale rows, and mismatched release/platform/commit identity. Capture and verify trusted CI identity.

### P1 — Release identity

The workflow accepts version-shaped tags but hardcodes 0.1.0 in build and evidence steps. Derive version from tag and require agreement with project metadata and artifacts before publication.

### P2 — SPDX authority

Pin authoritative SPDX License List data or return UNVERIFIED when identifier validation cannot be performed.

### P2 — Archive and execution hardening

Bound archive members, expanded size, paths, duplicate names, symlink behavior, and untrusted code execution. Add malicious-input tests.

## 5. Target architecture status

The proposed Change Assurance Engine is a design hypothesis. None of the following is implemented by this documentation update:
- change taxonomy and classifier;
- impact analysis and coverage evaluator;
- policy obligation compiler;
- versioned evidence envelope and append-only history;
- provenance verifier;
- decision engine;
- Change Assurance Dossier;
- reusable PR integration;
- second-language adapter;
- remediation agent or runtime monitor.

The strategic decision is a conditional GO for one Python vertical slice, subject to Gate 0 and the experiments in the roadmap.

## 6. Status transition rule

A capability moves from NOT IMPLEMENTED or PARTIAL only when code, regression tests, an appropriate CI run, and a reproducible artifact exist on a named commit. Conversation repetition, documentation text, an unrelated passing workflow, or a proposed PR does not upgrade status.
