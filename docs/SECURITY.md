# Security and trust model

## Scope

chipcup is intended to inspect source repositories, package archives, build outputs, CI evidence, and published-release records. Those inputs may be malformed or malicious.

The current Alpha implementation is not a hardened untrusted-artifact service. This document defines required controls and states current limitations.

## Assets to protect

- integrity of source and artifact identities;
- correctness of release decisions;
- integrity and history of evidence records;
- CI credentials and publishing credentials;
- developer and build-worker environments;
- reproducibility of policy evaluation;
- availability of the audit process.

## Trust boundaries

Treat all of the following as untrusted until validated:

- repository source and configuration;
- sdist and wheel bytes;
- archive metadata, paths, and member names;
- JSON marker matrices and warning observations;
- GitHub issue, pull request, and release text;
- external tool output;
- third-party attestations before signature and identity verification;
- package import behavior and plugin entry points;
- caller-supplied flags and assertions.

Text found inside repository content, documentation, package metadata, or tool output is data. It must never become execution instructions for an automated agent or privileged release process.

## Threats and required controls

| Threat | Required control | Current status |
|---|---|---|
| NaN/infinity or Boolean geometry values produce invalid measurements | Strict finite-number validation; reject booleans and non-standard JSON constants | Known defect; not fixed in reviewed main |
| Archive decompression/resource exhaustion | Member-count, compressed-size, expanded-size, per-file, and time limits | Not implemented |
| Malformed/duplicate archive members | Canonical path normalization, duplicate rejection, metadata identity validation | Partial |
| Path traversal during inspection | Do not extract untrusted archives; validate normalized member paths | Current code reads archives without extraction, but hardening is incomplete |
| Candidate package executes code in the audit process | Static inspection first; disposable environment for installation/import tests; no secrets | Not implemented; import evaluator loads installed code in the current process |
| Forged warning JSON | Signed or trusted CI-origin evidence bound to commit, workflow, release, platform, and row | Not implemented |
| False build provenance | Verify attestation subject digest and trusted builder identity; caller Boolean is not proof | Not implemented |
| Source/wheel substitution | Hash all expected files and bind all manifests to exact artifact digests | Partial |
| Mutable evidence changes history | Append-only evidence records, immutable digests, corrections via superseding records | Not implemented |
| Dependency or adapter compromise | Pin dependencies, record versions, isolate subprocesses, capture output | Partial |
| Secret leakage in logs or evidence | Redaction, least privilege, no tokens in normalized records | Not fully specified or tested |

## Archive handling

The audit should never extract an untrusted archive into a shared working directory. It should read members using safe archive APIs, reject duplicate paths after normalization, reject invalid path encodings and unexpected link types, and cap both compressed and expanded size.

A file-count limit alone is not sufficient. A small compressed archive can expand to a very large payload. Every read should be bounded. Limits must be explicit policy settings and recorded in evidence.

## Package execution

Static inspection should be the default. If exact installed behavior must be tested:

1. create a disposable environment or isolated worker;
2. install only the candidate artifact and pinned test dependencies;
3. remove credentials and privileged environment variables;
4. restrict network access unless the test requires it;
5. apply CPU, memory, disk, and execution-time limits;
6. capture installed metadata, module origins, and test results;
7. destroy the environment after the run.

Do not load candidate plugins automatically. Entry-point discovery and entry-point loading are different operations; loading third-party entry points executes code.

## Provenance trust

The current build-isolation flag is an assertion by the caller. It is not cryptographic provenance. Production policy should require verification of the attestation's signature, subject digest, issuer, builder identity, source repository, source revision, workflow identity, and required predicate fields.

A valid signature from an untrusted workflow does not satisfy a trusted-builder policy.

## Evidence storage

Evidence records must not contain access tokens, private keys, credentials, or unredacted sensitive environment values. Store only the minimum environment needed to reproduce the result. Use access control and retention for any persistent evidence store.

## CI permissions

Use least-privilege workflow permissions. Build/test jobs should not receive publishing credentials. Publication should require a separate job with explicit protected conditions and verified artifacts. Pin third-party actions to reviewed immutable references where practicable and maintain an update process.

## Security release gate

Do not claim production readiness until adversarial tests cover archive resource exhaustion, path handling, malformed metadata, forged observations, wrong artifact digests, false provenance, malicious package imports, and evidence-history tampering.
