# Product strategy — Change Assurance Engine

**Status:** strategic hypothesis, not a shipped product or proven market category.  
**Review date:** 2026-11-05.

## Strategic decision

Explore a Change Assurance Engine: a system connecting a concrete software change to its potential impact, required verification obligations, collected evidence, policy evaluation, and accountable decision.

This is narrower than a general Software Engineering Intelligence platform. Code intelligence, autonomous repair, runtime monitoring, cross-language support, knowledge graphs, and enterprise governance are adjacent possibilities, not the first product. The working name is descriptive; repository and package names remain unchanged.

## Problem to investigate

Engineering teams already have source control, review, static analysis, tests, security scanners, dependency tools, build systems, provenance records, and release workflows. The potential problem is fragmentation between:
- what changed and what may be affected;
- which compatibility, security, quality, and release obligations apply;
- which tool produced each result;
- whether every result concerns the exact source revision and artifact;
- whether evidence is complete, fresh, and trusted;
- why the final decision was made and whether it can be replayed.

A green check can be insufficient if it applies to an earlier commit, a different artifact, an incomplete test subset, or an untrusted workflow.

## Product job

For each material change, answer:
1. What exact source and artifact subjects are under review?
2. What may be affected within the declared analysis model?
3. How complete is the impact analysis?
4. Which versioned policies require which checks?
5. Which evidence was produced, by whom, using what tool, configuration, and environment?
6. Does each result match the exact subject and policy?
7. What remains missing, stale, contradictory, unsupported, or waived?
8. Who is accountable for the decision and any exception?

The output is a Change Assurance Dossier: an auditable assurance case, not a formal proof of program correctness.

## Differentiation hypothesis

The hypothesis is the conjunction of:
- change-scoped obligations;
- cross-tool evidence lineage;
- lifecycle continuity from source through exact build/release artifact;
- replayable decisions from preserved evidence and policy.

This is not experimentally established. Do not advertise uniqueness before a paired benchmark against a competent baseline.

## Market overlap

The public documentation review on 2026-11-05 found active products in:
- AI pull-request review and approval assessment (GitHub Copilot);
- multi-repository context, PR analysis, and review rules (Qodo);
- AI reviews and custom quality rules (Graphite);
- predictive test selection (Launchable);
- code graphs and impact navigation (Sourcegraph);
- software supply-chain relationship graphs (GUAC);
- provenance requirements and verification models (SLSA).

Consequences: do not differentiate as another reviewer, code graph, scanner, predictive test selector, or dashboard. Integrate specialist tools. The market review is not exhaustive or hands-on.

References:
- https://github.blog/changelog/2026-09-01-copilot-code-review-can-now-approve-pull-requests/
- https://docs.github.com/en/code-security/concepts/code-scanning/code-scanning-on-pull-requests
- https://www.qodo.ai/formerly-qodo-merge/
- https://www.graphite.com/docs/ai-reviews
- https://help.launchableinc.com/features/predictive-test-selection/
- https://sourcegraph.com/docs/cody/core-concepts/code-graph
- https://docs.guac.sh/guac/
- https://slsa.dev/spec/v1.2/tracks
- https://dora.dev/guides/dora-metrics/

## Initial user and buyer hypotheses

| Role | Job | Value that must be demonstrated |
|---|---|---|
| Maintainer / senior developer | Understand consequences of a change and avoid missed regressions | High-signal impact explanation with low review friction |
| Platform engineering | Standardize CI, artifact identity, and release gates | Reusable policy and evidence integrations |
| Release engineering | Decide whether the exact artifact is eligible to publish | Artifact-bound evidence and replay |
| Product security | Verify critical controls ran on the actual subject | Trusted producer identity and traceable exceptions |
| Audit stakeholder | Reconstruct why a change was accepted | Durable evidence and accountable approvals |

These are hypotheses, not confirmed segments.

## First vertical slice

Python pull request → API/change impact → policy obligations → established verification tools → exact sdist/wheel subject binding → release assurance dossier.

The current chipcup code is a starting reference, not proof that this workflow exists.

## Deferred expansions

A second-language pilot, organization policy, expiring waivers, deployment/runtime evidence, more CI providers, advisory AI investigation, and hosted history are later decisions gated on demonstrated value and demand.

## First-release non-goals

- general-purpose autonomous software engineer;
- replacement for GitHub, Qodo, Graphite, Sourcegraph, CodeQL, Launchable, or GUAC;
- general code-search engine or vulnerability scanner;
- universal graph database;
- predictive test selection that removes required suites;
- runtime monitoring and incident management;
- legal/compliance certification;
- opaque quality score;
- AI-controlled merge, publication, or policy waiver.

## Business hypotheses

A plausible first experiment is an open-source local engine, evidence schema, CLI, and baseline adapters. Hosted history and policy management should be added only if repeated use requires centralized governance. Private deployment requires real demand and a dedicated security design.

Unknowns include willingness to install another GitHub app, workflow maintenance burden, evidence storage/compute cost, false-positive review load, procurement, and whether incumbents already solve the problem.

## Validation questions

Which decisions are hard to reconstruct? Which evidence is fragmented or untrusted? What escaped defect followed from stale or wrong-subject checks? Who owns policy and exceptions? What is today's review/CI cost? What minimum integration produces value? Would teams adopt a local CLI before a hosted service? What retention and source access constraints apply?

## Success criterion

Proceed beyond the Python slice only if paired experiments show reliable, actionable evidence or decision-quality gains over a declared baseline, without unacceptable false blocks, false passes, latency, privacy risk, or operating burden.
