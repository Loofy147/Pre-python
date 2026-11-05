# Open decisions and risk register

This file tracks unresolved decisions that affect correctness or product scope. Each item should be closed with an ADR, implementation, test, or explicitly accepted limitation. Discussion alone does not close an item.

## P0 — Resolve before expanding implementation

### P0-1. Which orchestration path is authoritative?

Current runtime.py implements the receipt pipeline; gate.py implements a separate GateRequest/GateReport path.

Decision needed: select one public execution path and one report schema. Decide whether the other path becomes a compatibility adapter or is removed with a migration policy.

Closure evidence: one end-to-end test suite exercises the authoritative path; no contradictory release semantics remain.

### P0-2. What qualifies as verified build provenance?

Current build-isolation Boolean is caller supplied.

Decision needed: require which attestation predicates, issuers, builder identities, source repositories, workflow identities, and artifact subject digests? Define offline behavior and how unsupported publishers are handled.

Closure evidence: positive and negative signature/identity/subject-mismatch tests against real or controlled attestations.

### P0-3. What does source-to-wheel equivalence mean?

Current comparison checks metadata, package names, and literal exports, not every distributable file.

Decision needed: define path normalization, generated files, platform-specific artifacts, metadata files, license placement, and allowed transformations.

Closure evidence: canonical manifest and hash comparison tests for missing, extra, modified, and intentionally generated files.

### P0-4. How are untrusted candidate packages executed safely?

Current import checks use the installed package in the current interpreter.

Decision needed: define isolated environment, network policy, secret stripping, resource limits, plugin behavior, and disposal lifecycle.

Closure evidence: malicious import and resource-limit tests in an isolated worker.

## P1 — Required for the intended differentiated product

### P1-1. API baseline source

Should the baseline be the latest stable Git tag, the release immediately preceding the candidate, or a policy-configured reference? How should prereleases and maintenance branches be handled?

### P1-2. Public API definition

How should __all__, documented exports, dynamic __getattr__, re-exports, namespaces, overloads, stubs, and behavior contracts contribute to the API surface?

### P1-3. Deprecation policy semantics

How many published releases are required after the first valid warning observation? Does the rule count minor version numbers, distinct published artifacts, or policy-defined release events? How are yanked releases, prereleases, and platform support changes treated?

### P1-4. Warning evidence authenticity

Which CI identities are trusted to assert native-platform observations? How is the workflow, commit, platform, Python implementation/version, matrix row, and release bound to the record? How are reruns and duplicated evidence handled?

### P1-5. SPDX data lifecycle

Which SPDX License List version is pinned? How are updates reviewed? When offline, should unknown identifiers fail or become UNVERIFIED? Which project-specific LicenseRef mappings are permitted?

### P1-6. Type surface scope

Should chipcup require .pyi contract sets at all? If retained, what parser/checker proves their semantic relationship with runtime exports? If no robust proof is planned, remove the subsystem rather than preserve file-presence checks as a type guarantee.

### P1-7. Release tag and version contract

Should tag version, pyproject version, sdist metadata, wheel metadata, installed metadata, and published index metadata be exact canonical matches? Define normalization and prerelease behavior.

### P1-8. Decision and exception authority

Who can approve an exception, how long can it live, what scope can it cover, and how is it revoked? How do organization-level policies compose with project policy?

## P2 — Product and operational design

### P2-1. Evidence storage

Is a local content-addressed directory sufficient for the first usable product, or is a database needed for concurrent repositories, multiple teams, and long history?

### P2-2. Schema compatibility

What is the compatibility policy for evidence, receipt, report, adapter, and policy schemas? Which changes require a new major version?

### P2-3. CI providers

Which provider should be first after GitHub Actions? Preserve provider-neutral identity and job evidence.

### P2-4. Caching

Which adapter results can be reused safely, and which exact input digests, configuration, tool versions, and trust changes invalidate a cached result?

### P2-5. Data retention and privacy

Which evidence is public, private, or sensitive? How are secrets redacted? How are deletions and legal retention requests handled without silently rewriting past decisions?

### P2-6. Product surface

Should the initial developer experience be CLI + GitHub Action only? Do not build a dashboard until the report schema and policy model are stable and a concrete user need exists.

## Closed decisions

### C-1. Do not compress unlike verdicts into one score

The report preserves distinct rule outcomes. The final release decision may be ALLOW, DENY, or APPROVAL_REQUIRED, but must expose all contributing results.

### C-2. Do not treat PEP 387 as a third-party release schedule

PEP 387 describes CPython's backward-compatibility policy. A package's own warning/removal window is a project policy that must be documented as such.

### C-3. Do not treat archive-level License-Expression as a per-file license declaration

Core metadata's License-Expression applies to the distribution archive containing that metadata. Supplemental per-file LicenseRef mappings need their own text and subject checks.

### C-4. Integrate specialist tools before reimplementing them

Use Griffe, packaging, pydistcheck, Twine, SPDX data, and PEP 740 provenance where their capabilities fit. Reimplement only a proven gap with tests and clear boundaries.
