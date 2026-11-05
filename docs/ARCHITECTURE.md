# Architecture

## Status boundary

This document separates:
- **CURRENT:** 0.1.0 Alpha source contains a Python-specific seven-boundary receipt experiment and a separate GateReport evaluation path.
- **TARGET:** the Change Assurance Engine below is proposed architecture, not shipped code.

Reviewed main commit: 7ef2c82fb2ebdf2e08376b154bd6e9f112b6a5ca.

## Current implementation

The CLI calls runtime.run_receipt_cycle. It composes build, licenses, types, markers, deprecations, imports, versions, and build-cycle closure.

Shared BoundaryReceipt records contain a boundary name, closed AuditVerdict, ReceiptState, evidence mapping, and issue list. The dataclass is frozen, but the evidence mapping is not deeply immutable.

The public root evaluate_release API uses chipcup.gate and a GateRequest/GateReport model. This is a separate execution and output path. The project has not selected one authoritative public report contract.

The current CLI hardcodes published release history around 0.1.0 and accepts a caller-supplied build-isolation flag. Neither is an acceptable future trust mechanism.

## Target architecture

~~~text
SCM / CLI / CI event
        |
        v
[1] Subject resolver
    repository, base, head, tree, diff, artifact IDs
        |
        v
[2] Change normalizer + classifiers
    source/API, dependency, build, config, security, schema
        |
        v
[3] Impact analyzers + coverage evaluator
    affected symbols, modules, tests, consumers, blind spots
        |
        v
[4] Obligation compiler
    versioned policy -> required evidence and checks
        |
        v
[5] Verification adapter runner
    Griffe, tests, mypy, scanners, build, SPDX, provenance
        |
        v
[6] Evidence ledger
    raw outputs, digests, identity, lineage, corrections
        |
        v
[7] Policy evaluator
    obligation results, trust, waivers, conflicts
        |
        v
[8] Assurance dossier + status check
    ALLOW / DENY / APPROVAL_REQUIRED
~~~

An optional agent may investigate findings or suggest repairs. It is outside the trusted policy path.

## Component responsibilities

### Subject resolver

Creates immutable identities for repository, base/candidate commits, tree, merge base, diff, build inputs, sdist, wheel, and later deployment subjects. A branch name or PR number is not subject identity.

The dossier must distinguish a PR head commit from the merge-queue merge-group commit actually tested.

### Change normalizer and classifier

Normalizes changed paths, symbols, configuration objects, dependency edges, and declared interfaces. It emits proposed change classes with source signals. LLM classifications are advisory and preserve evidence and uncertainty.

### Impact analyzers and coverage evaluator

Uses language/ecosystem analyzers and emits affected subjects plus model coverage limitations. No graph edge means “not observed”, not “unaffected”. Unsupported constructs produce PARTIAL or UNKNOWN.

### Obligation compiler

Combines change classes, repository policy, supported environments, and release context into obligations. It is deterministic and policy-versioned. A model cannot add/remove mandatory obligations at runtime.

### Verification adapters

Invoke specialist tools and controlled tests. They produce evidence, not final policy decisions. Each adapter declares versions, inputs, resource limits, output schema, timeout/failure semantics, and unsupported cases.

### Evidence ledger

Stores raw output or content-addressed references, normalized records, subject identity, tool/configuration, environment, trust, and relations. A first version can use local files and a small index. A graph database is not a prerequisite.

### Policy evaluator

Checks that mandatory obligations are satisfied by valid, trusted, fresh evidence for the exact subject. Missing, conflicting, stale, or untrusted evidence remains unresolved.

### Dossier and status integration

Produces a versioned machine-readable dossier and concise human summary. A GitHub status/check points to the exact dossier and commit; it is not the evidence source of truth.

## Target contracts

- ChangeSubject: immutable repository/revision/artifact identity.
- ChangeSet: normalized changed paths/symbols, base/head relation, diff digest.
- ImpactResult: analyzed scope, affected subjects, coverage, exclusions, analyzer identity.
- Obligation: policy clause, applicability, required evidence, owner, waiver semantics.
- EvidenceEnvelope: subject, producer, tool, inputs/outputs, raw reference, environment, trust, time.
- Finding: issue, severity, confidence, location, supporting evidence, limitations.
- DecisionRecord: policy digest, obligation results, exceptions, approvers, final decision, rationale.

These are target contracts, not current Python data classes.

## Storage and query strategy

Start with content-addressed evidence objects, a versioned JSON schema, and a small relational/document index for subjects and relationships. Add graph indexing only when real queries, repository count, evidence volume, and retention needs justify it.

## Execution and concurrency

- Jobs are idempotent for a defined input tuple.
- Cache keys include source/artifact digests, tool version, configuration digest, environment, policy version, and trust policy.
- Decision-relevant input changes invalidate dependent evidence.
- Jobs have timeouts, bounded retries, resource caps, and terminal states.
- Duplicate events are deduplicated without losing rerun history.
- PR head updates create new subjects and invalidate head-bound results.
- Merge-queue validation uses the merge-group subject and correct workflow trigger.
- The decision is recomputed when policy or required evidence changes.

## Failure states

Distinguish analyzer finding, unavailable, error, incomplete scan, invalid output, subject mismatch, stale evidence, untrusted producer, timeout, and not applicable. Unavailable or invalid required analysis cannot satisfy an obligation.

## Extensibility and deferrals

A language adapter declares semantics and blind spots. A CI adapter preserves native workflow identity. A policy pack is versioned and cannot reinterpret old evidence silently.

Do not implement now: organization-wide graph infrastructure, runtime telemetry, autonomous remediation, hosted dashboard, arbitrary multi-provider CI, or generic multi-tenant SaaS.
