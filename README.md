# chipcup

**chipcup** is a typed Python package that makes seven packaging contracts executable. Its reference object is a chipped teacup: the specimen is shared, but each inspection boundary has its own rules and evidence.

## Install

    python -m pip install chipcup

For a source checkout:

    python -m pip install -e ".[test]"
    python -m pytest

Python 3.10 or newer is required. The distribution is versioned independently using PEP 440. Version 0.1.0 is an initial alpha release.

## Seven boundaries

| Subpackage | Governing system | Executable responsibility |
|---|---|---|
| imports | Python import machinery, sys.modules, PEP 420, PEP 562 | Module identity, namespace plugin discovery, deferred entry-point loading and a lazy compatibility shim |
| versions | PEP 440 | Version parsing, ordering and specifier satisfaction |
| markers | PEP 508 | Environment and extras evaluation |
| types | PEP 484/544/695 and PEP 561 | Structural receipt contracts, generic variance and explicit Any detection |
| build | PEP 517/621 | Inspection of wheel and sdist metadata and license-file members |
| licenses | PEP 639 and SPDX expressions | Expression syntax, LicenseRef mapping and artifact file coverage |
| deprecations | PEP 387 | Warning schedules, soft deprecations and lazy compatibility resolution |

The package uses setuptools.build_meta as its PEP 517 backend and static PEP 621 metadata. Build isolation is exercised in CI. Dynamic metadata is intentionally not enabled in this first release.

## Quick example

    from chipcup.versions import VersionPolicy, parse_version
    from chipcup.markers import MarkerPolicy

    release = parse_version("1!2.0rc1")
    policy = VersionPolicy(">=1!2.0rc1,<2!0")
    assert policy.accepts(release)
    assert MarkerPolicy('python_version >= "3.10"').evaluate()

The package root is intentionally lazy:

    import chipcup
    parse_version = chipcup.parse_version

A deprecated root alias remains available during the initial compatibility window and emits DeprecationWarning.

## The release gate

The top-level gate coordinates all seven subpackages in order: module identity, version satisfaction, environment selection, structural type receipt, artifact consistency, license coverage, and deprecation history. It stops at the first failed boundary. See docs/ARCHITECTURE.md for the hand-offs and import-cycle controls.

The gate is a policy check, not a substitute for CI, a trusted build service, legal review, or a full static type checker. SPDX syntax is parsed locally; identifier validity against the complete SPDX License List remains an explicit follow-up.

## Formal boundary, not a universal schema

The package does not claim that its contracts cannot be serialized. It claims that one representation with one evaluation semantics cannot replace the separate evaluators and state sources: live module identity, PEP 440 ordering, marker environments, static typing, build artifacts, SPDX licensing, and release history. A manifest may index them, but cannot flatten their semantics.

## Open questions

The unresolved design questions are intentionally open-ended and recorded in docs/OPEN_QUESTIONS.md. They are not silently converted into defaults.

## License

MIT. See LICENSE.
