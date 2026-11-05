# Roadmap and release gates

## Guiding rule

Do not expand the feature list until the system can fail closed on invalid evidence and explain every release decision. The roadmap is ordered by dependency, not by visual appeal or module count.

No dates are assigned. A stage is complete only when its exit criteria are evidenced on a named commit and the relevant CI run.

## Stage 0 — Correctness and source-of-truth cleanup

**Objective:** remove false-pass paths and contradictions in the existing prototype.

Work:

- reject NaN, infinity, and booleans in geometry and numeric policy inputs;
- make archive parsing bounded and reject ambiguous paths/members;
- replace caller-provided build-isolation Boolean with an explicitly unverified assertion until independent evidence is verified;
- compare canonical package-relative file manifests and content hashes across source, sdist, and wheel;
- build and install the exact wheel from the sdist in a clean environment;
- reconcile GPU stub declarations and runtime contract mappings, or remove the unsupported stub subsystem;
- make the marker evaluator validate only selected rows while still validating the policy's required scope;
- validate warning count/emitted consistency and reject malformed or duplicate records;
- derive release workflow version from the tag and compare with project metadata;
- choose one authoritative orchestration path and bridge or retire the other;
- reconcile the open exit-code proposal with the actual policy vocabulary.

Exit criteria:

- all known critical false-pass cases have regression tests;
- exact produced wheel is installed and audited;
- all package files are accounted for by a declared source-to-artifact policy;
- direct API defaults fail closed;
- release tag mismatch fails before publication;
- only one supported report contract exists;
- full CI passes on the final commit.

## Stage 1 — Canonical evidence and claim model

**Objective:** create the data contract that makes the product more than a collection of evaluators.

Work:

- versioned evidence envelope;
- immutable subject identifiers and artifact digests;
- typed evidence kinds and trust status;
- validated relationship records;
- claim status separate from receipt state;
- append-only correction and supersession model;
- deterministic serialization and replay;
- raw output references with digest validation.

Exit criteria:

- schema conformance tests;
- malformed and mismatched subject rejection;
- immutable evidence behavior;
- correction history preserves prior records;
- independent replay produces identical policy inputs.

## Stage 2 — Specialist tool adapters

**Objective:** reuse existing tool quality rather than reimplement it.

Initial adapters:

1. Griffe for base/candidate API snapshots;
2. pydistcheck and archive inspectors for distribution structure;
3. Twine description rendering;
4. packaging for version/marker semantics;
5. version-pinned SPDX License List validation;
6. PyPI PEP 740/SLSA attestation verification.

Exit criteria:

- each adapter binds output to exact source/artifact identity;
- preserves raw output, tool version, and invocation;
- distinguishes pass, fail, unsupported, unavailable, and incomplete;
- includes positive, negative, malformed, and wrong-subject tests;
- can be reproduced from published instructions.

## Stage 3 — Cross-release lifecycle and policy engine

**Objective:** turn observations into historical, explainable policy decisions.

Work:

- published release inventory;
- immutable API snapshot history;
- warning observations tied to release and native environment;
- platform support matrix history;
- configurable deprecation/removal windows;
- versioned policies and exceptions;
- ALLOW / DENY / APPROVAL_REQUIRED decisions;
- contradictions, stale evidence, and supersession handling.

Exit criteria:

- policy replay against historical releases is deterministic;
- removal eligibility is tested against multi-platform and multi-release scenarios;
- no missing required evidence can produce ALLOW;
- policy changes preserve historical decisions.

## Stage 4 — CI product and developer experience

**Objective:** make the assurance engine practical to adopt.

Work:

- reusable GitHub Action;
- machine-readable versioned report and human summary;
- pull-request checks with precise finding links;
- local CLI with explicit offline behavior;
- provider-neutral CI evidence contract;
- exit-code and report compatibility policy.

Exit criteria:

- clean setup on a sample repository;
- no credentials required for public-source checks;
- least privilege for private or publishing workflows;
- example integration and migration documentation;
- stable schema and exit-code tests.

## Stage 5 — Comparative validation and first stable release

**Objective:** prove the project provides a distinct, useful improvement.

Work:

- public benchmark corpus;
- declared baseline toolchain;
- seeded defect/mutant matrix;
- true/false positive analysis;
- independent reproduction;
- performance and resource measurements;
- security review;
- release provenance verification.

Exit criteria:

- reproducible benchmark demonstrates a concrete incremental value;
- no critical false-pass in the release decision path;
- security and operational limits are documented;
- all core capabilities are implemented rather than aspirational;
- release artifacts and their provenance are independently verifiable;
- versioned schemas and compatibility policies are stable.

## Explicit non-goals for the first stable release

- replacing Griffe, packaging, Twine, mypy, or SPDX;
- offering legal advice or automated legal acceptance;
- claiming every Python package's behavior can be proven statically;
- executing arbitrary candidate package code in a privileged process;
- a large hosted dashboard before local evidence and policy semantics are stable;
- an opaque score that hides why a release passed or failed.

## Release readiness

The current 0.1.0 Alpha is a research prototype. Do not publish a production-readiness claim until Stage 0 through Stage 5 exit criteria are met. A tag-shaped version or successful CI run is not a substitute for those gates.
