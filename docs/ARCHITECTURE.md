# Architecture

## 1. Product boundary

chipcup is intended to be an evidence-coordinating release-assurance system for Python distributions.

It should answer:

**Does this exact candidate release satisfy this exact, versioned compatibility and release policy, based on evidence whose subject, origin, scope, and freshness can be checked?**

It is not intended to replace specialist packaging, API, static-analysis, licensing, or provenance tools. It should integrate them and preserve relationships among their outputs.

The current implementation is an Alpha prototype. This document describes the current source separately from the target architecture.

## 2. Current implementation architecture

### 2.1 Package layout

The repository is named Pre-python. Its distribution/import package is chipcup.

The current evaluator packages are:

- build: sdist/wheel metadata, selected contents, build metadata, and teacup fixture geometry;
- licenses: SPDX-like expression parsing, LicenseRef mapping, and declared file/subject coverage;
- types: public protocol experiments, stub manifest, stub-file presence, and selected type-surface checks;
- markers: PEP 508 environment and extra evaluation;
- deprecations: DeprecationWarning observations and configured warning/removal schedules;
- imports: module identity, public names, namespace discovery, and entry-point discovery;
- versions: PEP 440 version parsing, comparison, specifier membership, and marker-row scope selection.

The evaluator modules exchange neutral receipt types from chipcup._contracts.

### 2.2 Current receipt execution

The CLI imports runtime lazily from main(). runtime.run_receipt_cycle then imports evaluator functions inside the orchestration call and runs:

    build → licenses → types → markers → deprecations → imports → versions → build-cycle-closure

The cycle-closure receipt compares the artifact release version with the installed distribution version. The receipt envelope contains a boundary name, a closed AuditVerdict, a ReceiptState, evidence, and issues.

The operational states are:

- PASS: the boundary's implemented checks pass;
- FAIL: implemented checks find a failure;
- UNVERIFIED: required evidence or prerequisites are absent or untrusted;
- NOT_APPLICABLE: a policy-controlled boundary is explicitly not applicable.

A missing prerequisite must never be transformed into PASS.

### 2.3 Parallel legacy path

gate.py separately exposes GateRequest, GateReport, and evaluate_release. It executes the same named domains through a different orchestration path and has a different report structure.

This is an architectural inconsistency. The target design requires one authoritative execution path and one versioned output contract. Until that is implemented, consumers should not assume that the legacy GateReport and receipt-cycle CLI have identical semantics.

### 2.4 The teacup fixture

fixtures/chip.dat is an actual input to the build evaluator. fixtures/golden-profile.json defines the golden rim and notch coordinates. The golden notch depth is 2.40 mm; the tolerance is five percent, or 0.12 mm. Source, sdist, and wheel fixture payloads are checked against the golden reference.

The fixture is a useful deterministic geometry mutation test. It is not a proxy for package integrity generally and should not drive the product architecture.

## 3. Current evidence boundaries and limitations

| Boundary | Current evidence | Important limit |
|---|---|---|
| Build | Archive metadata, package names, literal exports, hashes of whole archive files, selected fixture payloads | Does not prove all package files match source-to-sdist-to-wheel |
| License | License-Expression/License-File values, source files, archive member names, configured LicenseRef subject paths | Does not validate identifiers against a versioned SPDX registry or establish legal interpretation |
| Types | Stub manifest and declared paths in source/wheel; some runtime protocol experiments | Does not prove stub declarations are semantically equivalent to runtime contracts |
| Markers | PEP 508 expression and explicit environment/extra rows, filtered by PEP 440 specifier | Requires an explicit policy for which rows are required; currently selected-row evidence is limited |
| Deprecations | JSON observations with release, row, platform, selected, emitted, and count fields | No immutable history or independent proof of observation origin; CLI history is fixed to one release |
| Imports | Import identity and public-name checks in the current process | Importing candidate package code is not isolated from the current process |
| Versions | Imported version and installed distribution metadata are compared to a specifier | CI installs the checkout editable; it does not prove the exact newly built wheel was installed |

The detailed inventory is in STATUS.md.

## 4. Target architecture

The finished system should use six layers.

### Layer 1 — Release subject and inputs

Resolve the exact subjects under evaluation:

- repository and source commit;
- base API reference and candidate API reference;
- project metadata and policy version;
- source distribution and wheel digests;
- installed distribution identity;
- platform and environment matrix;
- published release history;
- external evidence such as build attestations and CI runs.

