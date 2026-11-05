# Documentation index

This documentation distinguishes three things:

- **Current implementation:** behavior present in the source tree and exercised by current tests or CI.
- **Known limitation:** a gap, false-pass risk, or missing source of evidence in the current implementation.
- **Target design:** a proposed capability that requires implementation and proof before it can be advertised.

Do not convert a target-design statement into an implementation claim.

## Start here

| Document | Purpose |
|---|---|
| [Status](STATUS.md) | Current implementation truth, verified evidence, and known gaps |
| [Architecture](ARCHITECTURE.md) | Existing execution paths and target system architecture |
| [Evidence model](EVIDENCE_MODEL.md) | Proposed evidence envelope, trust levels, claims, and relationships |
| [Policy model](POLICY_MODEL.md) | Verdicts, release decisions, temporal rules, and exceptions |
| [CLI reference](CLI_REFERENCE.md) | Actual current command, inputs, output, and exit behavior |
| [Integrations](INTEGRATIONS.md) | Responsibilities of existing tools and planned adapters |
| [Security](SECURITY.md) | Threat model, trust boundaries, and security requirements |
| [Validation](VALIDATION_AND_BENCHMARK.md) | Current test evidence, missing tests, and differentiation benchmark |
| [Roadmap](ROADMAP.md) | Sequenced implementation stages and release gates |
| [Design rationale](DESIGN_RATIONALE.md) | Architectural decisions, non-goals, and product thesis |
| [Open decisions](OPEN_QUESTIONS.md) | Prioritized unresolved design and implementation decisions |

## Vocabulary

**Evidence** is a sourced observation or artifact. A hash can establish content identity, but does not alone establish who produced the content or whether it is trustworthy.

**Claim** is a statement about a subject, such as “the public API removal is compatible with the declared warning policy.”

**Receipt** is the current prototype's boundary result. Its operational state is not an epistemic confidence score.

**Policy** is a versioned set of rules and scopes that determines which evidence is required and how it is evaluated.

**Decision** is the policy result for a release: ALLOW, DENY, or APPROVAL_REQUIRED. It must include reasons and evidence references.

**Subject** is the exact entity under evaluation: source commit, distribution artifact, installed package, public API snapshot, platform observation, release, or policy version.

**Provenance** is evidence about origin and production. A caller-provided Boolean is an assertion, not independent provenance verification.

## Documentation maintenance rule

When implementation changes, update the relevant status row, CLI examples, evidence contract, and tests-to-claims mapping in the same change. Every claim of verified behavior must point to a reproducible test, CI execution, immutable artifact, authoritative source, or other independently re-checkable evidence.
