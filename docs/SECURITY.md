# Security and trust model

**Status:** target requirements. The current prototype does not satisfy every requirement here.

## Objective

The system consumes untrusted source code, PR metadata, build configuration, dependencies, tests, scanner output, and model-generated text. Those inputs must not gain authority over credentials, policy, evidence trust, approvals, or publication.

## Threat actors and assets

Threat actors:
- malicious or compromised pull-request author;
- compromised dependency, package, build backend, action, or runner;
- compromised CI identity or evidence collector;
- malicious or careless administrator;
- prompt injection in source, docs, issue text, test logs, or scanner output;
- compromised integration or tenant;
- accidental policy misconfiguration.

Assets:
- source and artifact integrity;
- tokens, secrets, and signing keys;
- policies and trust lists;
- evidence history and decision records;
- private source code and customer metadata;
- approval and publishing authority;
- availability and CI capacity.

## Trust boundaries

Separate at minimum:
1. **Control plane:** trusted configuration, policies, job scheduling, and decisions.
2. **Candidate execution plane:** untrusted source, tests, builds, and imports.
3. **Evidence plane:** outputs, attestations, normalized records, and storage.
4. **Integration plane:** SCM, CI, package index, artifact store, and scanners.
5. **Human authority plane:** maintainers and security/policy approvers.
6. **Optional model/agent plane:** advisory only.

Candidate code must not run in the privileged orchestration process or context holding SCM write credentials, signing keys, publishing tokens, or policy secrets.

## Pull-request execution

- Treat PR source, tests, build config, metadata, and workflow files as attacker-controlled.
- Do not execute untrusted PR code in a privileged workflow.
- Keep analysis credentials read-only and narrowly scoped.
- Separate privileged status publication from candidate execution.
- Use ephemeral workers and clean filesystems.
- Never execute untrusted outputs in a privileged workspace.
- Validate output schemas and sizes before parsing.
- Handle merge-queue merge_group events for checks required by the repository's merge policy.

GitHub merge-queue status guidance: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks?plain=1

## Worker isolation

Required controls:
- disposable workers;
- no host mounts containing secrets;
- least-privilege filesystem;
- CPU, memory, process, size, and wall-clock limits;
- default-deny egress;
- sanitized environment;
- pinned or verified images;
- distinct service identity;
- no signing/publishing keys;
- bounded logs and output.

Do not call a normal virtual environment or container a security sandbox without adversarial isolation evidence.

## Supply chain and provenance

Pin critical actions/dependencies according to a reviewed update policy. Verify artifact subject digest, builder, source revision, workflow identity, predicate, signature, and trust list. Reject replayed and mismatched attestations. A caller Boolean is not provenance.

SLSA reference: https://slsa.dev/spec/v1.2/tracks

## Prompt injection and agents

Source files, README text, issues, PR descriptions/comments, test output, metadata, and scanner results are untrusted data.

Agents require:
- bounded untrusted-input handling;
- fixed tool allowlist and scoped inputs;
- no secret or policy-key access;
- no policy/trust-list edits;
- no waiver approval, merge, release, or publication;
- human authorization for patch application;
- independent clean-worker verification;
- agent findings separate from verifier evidence.

An agent cannot certify its own patch.

## Evidence and policy integrity

Use cryptographic digests, exact subject binding, producer identity, correction/revocation records, replay detection, secret redaction, explicit retention, and scoped expiring exceptions.

A hash proves bytes, not origin. A signature proves identity only under an applicable trust policy.

## Hosted future

Multi-tenant operation requires tenant isolation across compute/storage/queues/caches/logs, key management, deletion/retention, token isolation, administrator audit, residency controls, incident response, third-party/model-provider review, and availability/recovery design.

Do not implement hosted multi-tenancy before customer requirements and operational ownership are established.

## Security acceptance

Before becoming a merge/release gate, test malicious imports/build hooks, attempted exfiltration, workflow permission escalation, archive path/decompression attacks, resource exhaustion, forged/replayed/stale/wrong-subject evidence, revoked signers, prompt injection, self-approval, malicious patches, policy mutation, waiver abuse, and cross-tenant access if hosted.

A critical mandatory-policy bypass blocks release.
