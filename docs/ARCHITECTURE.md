# Architecture and evidence boundaries

## Purpose

chipcup audits a distribution's public-API lifecycle. Each subpackage has a distinct evaluator and a concrete responsibility. The report preserves seven independent result records; the Boolean `GateReport.passed` is only a release-gate convenience.

## Dependency graph

The package contracts are connected as follows:

```text
imports → versions → markers → types → build → licenses → deprecations
                            types --lazy--> build
```

- **imports → versions (static):** entry-point distribution versions are filtered by a PEP 440 `VersionPolicy`; the import audit records canonical module identity from `sys.modules`.
- **versions → markers (static):** the installed distribution version selects marker-matrix rows whose row-level specifiers admit the release.
- **markers → types (static):** each true marker row selects a declared protocol/stub contract set. An `extra == "gpu"` row is false when no GPU extra is requested.
- **types → build (lazy):** build needs the runtime `AuditReceipt` protocol, while types exports `BuildEvidence`. The types module exposes that symbol via PEP 562 `__getattr__`; build imports `AuditReceipt` at module load, and types resolves `BuildEvidence` only when requested. This is the actual import-cycle breaker.
- **build → licenses (static):** build extracts the sdist/wheel member lists and Core Metadata. Licenses consumes those manifests; it does not ask the backend to rebuild them.
- **licenses → deprecations (static):** schedules that depend on a custom LicenseRef are blocked when its text cannot be resolved to a declared `License-File`.
- **deprecations → audit entry point (process composition):** deprecations does not import imports. The installed `chipcup.audit` console entry point runs the full audit in a fresh process and closes the operational workflow without adding an import edge back into the module graph.

The arrows denote code-level data dependencies, not claims that each PEP explicitly mandates these package boundaries.

## Seven evaluators and their verdict shapes

| Boundary | State/evaluator | Evidence retained |
|---|---|---|
| imports | Python import machinery and `sys.modules` | Module name, object identity, origin, namespace search locations, repeat-import identity, unresolved public exports |
| versions | PEP 440 `Version` and `SpecifierSet` | Imported version, installed version, comparison relation, specifier, membership result |
| markers | PEP 508 `Marker` and explicit environments | Per-row expression, selected Boolean, requested extra, chosen type-contract set, log line |
| types | PEP 484/544/695 contracts and mypy | Selected protocol sets, unknown sets, exported names, missing wheel names, variance result |
| build | PEP 517/621 backend and archive metadata | sdist/wheel hashes, project identity, requirements, top-level packages, public `__all__`, backend, dynamic-version state |
| licenses | PEP 639 metadata plus SPDX grammar and archive member names | License expression, LicenseRef mapping, source-file presence, per-artifact coverage, dependency issues |
| deprecations | Emitted warning observations and project release history | Required marker rows, release of first observed warning per row, effective global start, missing rows, removal-window verdict |

These verdicts are not one algebra. Version comparison is ordered; specifier membership and marker evaluation are Boolean; typing is a static judgment; artifact comparison is a set of consistency predicates; license evaluation combines Boolean expression syntax and file coverage; deprecation validation depends on observed events and release chronology. Serializing them into JSON is useful, but reducing them to one score would remove the failure mode and provenance a maintainer needs to investigate.

## Release gate invariants

The release gate currently enforces these checks:

1. `chipcup.__version__` and the installed `importlib.metadata.version("chipcup")` compare equal under PEP 440.
2. The installed version satisfies the audit's configured version specifier.
3. Only marker rows whose own PEP 440 row specifier admits the release are evaluated.
4. Every true row contributes its named protocol/stub contract set.
5. Literal package `__all__` surfaces from source and wheel are compared by module name; a typed name absent from the wheel fails the type boundary.
6. The sdist and wheel agree on project name, version, `Requires-Dist`, top-level package names, public `__all__` surfaces, and PEP 639 license metadata.
7. The sdist carries a static `project.version`, or the build is rejected for dynamic version metadata until deterministic hook validation exists.
8. Every declared `License-File` exists in the source tree and is covered in both archives. Every supplemental LicenseRef maps to a declared file which ships in both archives.
9. A removal schedule cannot start until an actual `DeprecationWarning` is observed for every required, selected marker row.

The CI workflow builds an sdist, then builds the wheel **from that sdist**, validates both with Twine, and runs `chipcup.audit` against those exact artifacts.

## License semantics: distribution expression vs file grant

The package's distribution-level PEP 639 expression is `MIT`. The fixture also has a custom alternative grant recorded in `LICENSES/Fixture-Dual.txt`, with the project-specific supplemental mapping:

```text
LicenseRef-Fixture-Dual → LICENSES/Fixture-Dual.txt
```

The validator checks the mapped text and file coverage. It does not pretend that a single distribution-level `License-Expression` assigns a different expression to an individual file. Core Metadata's `License-Expression` applies to the archive metadata that contains it; file-level scoping is not encoded by adding a `LicenseRef` to the package expression.

## Deprecation timing

PEP 387 is the compatibility policy for CPython. It is not a rulebook that imposes removal schedules on third-party distributions. chipcup therefore labels its own schedule as a project policy informed by PEP 387.

For a configured set of required marker rows, chipcup records a warning only when the marker selected the row and the deprecated alias actually emitted `DeprecationWarning`. The effective start is the latest of the first observed warning releases across all required rows. A row that never emitted the warning prevents the removal clock from starting.

For hard removals, chipcup's current project policy requires at least one distinct published project minor release after that effective start and before removal. This is a chipcup policy choice, not PEP 387's CPython-specific timing rule. Soft deprecations do not schedule automatic removal.

A marker result generated by evaluating an environment dictionary is not proof of an actual platform warning. Evidence intended to justify a real removal should come from the corresponding platform CI job and be retained with its release identity. The current gate supports supplied `WarningObservation` records; it must not manufacture missing platform evidence by treating simulated environments as executions.

## Reducibility and known reductions

The seven systems do not replace each other:

- Import object identity does not define PEP 440 ordering.
- A PEP 440 specifier cannot state a platform predicate such as `sys_platform == "linux"`.
- A PEP 508 marker does not express static variance or a type judgment.
- A typing judgment cannot prove build isolation or archive reproducibility.
- A PEP 517 build hook does not encode SPDX license-expression semantics.
- An SPDX expression is not a temporal warning/removal history.
- A deprecation warning class cannot express `sys.modules` identity.

One metadata-level partial reduction is real: a removal target can be represented by a PEP 440 specifier such as `>=2.0`. The remaining deprecation evidence is not reducible to that specifier: it includes whether a warning was actually emitted on required rows, and when.

## Known limits and falsification targets

- SPDX syntax and custom LicenseRef file mapping are checked locally; the complete live SPDX License List is not vendored.
- Wheel metadata does not independently attest the build backend. Building the wheel from the sdist reduces, but does not cryptographically prove, backend provenance.
- The public API check currently compares literal `__all__` exports, not every possible dynamic attribute, entry-point contract, or symbol reachable through reflection.
- Runtime-checkable Protocols are shallow; mypy provides a separate static check. Neither proves semantic correctness of arbitrary third-party implementations.
- A PEP 420 namespace path may contain a shadowing submodule earlier in `sys.path`; a test verifies the observable winner rather than claiming namespace composition removes that risk.
- The default marker matrix is a policy fixture. Add or remove rows only with evidence from supported platforms, extras, and the CI execution matrix.

A boundary should be removed if a regression test demonstrates that another boundary already covers its responsibility without changing the report's meaning. A boundary should be split if its output combines verdicts with incompatible semantics or provenance.
