# Integrations and ecosystem boundaries

## Principle

chipcup should coordinate established tools, not clone them. An integration is valuable only when it provides evidence that chipcup can bind to an exact release subject and evaluate under explicit policy.

Every adapter must record tool name/version, invocation, input subject digests, environment, output digest, raw output reference, normalized findings, and limitations. An adapter failure or unavailable dependency must not be silently converted to PASS.

## Existing ecosystem

| Tool or standard | Existing responsibility | Planned chipcup role | Current integration status |
|---|---|---|---|
| Griffe | Reads Python API structure and compares snapshots for breaking changes | Produce API-change evidence for exact base/candidate refs and connect findings to deprecation policy | NOT IMPLEMENTED |
| pydistcheck | Inspects distribution archives for packaging, portability, and content issues | Reuse archive-quality findings and bind them to sdist/wheel digests | NOT IMPLEMENTED |
| Twine | Its check command validates rendering of distribution long descriptions | Keep description-rendering validation as a specialist CI check; do not claim it proves artifact integrity | Invoked by CI, not an evidence adapter |
| packaging | Implements PEP 440 versions, specifiers, and PEP 508 markers | Use its semantics for deterministic version and marker evidence | Used by current code |
| SPDX License List | Authoritative versioned list of license and exception identifiers | Validate syntax plus identifiers against a pinned list snapshot | NOT IMPLEMENTED; current custom parser is incomplete |
| PyPI PEP 740 attestations | Provides signed attestation records associated with uploaded distribution files | Verify attestation subject digest, signer/workflow identity, predicate, and trusted policy | NOT IMPLEMENTED |
| SLSA provenance | Describes build provenance and the process that produced an artifact | Validate the provenance predicate and trusted builder identity | NOT IMPLEMENTED |
| mypy | Static type checker | Run as a development quality check; do not substitute it for artifact or runtime API evidence | Used in CI on one Python lane |
| pytest | Executes project tests | Capture result and environment as CI/test evidence | Used by CI |

## Adapter priorities

### 1. API snapshot adapter

Use Griffe to load the base and candidate API snapshots, preferably from immutable commits or tags. Preserve:

- base and candidate commit IDs;
- package/module search roots;
- tool version and configuration;
- serialized API snapshot digests;
- complete breakage records;
- exclusions and overrides.

Map each finding to the public-API policy. A detected breakage is not automatically a release denial; an approved deprecation path or declared major-version policy may alter the decision.

Griffe documentation: https://mkdocstrings.github.io/griffe/guide/users/checking/

### 2. Distribution inspection adapter

Use pydistcheck and appropriate wheel/sdist inspectors to detect packaging and portability defects. Keep the raw findings and tool version, then cross-check their artifact subject digests against the exact artifacts being evaluated.

Do not duplicate every archive rule in chipcup unless there is a demonstrated gap or a required cross-artifact relationship.

pydistcheck documentation: https://pydistcheck.readthedocs.io/en/latest/how-to-test-a-python-distribution.html

### 3. Description validation adapter

Twine check should remain responsible for the rendering check it provides. It does not prove complete package metadata correctness, source/wheel parity, or provenance.

Twine documentation: https://twine.readthedocs.io/en/stable/

### 4. SPDX validation adapter

Use a versioned SPDX License List snapshot. Record the list version and digest used by each decision. If the identifier or exception is not in the pinned list, fail or require an explicit LicenseRef mapping according to policy.

If the required list version cannot be obtained or verified, return UNVERIFIED rather than accepting a syntactically plausible identifier.

SPDX list: https://spdx.org/licenses/  
Machine-readable list information: https://github.com/spdx/license-list-data

### 5. Provenance adapter

Consume PyPI's Integrity API and verify accepted PEP 740 attestations. For SLSA provenance, validate the subject digest, builder identity, source repository, source revision, workflow identity, and predicate requirements.

A successful signature check is not sufficient if the identity is not trusted by policy. A valid attestation for a different artifact digest is not evidence for the candidate artifact.

PyPI attestations: https://docs.pypi.org/attestations/  
PyPI provenance: https://docs.pypi.org/using-pypi/package-security/provenance/

### 6. CI platform adapter

Capture immutable workflow and job identities, commit SHA, job result, matrix environment, artifact IDs/digests, and timestamps. Avoid treating a branch name or mutable job URL as a complete subject identity.

The first provider can be GitHub Actions. Keep the normalized evidence contract provider-neutral so that GitLab or other build systems can be added later.

## Adapter interface requirements

A proposed adapter should expose:

- capability and supported schema versions;
- input subject requirements;
- deterministic invocation parameters;
- output schema validation;
- raw-output persistence and digest;
- normalized findings;
- provenance/trust status;
- timeout and resource policy;
- explicit failure and unavailable states.

Adapters must not own final release policy. They provide evidence; the policy engine decides whether that evidence satisfies the project's requirements.

## Integration acceptance criteria

An integration is not complete merely because a command runs. It must:

1. bind output to exact source/artifact subjects;
2. reject mismatched or missing inputs;
3. preserve raw output and tool version;
4. normalize findings without losing source details;
5. distinguish tool failure, unavailable tool, no findings, and incomplete scan;
6. have tests using positive, negative, malformed, and mismatched-subject outputs;
7. provide a reproducible integration example.
