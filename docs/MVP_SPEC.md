# First vertical-slice specification

**Scope:** Python pull-request-to-release assurance  
**Status:** TARGET specification; the complete workflow is not implemented.

## Objective

Given a Python pull request and the distribution artifacts produced from its candidate revision, generate one assurance dossier explaining exact subjects, affected surfaces, obligations, evidence, coverage, provenance, unresolved issues, and the policy decision.

The dossier is an assurance case, not proof of arbitrary program correctness.

## Entry points

1. Local CLI for an explicit repository and base/head references.
2. GitHub Actions / pull-request integration with read-only analysis access.

A hosted app, multi-provider control plane, and SaaS are not prerequisites.

## Required inputs

- immutable repository identifier;
- base commit and candidate commit SHA;
- merge-base identity where relevant;
- package/project identity;
- declared support matrix and policy bundle version;
- dependency and build configuration;
- baseline release/API snapshot reference;
- candidate sdist and wheel;
- trusted CI provenance or explicit UNVERIFIED state;
- required test and analysis outputs.

Branch labels, PR numbers, mutable URLs, and caller Booleans are not immutable subject identity.

## Processing flow

1. Resolve exact base and candidate commits.
2. Normalize the diff and classify changed files/symbols.
3. Run Python API comparison through a specialist adapter such as Griffe.
4. Calculate impact within the supported model and record coverage limitations.
5. Compile policy obligations from change classes and repository policy.
6. Schedule required analyzers/tests in restricted workers.
7. Build the sdist and wheel from the candidate revision.
8. Compare canonical package-relative source/sdist/wheel manifests and hashes under a declared generated-file policy.
9. Install the exact produced wheel in a clean environment and verify import origin and metadata.
10. Verify provenance against artifact digest and accepted builder/workflow identity.
11. Validate warning/deprecation history against published releases and required platform rows.
12. Evaluate every obligation and produce the dossier.
13. Publish a read-only PR check bound to the exact commit.

## Required output

A versioned JSON dossier plus concise human summary containing:
- schema version;
- repository and exact source subjects;
- base/head/diff identities;
- detected change classes and supporting evidence;
- impact coverage and exclusions;
- obligation IDs and policy provenance;
- evidence envelopes and raw artifact references;
- rule results and findings;
- trust and freshness state;
- waivers, approvals, and expiry;
- final decision and rationale;
- unresolved items, tool failures, unavailable checks, timeouts, and rerun lineage.

## Decision semantics

- **ALLOW:** every mandatory obligation is satisfied by evidence trusted for the exact subject and policy.
- **DENY:** valid evidence demonstrates a non-waivable policy violation.
- **APPROVAL_REQUIRED:** required evidence is missing, partial, stale, contradictory, unsupported, or an authorized exception requires human approval.

Evaluator ERROR is never ALLOW.

## Mandatory safety properties

- Candidate code, tests, setup hooks, build backends, and package imports execute only in disposable restricted workers.
- Untrusted PR code receives no publishing credentials or long-lived secrets.
- Privileged status publication is separated from candidate-code execution.
- Evidence binds to exact commit and artifact digests.
- A PR head update invalidates evidence bound to the previous head unless proven independent.
- Required full suites remain required. Predictive test selection may prioritize order but cannot silently remove policy-mandated checks.
- The LLM may suggest change classes, obligations, summaries, and repairs; deterministic policy and trusted evidence determine the decision.
- The agent cannot approve a waiver, merge, publish, or certify its own changes.

## Explicit exclusions

Not included in this slice:
- JavaScript, TypeScript, Rust, Go, or infrastructure-language analyzers;
- runtime telemetry ingestion or incident response;
- hosted graph databases;
- autonomous code changes or merge authority;
- custom general vulnerability scanner;
- dashboard and analytics suite;
- legal compliance certification;
- generic multi-tenant SaaS;
- replacement for existing code review or CI platforms.

## Acceptance gates

### Functional
- exact source and artifact subjects appear in every dossier;
- each obligation traces to a versioned policy clause;
- every result traces to raw evidence and tool/configuration identity;
- missing and mismatched evidence cannot produce ALLOW;
- impact coverage and blind spots are visible;
- decision replay is deterministic.

### Correctness
- seeded API, dependency, packaging, provenance, warning-history, marker, and archive mutants are detected or explicitly unsupported;
- no critical false-pass in the declared corpus;
- malformed, duplicate, stale, forged, and wrong-subject evidence is rejected;
- clean installation tests the exact wheel produced from the sdist.

### Security
- hostile PR and malicious build fixtures cannot access secrets or privileged tokens;
- workers enforce time, memory, CPU, filesystem, and network controls;
- status publication and candidate execution are separated;
- prompt injection cannot alter tool permissions or policy.

### Adoption
- a maintainer can run the CLI on a public sample project without cloud credentials;
- output is concise enough to review and detailed enough to audit;
- a GitHub check links to precise findings and evidence;
- setup and support burden are measured.

## Stop conditions

Pause or reduce scope when impact coverage cannot be measured, evidence identity cannot be established, security isolation is impractical, false-block rates make developers ignore results, baseline tools already deliver equivalent value at materially lower cost, or target users do not recognize the problem.

Do not add features to compensate for an unproven core thesis.
