# Change taxonomy and evidence map

**Status:** TARGET taxonomy. It is not a claim that every category is currently analyzed.

## Lifecycle view

| Lifecycle point | Questions | Candidate evidence |
|---|---|---|
| Intent / specification | What behavior or contract is meant to change? | Issue, design decision, API/schema contract |
| Source change | What changed in code and configuration? | Base/head diff, symbol and dependency analysis |
| Verification | Which obligations were checked? | Tests, static analysis, security and compatibility results |
| Build | What exact artifact was produced from which inputs? | Build record, artifact digest, provenance |
| Release | Is this artifact eligible under policy? | API history, release chronology, attestations, approvals |
| Deployment | Which artifact/configuration was promoted? | Deployment record, environment/configuration digest |
| Runtime | Did observed behavior drift or fail? | Traces, metrics, incidents, contract observations |
| Learning | Did the decision correlate with outcomes? | Rework, failure, recovery, reviewer and developer feedback |

The first product slice ends at release-artifact assurance. Deployment and runtime are future evidence sources, not first-release subsystems.

## Change classes

| Class | Examples | Potential impact analysis | Typical obligations | First-slice status |
|---|---|---|---|---|
| Public API / ABI | Removed export, changed signature/default, module move | API snapshots, downstream imports, documented contracts | Compatibility diff, deprecation chronology, version policy, consumer tests | CORE |
| Internal source / behavior | Algorithm, control flow, error handling | Symbol references, dependency relations, changed paths | Unit/integration/regression/property tests | LIMITED |
| Dependencies | Added, removed, upgraded package, lockfile | Direct/transitive graph, affected modules, licenses/advisories | Resolution, reproducibility, advisory and license review | CORE |
| Build and packaging | Backend, build config, package data, entry points | Build graph, archive members, metadata and artifact identity | Source/artifact parity, metadata, provenance | CORE |
| License and provenance | License expression/file, publisher/workflow identity | Affected distribution members and producer identity | Pinned license data, subject/signature checks | CORE |
| Runtime configuration | Environment variables, defaults, feature flags | Consumers, deployment profiles, config schema | Parsing, compatibility, secret and environment tests | LATER |
| Infrastructure / IaC | Terraform, Kubernetes, IAM, network policy | Resource graph, trust boundary, permission blast radius | Policy-as-code, plan review, least-privilege checks | LATER |
| Data schema / migration | SQL, event schema, serialization | Producers/consumers, migration order | Forward/backward compatibility, rollback, data integrity | LATER |
| Security / identity | Authn/authz, secrets, crypto, trust policy | Privileged paths, identities, data flows | Security tests, scanner evidence, threat review | LATER; high risk when applicable |
| CI / workflow / release automation | Actions, scripts, token scopes, deploy workflows | Workflow graph, permissions, artifact flow | Pinned actions, permission and trigger review | CORE for project workflows |
| AI system configuration | Prompts, models, tools, agent policy, retrieval index | Tool reach, data sources, model versions, permissions | Prompt-injection and tool-policy tests, evaluation, human approval | LATER |
| Documentation / contract | Docs, OpenAPI, generated client, schema | Cross-reference and code/spec consistency | Link/schema/generated-output checks | LIMITED |
| Deployment / rollout | Image, manifest, traffic weight | Artifact and configuration identity | Digest, approval, health and rollback policy | DEFERRED |
| Runtime behavior | Latency, reliability, data integrity | Telemetry and change-to-deployment lineage | SLO and contract monitoring, incident linkage | DEFERRED |

CORE means included in the first vertical-slice plan, not implemented. LATER and DEFERRED require a fresh scope and security review.

## Obligation mapping

A classifier emits proposed labels with:
- source signal and exact file/symbol/rule;
- classifier name and version;
- supporting evidence;
- ambiguity/confidence only as advisory metadata;
- unsupported constructs and exclusions;
- human correction history.

The policy engine—not the model—decides which obligations follow.

Examples:
- removed public function → compatibility and possible deprecation-history obligations;
- dependency lockfile change → resolution, vulnerability/advisory, license, and reproducibility obligations;
- build configuration change → archive inclusion, metadata, isolation, and provenance obligations;
- workflow permission change → privilege and trust-boundary obligation;
- database migration → compatibility, ordering, rollback, and data-integrity obligations, outside the first release.

## Coverage states

Every analysis result declares:
- **COMPLETE_WITHIN_DECLARED_MODEL:** all declared inputs and supported constructs were analyzed; this does not claim to model all runtime behavior.
- **PARTIAL:** some inputs or constructs were excluded or unsupported.
- **UNKNOWN:** adequate scope cannot be established.
- **NOT_APPLICABLE:** the analysis is irrelevant, with a recorded rationale.

PARTIAL or UNKNOWN may trigger broader tests or human review. Neither means “no impact”.

## Python-specific blind spots

The initial analyzer must handle or explicitly report limitations for:
- reflection and dynamic attribute lookup;
- importlib and dynamic module loading;
- generated source and code generation;
- decorators and metaclasses that alter runtime behavior;
- namespace packages and entry-point discovery;
- monkey-patching and runtime registration;
- native extensions and platform-specific build products;
- environment-dependent configuration;
- tests dependent on external services or runtime fixtures.

An analyzer must not certify a behavior absent when it cannot observe that behavior.

## Multi-language extension rule

A second language is an experiment to test portability. Do not generalize language-specific APIs into a universal interface too early.

A language adapter declares supported language/version, parser/compiler/build-tool versions, project layouts, dynamic features, API/ABI model, dependency/artifact model, known blind spots, exact subject binding, and a semantic regression corpus.

A second language is accepted only when it can produce the same evidence contract without falsely equating different language semantics.
