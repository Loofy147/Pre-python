# Adversarial architecture and implementation review

**Review date:** 2026-11-05  
**Source baseline:** main commit 7ef2c82fb2ebdf2e08376b154bd6e9f112b6a5ca  
**Previous documentation head:** 0560c36078e7c477f1a7e12958fb4c72932c044d

## Decision

**CONDITIONAL GO:** proceed with a narrow Python change-to-release assurance experiment.  
**NO-GO for now:** do not implement a general autonomous engineering or runtime intelligence platform as the first product.

The differentiation hypothesis is cross-tool evidence lineage and replayable policy decisions bound to exact source and artifact subjects. It remains unproven.

## Review method

The review considered repository source and workflow files, existing documentation, the separate exit-code PR and its CI metadata, and public product/standards documentation.

Evidence labels:
- FACT: directly observed in source, workflow, PR, CI metadata, or cited public documentation.
- INFERENCE: supported conclusion, not directly measured.
- HYPOTHESIS: requires experiment or customer validation.
- OPEN: not established.
- CONTRADICTED: inconsistent with the inspected repository state or another claim.

The competitor review is not exhaustive or hands-on.

## Findings by dimension

| Dimension | Finding | Decision |
|---|---|---|
| Product scope | Previous vision combined change analysis, test optimization, repair agents, runtime assurance, graph infrastructure, and governance | Narrow to one Python change-to-release slice |
| Differentiation | PR review, code graphs, security scanning, and predictive testing already exist | Benchmark only cross-source evidence and policy replay |
| Impact coverage | Static analyzers miss dynamic behavior, generated code, runtime configuration, and unsupported constructs | Expose coverage and uncertainty |
| Obligation planning | LLM-generated obligations may omit controls or follow injected instructions | Versioned policy packs own obligations |
| Verification | A smaller predicted test subset may miss regressions | Test ranking only; required suites remain required |
| Evidence identity | Branch names, PR numbers, filenames, and mutable URLs are not immutable subjects | Bind commits, trees, artifacts, environment, tool, and policy |
| Evidence trust | A hash proves bytes, not origin | Verify producer and builder identity |
| Decision semantics | One score hides incompatible dimensions and uncertainty | Keep claims, evidence, rule results, severity, trust, and decisions separate |
| Architecture | Current runtime and GateReport paths differ | Unify before expanding |
| Graph storage | Graph infrastructure adds cost and does not create trustworthy relations | Start with typed records and explicit edges |
| Language expansion | Python alone cannot prove a generic adapter abstraction | Pilot one contrasting language later |
| Security | PR content and candidate build/test code are attacker-controlled | Separate orchestration from disposable unprivileged execution |
| AI agents | Autonomous actions expand prompt-injection and permission risk | Advisory and approval-gated only, later |
| Runtime assurance | Monitoring and incident response are separate operational domains | Defer |
| Operations | Tool fan-out, stale caches, retries, and merge queues affect correctness | Idempotency, strict cache keys, and subject revalidation |
| UX | Excessive comments and unexplained blocks erode trust | One concise dossier with linked evidence and explicit unknowns |
| Commercial | Buyer, willingness to install, pricing, and support load are unknown | Validate with design partners |
| Compliance | Evidence can support an audit but does not establish legal compliance | No certification or legal guarantee |

## Market-overlap result

Public documentation shows established capabilities in GitHub Copilot PR review/approval assessment, Qodo multi-repository context and review rules, Graphite AI reviews, Launchable predictive test selection, Sourcegraph code graphs, GUAC supply-chain graphs, and GitHub code scanning.

This contradicts a generic AI reviewer, code graph, predictive testing engine, or vulnerability scanner as a standalone differentiator. It does not prove that no vendor solves the exact cross-lifecycle evidence problem. A hands-on paired benchmark remains necessary.

## Technical conclusions

### Impact analysis is never complete by default

Python reflection, dynamic imports, decorators, generated source, plugin discovery, monkey-patching, native extensions, and environment-dependent behavior can defeat static reachability. Unsupported scope must remain visible. No graph edge means “not observed by this analyzer”, not “proven unaffected”.

### Obligations must be policy-owned

A model may suggest that a change touches authentication, migration, API, dependency, or build behavior. That classification is advisory. A deterministic, versioned policy pack decides which obligations are mandatory.

### Evidence must match the artifact being judged

A source-code test result does not automatically apply to a built wheel. Bind results to exact commit/tree/artifact digests, tool/configuration, environment, and producer identity. Build isolation requires trusted provenance, not a caller flag.

### Assurance is not formal verification

A dossier records which obligations were checked under a stated model. It does not prove arbitrary software correct, secure, or vulnerability-free.

## Proposed target architecture

1. Change intake and immutable subject resolver.
2. Change normalizer and classifier.
3. Impact analyzers plus coverage/uncertainty evaluator.
4. Deterministic obligation compiler.
5. Verification adapter runner.
6. Content-addressed evidence store and relationship index.
7. Policy evaluator and exception ledger.
8. Assurance dossier and source-control status check.
9. Optional advisory agent outside the trusted decision path.

A universal graph database is not required. Start with typed evidence records and explicit relations.

## Security review conclusion

A pull request can modify source code, tests, build configuration, dependencies, project metadata, and CI workflows. These may execute code or attempt to read credentials.

Candidate code must not execute inside the privileged orchestrator. Untrusted PR execution must not receive publishing credentials. Privileged status publication must be separated from candidate execution. A remediation agent must not possess merge, release, policy-waiver, or signing authority.

## Operations and reliability review

Required design properties:
- idempotent jobs keyed by immutable inputs;
- bounded retries, timeouts, and resource limits;
- cache keys including source/artifact, tool, configuration, environment, policy, and trust versions;
- rerun lineage instead of overwriting old evidence;
- revalidation on PR head changes and merge-queue commits;
- explicit states for unavailable, failed, incomplete, stale, and untrusted analyzers;
- no conversion of a missing mandatory check into a pass.

## PR #4 exit-code review

PR #4 remains separate and open. Its head commit f3ac230a077f532d1dc3bf5edad022d7303653b passed configured CI run 42058135115. That proves its configured tests ran, not that the public contract is semantically correct.

Concerns:
- its type-surface exit code implies stronger semantics than current stub declaration/file-presence checks establish;
- fixture categorization uses string matching against issue text, which should not be authoritative;
- exit precedence needs a policy rationale and must not be confused with numeric severity;
- missing/unverified semantics should derive from one versioned report contract;
- reviewed main still has the 0/1/3 CLI behavior, plus argparse usage errors.

Recommendation: reconcile the exit-code proposal with actual report and capability semantics before treating it as stable. This documentation change does not modify or merge PR #4.

## Priority result

| Priority | Work | Reason |
|---|---|---|
| P0 | Fix false-pass paths and unify current execution semantics | Do not turn an unreliable prototype into a gate |
| P0 | Define subject, evidence, and policy contracts | Every adapter depends on these identities |
| P1 | Complete Python PR-to-artifact vertical slice | Tests the smallest valuable product |
| P1 | Comparative benchmark against a competent baseline | Establishes whether differentiation exists |
| P2 | Second-language portability experiment | Tests rather than assumes the abstraction |
| P3 | Hosted governance, runtime evidence, and advisory agent if demanded | Expansion after demand and core proof |
| Deferred | Universal graph, autonomous merge/release, general runtime monitoring | Distinct high-cost product domains |

## Final result

Proceed with P0 and the Python vertical slice. Do not claim production readiness, market uniqueness, language neutrality, formal proof, autonomous engineering, or runtime assurance until independent artifacts and experiments support those claims.
