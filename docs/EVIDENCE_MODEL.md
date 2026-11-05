# Evidence and assurance-case model

**Status:** TARGET contract. Current receipts are narrower and do not implement this schema.

## Core distinction

Evidence is an observation. A claim is a proposition about a subject. A policy rule states what must be evidenced. A decision applies policy to claims and evidence.

A log is not automatically trusted evidence. A passing test is not proof of all behavior. A hash identifies bytes but not origin. A valid signature does not mean the signer is trusted for this subject or policy. An AI explanation is not a verification result.

The dossier is an assurance case, not a formal proof.

## Subject identity

Source subject:
- provider and immutable repository ID;
- canonical repository identity;
- commit and tree SHA;
- base/head/merge-base relation;
- diff digest and normalization version;
- submodule and generated-source references where relevant.

Build subject:
- artifact type and cryptographic digest;
- package name and canonical version;
- build invocation and environment;
- source and dependency/input identities.

Deployment subject, later:
- artifact digest;
- environment and configuration digest;
- deployment and rollout event.

Branch names, PR numbers, filenames, tags, and URLs are not sufficient by themselves.

## Target evidence envelope

| Field | Purpose |
|---|---|
| schema_version | Contract and parser compatibility |
| evidence_id | Stable record/content identity |
| evidence_type | Test, API diff, build, provenance, approval, etc. |
| subject_refs | Exact source/artifact/deployment subjects |
| producer | Tool, collector, workflow, actor, or system identity |
| producer_version | Tool version and build/container digest |
| invocation | Normalized command/configuration and digest |
| input_digests | Decision-relevant input identities |
| output_digest | Normalized output digest |
| raw_evidence_ref | Content-addressed raw output reference |
| environment | OS, architecture, runtime, dependencies, relevant configuration |
| execution_identity | CI provider, workflow/job/run, issuer, repository identity |
| observed_at | Timestamp with timezone and clock assumptions |
| policy_context | Policy bundle/version when relevant |
| trust_state | Verified, asserted, untrusted, invalid, unknown, revoked |
| completeness | Complete within model, partial, unknown, not applicable |
| limitations | Unsupported constructs, excluded scope, missing rows |
| relations | Links to subjects, claims, obligations, and superseding evidence |

A final schema must define canonical serialization, digest algorithm, signature envelope, size limits, and compatibility rules. This table is a design outline.

## Separate evidence axes

Validity:
- VALID
- INVALID
- MISSING
- STALE
- CONFLICTING
- REVOKED
- UNSUPPORTED
- UNAVAILABLE

Trust:
- VERIFIED
- TRUSTED_ASSERTION
- UNTRUSTED
- UNKNOWN

Completeness:
- COMPLETE_WITHIN_MODEL
- PARTIAL
- UNKNOWN
- NOT_APPLICABLE

An observation can be valid but untrusted, trusted but stale, or valid and partial. Do not flatten these axes.

## Claims

Claim status:
- SUPPORTED
- CONTRADICTED
- UNKNOWN
- SUPERSEDED

A claim references exact subject, scope, claim type, policy/contract, supporting and contradicting evidence, assumptions, owner, and time.

Repeating a claim or copying one observation does not improve evidential weight.

## Obligation evidence

Each obligation includes stable ID, policy clause/version, applicability rationale, expected evidence, subject scope, environment/matrix, completion semantics, waiver authority/expiry, result, and evidence IDs.

A required check that did not run is MISSING or UNAVAILABLE, not PASS. “No findings” differs from an incomplete or failed scan.

## Relationships

Use typed records such as derived-from, built-from, tested-on, validates, supports, contradicts, applies-to, supersedes, waives, approved-by, deployed-as, and revokes.

A graph database is not required initially.

## Integrity and history

- Store raw evidence by digest or immutable reference.
- Record normalization/schema version.
- Append corrections with supersedes links; do not overwrite prior findings.
- Replay from exact evidence IDs and policy digest.
- Define retention and deletion explicitly.
- Redact secrets and unnecessary personal data.
- Reuse cached evidence only when all decision inputs and trust policy match.

## Provenance

Verify artifact subject digest, source repository/revision, builder/workflow identity, predicate, signature chain, and trust policy. A caller-supplied build-isolation Boolean remains an assertion.

Reference: https://slsa.dev/spec/v1.2/tracks

## Current compatibility

Current BoundaryReceipt contains boundary, closed AuditVerdict, ReceiptState, evidence mapping, and issues. It lacks most target identity, trust, completeness, lineage, signature, and correction semantics. Do not claim current receipts satisfy this target schema.
