# Policy, obligations, and decisions

**Status:** TARGET model. The current CLI does not implement this complete policy engine.

## Separate layers

1. Change classification.
2. Impact result and coverage.
3. Obligation generated from versioned policy.
4. Rule result.
5. Final decision for an exact subject.

Severity, classifier confidence, claim status, evidence trust, and final decision are distinct.

## Obligation compilation

Inputs: exact source/artifact subjects; change classes and impact results; versioned repository/organization policy; support matrix; dependency/build/release context.

Output:
- stable obligation ID;
- policy clause/version;
- applicability rationale;
- required evidence types and subject;
- expected tool/environment;
- required/optional status;
- waiver authority and constraints.

Compilation is deterministic for fixed normalized inputs and policy version. An LLM may propose an obligation, but a policy owner must accept it into a versioned policy pack before it becomes mandatory.

## Rule results

- **SATISFIED:** evidence is valid, trusted, sufficiently complete, fresh, and subject-matched.
- **VIOLATED:** valid evidence demonstrates a policy violation.
- **UNKNOWN:** evidence is missing, partial, conflicting, stale, untrusted, unsupported, or insufficient.
- **WAIVED:** a separate authorized exception applies.
- **NOT_APPLICABLE:** policy is irrelevant, with a recorded reason.
- **ERROR:** evaluator could not finish reliably.

SATISFIED means the specific obligation was met under its declared model, not that all software behavior is correct.

## Final decision

- **ALLOW:** all mandatory obligations are satisfied or legitimately not applicable.
- **DENY:** a mandatory non-waivable rule is violated or explicit prohibition applies.
- **APPROVAL_REQUIRED:** required evidence is unknown/error or an authorized exception requires human approval.

A waived violation remains recorded as VIOLATED with a separate waiver event. Do not rewrite it as PASS.

## Non-scalar semantics

Do not compress API compatibility, security, licensing, build identity, warnings, runtime behavior, and approvals into one score. A heuristic may prioritize investigation but cannot override hard policy or turn UNKNOWN into SATISFIED.

## Trust policy

Check exact subject, trusted producer/builder, accepted issuer/signature, expected workflow/repository, tool/configuration version, completeness, freshness, and revocation. A valid signature from an untrusted identity is insufficient.

## Temporal policy

Define supported Python/platform matrix, API baseline, warning/removal windows, prerelease and yanked-release treatment, source/sdist/wheel parity, SPDX list version, provenance identities, and required checks for high-risk changes.

PEP 387 describes CPython's policy. A third-party project's warning/removal period is its own policy.

## Exceptions

Every exception records rule and subject scope, reason, risk acceptance, approver/authority, creation and expiry times, compensating controls, decision link, and revocation/supersession. AI cannot create or approve waivers.

## Policy composition

Organization and repository policies require explicit precedence. Conflicting mandatory policies produce ERROR or APPROVAL_REQUIRED until resolved; do not silently choose the permissive rule.

## Replay

Every decision records exact subjects, policy digest, obligations, evidence IDs and states, rule results, exceptions, approvers, evaluator version, decision, and rationale. A policy change creates a new decision record; it does not rewrite history.
