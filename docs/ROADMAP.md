# Roadmap and implementation gates

## Rule

A gate closes only when source, tests, reproducible evidence, and a named commit demonstrate the exit criteria. No dates are assigned.

## Gate 0 — Repair and reconcile the Alpha

Work:
- reject NaN, infinity, booleans, malformed geometry, and invalid numeric inputs;
- bound archive member count/size; reject duplicate normalized paths and unsafe members;
- replace caller build-isolation Boolean as a trust mechanism with explicit unverified assertion until attestation verification exists;
- compare canonical package manifests/hashes across source, sdist, and wheel;
- install and audit the exact wheel built from the sdist in a clean environment;
- remove unsupported stub claims or implement and test semantic agreement;
- fix marker validation for selected versus unselected rows;
- authenticate and bind warning observations; reject duplicate/inconsistent/stale records;
- derive release version from tag and compare with project/artifact identity;
- unify runtime.py and gate.py execution/report semantics;
- reconcile PR #4 exit-code contract with actual receipt semantics;
- preserve limitations in documentation.

Exit: regression tests for known false-pass cases, exact artifact validation, fail-closed defaults, one authoritative report contract, tag mismatch rejection, and full CI on the final source commit.

## Gate 1 — Versioned evidence and policy contracts

Create source/artifact subjects, evidence envelope, validity/trust/completeness axes, typed relations, claim and obligation records, append-only corrections/revocation, deterministic policy bundles, and replayable decisions.

Exit: schema/canonicalization tests, wrong-subject and tamper rejection, preserved corrections, deterministic replay, and no secrets in evidence.

## Gate 2 — Python change-to-release vertical slice

Build an exact base/head resolver, diff/API classification, Griffe adapter, dependency/build/package classification, impact coverage, deterministic policy obligations, pytest/mypy/package/provenance/SPDX/archive adapters, exact artifact digest, clean exact-wheel install, dossier, and GitHub check.

Exit: complete sample project flow, evidence-linked obligations, no ALLOW for missing/wrong evidence, exact artifact verified, limitations surfaced, and usable latency/output.

## Gate 3 — Comparative proof of value

Pre-register baseline/mutants, evaluate paired immutable subjects, measure precision/recall, obligation coverage, critical false-passes, false-blocks, costs, perform ablations, obtain independent reproduction and user feedback.

Exit: incremental value over competent baseline, no critical false-pass in declared corpus, acceptable false-block and CI overhead, developers understand value, credible adoption path.

If this fails, reduce scope, integrate with existing platforms, or stop product expansion.

## Gate 4 — Portability experiment

Choose one second language from real user demand. Implement a language-specific API/dependency/build/artifact adapter with documented semantics, blind spots, and regression corpus.

Exit: same evidence contract works without false equivalence and benchmark justifies maintenance cost.

## Gate 5 — Multi-repository governance

Consider policy composition, expiring waivers, more CI providers, durable shared history, optional graph indexing, and private/self-hosted operation.

Exit: demand, tenant/security model, least privilege, operational ownership, and retention are established.

## Gate 6 — Advisory agent and deployment/runtime evidence

An agent may investigate or propose patches but cannot alter policy, approve exceptions, merge, publish, or certify itself. Deployment/runtime evidence may be linked later; monitoring and incident response require a separate scope decision.

## First-release non-goals

- replacing GitHub, GitLab, Qodo, Graphite, Sourcegraph, CodeQL, Launchable, or GUAC;
- general autonomous engineer;
- universal graph;
- every language;
- predictive subsets replacing required tests;
- runtime monitoring or incident response;
- legal compliance guarantee;
- opaque quality score;
- dashboard or hosted multi-tenant service before demand.

The current 0.1.0 Alpha is a research prototype. A green repository CI run is not a product-release gate.
