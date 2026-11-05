# Evidence model

## Purpose

The evidence model is the central proposed product capability. It binds each release claim to exact subjects, raw observations, producer identity, time, scope, and provenance.

The current BoundaryReceipt type is not yet this model. It is a lightweight operational result with an evidence mapping. The following is the target contract and must be implemented and tested before it is advertised as available.

## 1. Evidence is not a claim

Evidence is an observation: a file digest, CI job result, warning observation, API diff, package metadata record, or cryptographically verified attestation.

A claim is a statement derived from one or more evidence items: for example, “the removed symbol had the required warning period on every policy-required platform.”

A decision is the result of evaluating claims against a policy.

Do not conflate these entities. A tool exit code is evidence that the tool returned a status; it is not automatically proof that the broader claim is true.

## 2. Proposed evidence envelope

Every ingested evidence record should include:

| Field | Meaning |
|---|---|
| schema_version | Version of the evidence record contract |
| evidence_id | Stable identifier derived from canonical content or a generated ID plus content digest |
| evidence_kind | API_DIFF, ARTIFACT_MANIFEST, BUILD_ATTESTATION, WARNING_OBSERVATION, SPDX_VALIDATION, VERSION_OBSERVATION, CI_RESULT, or another registered kind |
| subject | Exact object being observed, such as a commit, artifact, release, package, API snapshot, platform row, or policy |
| subject_digest | Cryptographic digest where the subject has bytes |
| producer | Tool or system name, version, and implementation identity |
| invocation | Sanitized arguments, configuration digest, and execution environment |
| observed_at | UTC timestamp for the observation |
| scope | Release, platform, Python version, marker row, extra, package path, API name, or policy region to which the evidence applies |
| raw_reference | Immutable link or storage locator for the original output |
| raw_digest | Digest of the raw output |
| normalized_result | Validated structured result used by policy |
| provenance | Who or what produced the evidence, and how that identity was verified |
| trust_status | Declared, observed, integrity-checked, attested, verified, or unverified |
| limitations | Known coverage gaps and caveats |
| supersedes | Earlier evidence ID, if this is a correction or replacement |

The final schema should use explicit enums, validated field types, canonical serialization, and stable identifiers. Do not accept arbitrary dictionaries as trusted evidence.

## 3. Trust status

Trust status answers how the evidence was obtained. It is not a severity rating.

| Status | Meaning | What it does not prove |
|---|---|---|
| DECLARED | A caller supplied an assertion | That the assertion is true |
| OBSERVED | A controlled process observed an event or result | That the process or input was trusted |
| INTEGRITY_CHECKED | A digest matches the bytes inspected | Who produced those bytes |
| ATTESTED | A valid signature/attestation binds an identity and subject digest | That the policy accepts that identity or workflow |
| VERIFIED | The signature, subject, issuer, identity, scope, and policy requirements all validate | That unrelated claims are true |
| UNVERIFIED | Required checks or trusted evidence are absent | A passing result |

A digest is necessary for strong artifact identity but insufficient for provenance. A caller-supplied Boolean must remain DECLARED or UNVERIFIED.

## 4. Operational receipt state versus claim epistemic status

The current receipt states are operational:

- PASS;
- FAIL;
- UNVERIFIED;
- NOT_APPLICABLE.

The future claim model should preserve epistemic status separately. Suitable claim labels are:

- FACT / ESTABLISHED;
- EXPERIMENTALLY_SUPPORTED;
- USER_REPORTED;
- INFERENCE;
- HYPOTHESIS;
- CONTRADICTED;
- UNKNOWN / OPEN.

For example, a tool may return PASS under a limited test. The broader claim may still be EXPERIMENTALLY_SUPPORTED or UNKNOWN if the test does not cover all required inputs. Repeating the same result does not promote the claim.

## 5. Evidence relationships

The relationship engine should support at least:

- SUPPORTS: evidence supports a claim;
- CONTRADICTS: evidence conflicts with a claim or another evidence item;
- DERIVED_FROM: a claim or evidence item depends on named parents;
- SCOPED_TO: an observation applies only to a specific subject/environment;
- SUPERSEDES: a later correction replaces an earlier record for a declared purpose;
- REPRODUCES: an independent run reproduces a prior result;
- PRODUCED_BY: an execution produced an evidence item.

Each relationship needs a type, source ID, target ID, and optional rationale. A relation must not silently rewrite the underlying evidence.

## 6. Subject identity

A release name or version string is not enough. Relevant subjects include:

- repository identity;
- source commit SHA and tree SHA;
- API snapshot reference and digest;
- sdist filename, digest, and metadata identity;
- wheel filename, digest, metadata identity, and tags;
- installed distribution name/version/location;
- warning observation plus native platform and matrix row;
- release tag and published index file;
- policy ID, version, and digest.

The evidence engine must reject evidence for a different artifact digest even if the filename and version are equal.

## 7. Temporal evidence

The evidence ledger must distinguish:

- event time: when a warning or release actually occurred;
- observation time: when the evidence collector recorded it;
- ingestion time: when the evidence entered the ledger;
- policy evaluation time: when a decision was made.

Historical policy evaluation must be reproducible from the evidence available at that time. A newly added record may change today's result, but it must not silently rewrite a prior decision.

## 8. Append-only correction model

Evidence should not be edited in place after ingestion. If an observation was wrong:

1. retain the original record;
2. create a correction record;
3. link the correction with SUPERSEDES;
4. record why and who initiated the correction;
5. re-evaluate affected claims and decisions;
6. retain the prior decision and its input set.

This provides an auditable contradiction lifecycle.

## 9. Storage and schema evolution

The first implementation can use content-addressed JSON files and a small local index. A database is not required until concurrent writes, access control, retention, or query scale justify it.

Requirements:

- schema versions and migrations;
- canonical JSON or another deterministic encoding;
- SHA-256 or an explicitly versioned stronger digest policy;
- explicit UTC timestamps;
- no secret material in records or logs;
- integrity checks on every read;
- retention and export behavior;
- deterministic replay of policy evaluation.

## 10. Current gap

The current implementation serializes BoundaryReceipt values to ordinary JSON with evidence dictionaries. It does not provide a durable ledger, evidence identity model, signatures, append-only correction history, cross-run relationships, or policy replay. These remain target requirements.