Every subject must have a stable identifier. A version string alone is insufficient to identify an artifact.

### Layer 2 — Evidence adapters

Adapters retrieve or execute specialist evidence producers. Initial candidates:

- Griffe for API snapshot comparison;
- pydistcheck and wheel/manifest tools for distribution structure;
- packaging for PEP 440 and PEP 508 semantics;
- Twine for description rendering;
- a version-pinned SPDX License List for identifier validation;
- PyPI PEP 740/SLSA attestation verification for provenance;
- CI platform records for job and environment identity.

Adapters must preserve source version, arguments, raw outputs, timestamps, subject digests, and failure details. An adapter must not convert a missing external tool or failed fetch into a passing result.

### Layer 3 — Canonical evidence model

Normalize adapter outputs into a versioned evidence envelope. Preserve raw source references and cryptographic digests. Evidence should be immutable after ingestion; corrections create superseding evidence rather than overwriting history.

See EVIDENCE_MODEL.md.

### Layer 4 — Claim and relationship engine

Represent claims as objects with explicit scope and evidence references.

Relationships include:

- supports: evidence supports a claim;
- contradicts: evidence conflicts with a claim or other evidence;
- derived_from: a derived observation depends on parent evidence;
- scoped_to: evidence applies only to a named subject, release, platform, or policy;
- supersedes: a newer evidence item replaces an older item for a stated purpose;
- reproduces: a run independently reproduces a previous result.

Repeated conversation, duplicated logs, or repeated assertions must not upgrade evidence status.

### Layer 5 — Policy evaluator

Evaluate an explicit, versioned policy over claims and evidence. Each rule states required inputs, applicable subjects, evaluation semantics, allowed exceptions, and what happens when evidence is absent.

The evaluator must preserve unlike verdicts. It must not compress version, API, licensing, platform, and provenance results into one score.

See POLICY_MODEL.md.

### Layer 6 — Decision and report

Return a structured decision:

- ALLOW: all mandatory rules pass with sufficient evidence;
- DENY: a mandatory rule is contradicted or fails;
- APPROVAL_REQUIRED: a defined exception or policy-controlled uncertainty requires human approval.

The decision must list each rule, evidence IDs, reasons, contradictions, unresolved claims, policy version, and exact release subject. It must be reproducible from the same inputs.

## 5. Dependency graph, not a fixed seven-box taxonomy

The current receipt cycle is a useful experiment. The target product should represent a dependency graph rather than assume that exactly seven evaluators are the permanent architecture.

For example:

- API removal claim depends on base and candidate API snapshots.
- Deprecation-window claim depends on the applicable policy, published-release history, and native warning observations.
- Artifact-consistency claim depends on source, sdist, wheel, and installed-artifact digests.
- Provenance claim depends on cryptographic attestation, trusted identity, workflow identity, and artifact digest.
- Final release decision depends on all mandatory claims and their scoped evidence.

A dependency should be explicit and typed. A failed prerequisite must create a downstream UNVERIFIED result, not an artificial PASS.

## 6. Execution and isolation

The final implementation should separate safe artifact inspection from execution of package code.

- Parse archives without extracting untrusted paths into the workspace.
- Apply archive member-count, compressed-size, expanded-size, and time limits.
- Inspect source statically where possible.
- Install and import candidate wheels only in a disposable environment with no secrets and minimal permissions.
- Keep package import and plugin loading out of the control process.
- Run external tools with bounded resources and captured output.
- Treat repository files, issue text, release notes, metadata, and adapter output as untrusted data, never as instructions.

The current import evaluator imports the installed package in its executing environment. This is not a sandbox.

## 7. Reporting

The machine-readable report should have a versioned schema and stable IDs. It should preserve:

- subject identity and digest;
- policy identity and digest;
- rule-level outcomes;
- evidence references and provenance status;
- contradictions and missing evidence;
- tool versions and execution IDs;
- decision and exit status;
- reproducibility instructions.

A human report may summarize the result, but must link every conclusion to its underlying record. It must not hide missing evidence behind a score.

## 8. Architectural migration

1. Declare runtime receipt orchestration authoritative or replace it with a better single path.
2. Convert gate.py into a tested adapter over the authoritative path or remove it through a compatibility plan.
3. Version the report and receipt schemas.
4. Replace opaque evidence dictionaries with validated, immutable records.
5. Add adapter boundaries without embedding third-party tool logic in evaluators.
6. Add policy and historical evidence only after the canonical evidence model exists.
