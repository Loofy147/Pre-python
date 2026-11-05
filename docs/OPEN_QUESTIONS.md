# Open decisions and risk register

An item closes only through an explicit decision and its required evidence. Discussion or documentation wording alone does not close an implementation question.

## P0 — Resolve before new product code

1. **Authoritative execution path:** runtime.py is used by the CLI; gate.py exposes a separate GateRequest/GateReport path. Closure: one report contract, migration policy, and end-to-end tests.
2. **Type-surface guarantee:** current checks do not establish .pyi/runtime semantic equality. Closure: remove unsupported guarantee or implement a genuine semantic checker with positive/negative fixtures.
3. **Trusted build provenance:** define issuer, builder, source repository, workflow, subject digest, predicate, offline behavior, and revocation. Closure: positive, negative, mismatch, replay, and untrusted signer tests.
4. **Canonical artifact identity:** define paths, generated files, metadata, platform wheels, licenses, and transformations. Closure: canonical manifest/hash tests.
5. **Untrusted execution:** define worker isolation, egress, secrets, resources, disposal, and output handoff. Closure: malicious build/test/import and exfiltration tests.
6. **First product boundary:** proposed Python PR-to-release assurance. Confirm artifact stage and adoption test on a sample repository.

## P1 — Product correctness and differentiation

7. API baseline semantics: stable tag, prior release, or configured reference; define prerelease/yanked/maintenance behavior.
8. Public API semantics: exports, docs, re-exports, dynamic __getattr__, namespace packages, overloads, stubs, native ABI, behavior contracts.
9. Impact completeness: reflection, generated code, configuration, plugins, dynamic imports, external consumers; fallback when coverage is partial.
10. Policy ownership: who authors, reviews, versions, and retires obligations? Classifier proposals require policy-owner approval.
11. Deprecation chronology: release-event counting, prereleases, yanked/security/maintenance releases, and platform scope.
12. Warning identity: bind observations to commit, release, platform, Python runtime, workflow/job, matrix, and rerun.
13. SPDX lifecycle: pinned License List, update process, offline semantics, and LicenseRef rules.
14. Exception authority: scope, approver, expiry, revocation, precedence, and conflict behavior.
15. Test selection: predictive ranking must not silently remove required tests.
16. Second language: select from actual demand and semantic contrast.

## P2 — Product and operations

17. Storage: when do content-addressed local objects require relational or graph storage?
18. Schema: compatibility, canonical serialization, migrations, and replay.
19. CI providers: GitHub Actions first; define merge-group and provider-neutral identity.
20. Cache invalidation: source, artifact, tool, configuration, environment, policy, and trust inputs.
21. Retention/privacy: stored source/logs/artifacts, secret handling, deletion, historical decisions.
22. Hosted model: hosted history, customer-controlled storage, private deployment, and self-hosting.
23. Support: adapter maintenance, incident response, schema changes, and security reports.
24. Metrics: prevent Goodhart effects and define user outcomes.

## Closed strategic decisions

- Change Assurance is a working direction, not proven market differentiation.
- Python PR-to-release is the first vertical slice, not permanent language scope.
- No universal graph database in the first version; use typed records and explicit edges.
- AI is advisory; it cannot establish trust, waive rules, approve, merge, publish, or certify its own changes.
- Test ranking does not replace policy-required suites.
- Runtime assurance is deferred.
- Do not flatten unlike evidence into a scalar score.
- An assurance dossier is not formal proof or legal compliance certification.
