# Documentation index

Status labels:
- **CURRENT:** present in the reviewed source.
- **PARTIAL:** limited implementation exists and its boundary is stated.
- **TARGET:** proposed design, not shipped behavior.
- **EXPERIMENT:** hypothesis requiring measured results.
- **OPEN:** not established.

The repository is named Pre-python. The current distribution and import package are named chipcup.

## Product and architecture

| Document | Purpose |
|---|---|
| [Product strategy](PRODUCT_STRATEGY.md) | Product thesis, market overlap, user hypotheses, differentiation test |
| [Architecture review](ARCHITECTURE_REVIEW.md) | Adversarial review across product, technical, security, operational, and commercial dimensions |
| [MVP specification](MVP_SPEC.md) | First complete Python change-to-release vertical slice |
| [Change taxonomy](CHANGE_TAXONOMY.md) | Change types, evidence needs, and staged scope |
| [Architecture](ARCHITECTURE.md) | Current execution paths and proposed layered architecture |
| [Decision record](DECISIONS/ADR-0001-change-assurance-scope.md) | Accepted direction, rejected scope, and rationale |

## Trust, evidence, and policy

| Document | Purpose |
|---|---|
| [Evidence model](EVIDENCE_MODEL.md) | Subjects, evidence envelopes, trust, lineage, claims, and correction history |
| [Policy model](POLICY_MODEL.md) | Obligations, rule results, waivers, and final decisions |
| [Security](SECURITY.md) | Threat actors, trust boundaries, isolation, agent permissions, operational controls |
| [Integrations](INTEGRATIONS.md) | Existing tools, adapter contracts, and build-versus-integrate decisions |

## Validation and delivery

| Document | Purpose |
|---|---|
| [Validation and benchmark](VALIDATION_AND_BENCHMARK.md) | Current evidence, adversarial tests, baseline, metrics, acceptance |
| [Roadmap](ROADMAP.md) | Ordered implementation gates |
| [Status](STATUS.md) | Source snapshot, open PRs, current implementation truth, defects |
| [Open questions](OPEN_QUESTIONS.md) | Unresolved decisions and closure evidence |

## Current Python interfaces

| Document | Purpose |
|---|---|
| [Python API reference](API_REFERENCE.md) | Experimental exports in current Alpha source |
| [CLI reference](CLI_REFERENCE.md) | Actual CLI inputs, output, and current-main exit behavior |
| [Design rationale](DESIGN_RATIONALE.md) | Why the product direction and constraints were selected |

## Reading order

Product decisions: Product Strategy → Architecture Review → ADR-0001 → MVP Specification.

Implementation: Status → Architecture → Evidence Model → Policy Model → Security → Integrations → Validation and Benchmark → Roadmap.

Do not use target documents as evidence that a capability is implemented. Status changes only when source, tests, and reproducible artifacts exist on a named commit.
