# ADR-0001: Change Assurance scope and first vertical slice

- Status: ACCEPTED AS STRATEGIC DIRECTION; differentiation remains unproven
- Date: 2026-11-05
- Decision owner: project maintainers
- Supersedes: proposal to build Software Engineering Intelligence as one initial product

## Context

The repository has a Python packaging/release-audit prototype with real but limited receipt and artifact checks. A broader proposal included change intelligence, a software knowledge graph, adaptive verification, an engineering agent, runtime assurance, and governance.

Public product documentation shows substantial adjacent capabilities in AI code review, code graph/context, security scanning, predictive tests, and software supply-chain graphs. Rebuilding them independently would create overlap and operational burden.

The current code also has foundational correctness gaps: caller-asserted provenance, incomplete artifact parity, unauthenticated warning evidence, incomplete type-stub semantics, separate execution paths, and no comparative benchmark.

## Decision

Use **Change Assurance Engine** as the working strategic direction.

The core unit is a software change bound to exact immutable source and artifact subjects.

The workflow:
1. identify the exact change;
2. classify relevant change types;
3. determine affected subjects and report coverage;
4. compile obligations from versioned policy;
5. run specialist verifiers;
6. bind evidence to exact subjects;
7. evaluate obligations and exceptions;
8. emit a replayable assurance dossier and decision.

The first vertical slice is Python pull-request-to-release assurance. The current chipcup implementation is the starting reference and must first pass Gate 0 correctness work.

## Accepted constraints

- The dossier is an assurance case, not formal proof of program correctness.
- Policy packs, not LLMs, own mandatory obligations.
- Static analysis exposes blind spots and incomplete coverage.
- Required tests are not silently replaced by predictive test subsets.
- Candidate code runs only in isolated unprivileged workers.
- Agents cannot approve waivers, merge, publish, or certify their own repairs.
- Specialist tools are integrated before an equivalent replacement is considered.
- Graph database, dashboard, hosted SaaS, runtime monitoring, all-language support, and autonomous repair are not first-slice requirements.
- Evidence, rule result, claim status, trust, severity, and final decision remain separate.
- No opaque scalar score determines release policy.

## Consequences

Benefits:
- one concrete user workflow and product outcome;
- reuse of established analyzers;
- smaller security and operations surface;
- measurable comparison against an established baseline;
- a path to test cross-language abstraction later.

Costs and risks:
- narrower initial scope;
- evidence binding and provenance verification require careful implementation;
- Python dynamic behavior limits static impact completeness;
- product differentiation may not justify adoption;
- future languages/runtime evidence require separate domain work.

## Rejected alternatives

- Build the whole Software Engineering Intelligence platform immediately: too many product categories and no validated demand.
- Build another AI reviewer: the active market is crowded and the project thesis is evidence/decision lineage.
- Build a universal knowledge graph first: graph storage does not create reliable relations or trusted evidence.
- Start with autonomous repair: it expands execution and permission risk before verification is trustworthy.
- Remain permanently limited to Python release checks: rejected as long-term ambition, accepted as the first implementation slice.

## Validation required before expansion

- P0 code defects are closed with regression tests.
- Evidence and policy contracts are versioned and replayable.
- Python vertical slice passes security and correctness gates.
- Paired comparative benchmark shows incremental value.
- Design partners confirm a real problem and acceptable workflow burden.

## Revisit triggers

Revisit if baseline tools provide equivalent assurance at lower cost, customer interviews point to a different highest-value problem, impact coverage is inadequate, provenance/isolation cannot be established affordably, or benchmark results show unacceptable false blocks or overhead.
