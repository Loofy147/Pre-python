# Policy model

## Purpose

The policy engine turns evidence-backed claims into a release decision. It must be explicit, versioned, deterministic, and explainable.

The current CLI returns a report containing a Boolean passed value and boundary receipts. It is not yet a general release policy engine.

## 1. Policy identity

Every policy must include:

- policy ID and semantic version;
- content digest;
- applicable project/package identity;
- release channels or environments in scope;
- required evidence kinds;
- required platform/Python/extra matrix;
- rule definitions and severities;
- exception and approval rules;
- effective time and supersession history.

The policy used for a decision must be included in the report. A policy update creates a new identity; it must not rewrite historical decisions.

## 2. Decision vocabulary

The final decision has three values:

| Decision | Meaning |
|---|---|
| ALLOW | Every mandatory rule passes with evidence at the required trust level |
| DENY | A mandatory rule fails or is contradicted |
| APPROVAL_REQUIRED | A defined exception or policy-controlled uncertainty requires an authorized human decision |

A missing mandatory evidence item must not produce ALLOW. It should yield DENY or APPROVAL_REQUIRED according to an explicit policy rule. Never silently convert missing evidence into PASS.

## 3. Rule outcomes

Rule outcomes should remain multi-dimensional. Suggested outcomes:

- PASS;
- FAIL;
- UNVERIFIED;
- NOT_APPLICABLE;
- CONFLICT.

CONFLICT is useful when sources disagree and no precedence rule resolves them. It should not be folded into FAIL or PASS without preserving the contradiction.

Every rule result should contain a rule ID, subject scope, result, explanation, evidence IDs, missing evidence IDs, and policy version.

## 4. Evidence requirements

Each rule defines:

- required subject identity;
- permitted producer identities;
- minimum trust status;
- allowed age/freshness window;
- required environment/platform scope;
- whether evidence must be independently reproduced;
- how contradictory records are handled;
- what missing evidence means.

A digest match, tool success, or source-code assertion must not satisfy a provenance requirement unless the policy explicitly permits it.

## 5. Deprecation and removal policy

PEP 387 describes CPython's backward-compatibility policy. A third-party project's warning and removal schedule is its own policy; chipcup must not claim that a particular number of minor releases is mandated by PEP 387.

A removal-eligibility rule should identify:

- the public symbol or API path;
- the base and candidate API snapshots;
- the first published release in which the warning is observed;
- the required platform/Python/marker rows;
- the policy-required number and kind of subsequent published releases;
- releases in which the warning was actually observed;
- supported-platform changes and their approval evidence;
- exceptions, exemptions, or extensions;
- the proposed removal release.

A warning in a source tree or unit test is not enough. It must be tied to a published candidate or an explicitly defined pre-release observation policy. A marker simulation is not a native warning observation. A warning on one platform cannot satisfy another required platform row.

The warning clock should start according to a documented aggregation rule. For example, if all required platforms must observe a warning, the effective start can be the latest first-valid observation across those required rows. A policy change that removes a platform from scope needs an explicit change record; it cannot silently erase its history.

## 6. API compatibility policy

The policy must define what constitutes the public API:

- __all__ and documented exports;
- public modules, classes, functions, attributes, and aliases;
- dynamic exports and module-level __getattr__;
- import paths and compatibility re-exports;
- typing contracts and relevant metadata;
- documented behavior where API compatibility is behavioral rather than structural.

Use a specialist API snapshot engine such as Griffe for structural comparison, then map each finding to project policy. A detected breakage is evidence; it is not automatically a policy violation if an approved deprecation path or major-version exception applies.

## 7. Artifact policy

A release policy should specify:

- accepted sdist and wheel tags;
- source/sdist/wheel package-file parity rules;
- expected metadata identity;
- exact artifact digest;
- whether the wheel was built from the reviewed sdist;
- clean-environment installation and import checks;
- generated or platform-specific files that are intentionally different;
- artifact size/member-count limits;
- provenance attestation requirements.

Metadata equality is not file-content equality. An explicit manifest and hash comparison policy is needed.

## 8. Licensing policy

Keep these separate:

1. SPDX expression syntax;
2. identifier and exception validity against a pinned SPDX License List;
3. declared License-File coverage;
4. supplemental LicenseRef text and subject mapping;
5. organization-specific allow/deny policy;
6. legal interpretation and manual review.

A syntactically valid expression does not establish that all identifiers are recognized or that the license is acceptable to a particular organization. chipcup should not offer legal advice.

## 9. Version and marker policy

Use the packaging library for PEP 440 and PEP 508 semantics. The policy owns the supported matrix and allowed release range.

The selected matrix must identify the exact Python version, platform, implementation, architecture, and requested extras that matter. Unknown or unselected required rows must not be treated as successful observations.

## 10. Policy precedence and exceptions

Precedence must be explicit and deterministic. Do not overload numeric exit-code order to imply semantic severity.

Human exceptions require:

- authorized approver identity;
- exact subject and rule scope;
- rationale and linked evidence;
- expiration or review condition;
- policy version;
- immutable approval event.

An exception must not change the underlying evidence or pretend that a failed check passed.

## 11. Current implementation gap

The current receipt cycle contains boundary states and a passed Boolean, but no standalone policy identity, policy digest, authorized exception model, final decision type, persistent decision history, or generic rule engine. The current deprecation receipt validates warning observations under a narrow configuration; the CLI hardcodes the published release list to 0.1.0 and uses no scheduled removal release. Do not market that as a completed historical removal policy.
