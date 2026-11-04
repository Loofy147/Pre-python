# Architecture and evidence boundaries

## Package map

The seven subpackages use different state models and evaluators.

1. imports: Python's live import registry, module specs, namespace search locations and entry-point metadata.
2. versions: packaging.version.Version and SpecifierSet, which implement PEP 440.
3. markers: packaging.markers.Marker and the PEP 508 marker environment, including one evaluation per selected extra.
4. types: nominal Python classes, runtime-checkable Protocol contracts, covariant generic readers and a visible Any escape detector. The py.typed marker advertises type information.
5. build: reads actual wheel and sdist members and Core Metadata. The PEP 517 backend is setuptools.build_meta; project metadata is declared statically through PEP 621.
6. licenses: parses the SPDX AND/OR/WITH expression grammar, maps LicenseRef identifiers to files, and checks file coverage in every artifact.
7. deprecations: checks warning and removal releases against explicit release history, and resolves legacy symbols on demand.

## Runtime hand-off cycle

The hand-offs are executable and imports are deferred until a function is called:

- imports.compatible_entry_points delegates version acceptance to versions.
- versions.VersionPolicy.accepts_for delegates environment selection to markers.
- markers.MarkerPolicy.admits delegates structural compatibility to types.
- types.prepare_build_receipt hands a validated receipt to build.
- build.require_license_coverage delegates artifact file coverage to licenses.
- licenses.validate_compatibility delegates removal-window validation to deprecations.
- deprecations.resolve_shim delegates canonical module loading to imports.

Each cross-boundary import occurs inside a function. No subpackage imports its successor at module initialization. The root package uses PEP 562 __getattr__ for lazy exports and the compatibility shim. This is a runtime dependency cycle, not an import-time cycle.

## Non-flattenability claim

A serialized manifest can record inputs and outputs, but cannot replace the independent semantics:

- module identity is process-local and can change when sys.modules is manipulated;
- version comparison is an ordered algebra, not a marker predicate;
- environment markers depend on a particular interpreter and selected extras;
- static type judgments are not runtime checks;
- build outputs have their own files and metadata;
- SPDX expressions encode legal conjunction, alternatives and exceptions;
- deprecation decisions depend on the chronology of published releases.

The release gate composes these evaluators. It does not merge them into one schema.

## Build and metadata

pyproject.toml declares static PEP 621 metadata and uses the PEP 517 setuptools backend. CI builds in isolation. The release gate inspects produced artifacts rather than assuming that a successful source checkout implies a correct wheel.

The first release deliberately avoids dynamic metadata. If dynamic metadata is introduced later, sdist-to-wheel metadata consistency must be demonstrated with tests against both artifacts.

## Known scope limits

The SPDX parser validates expression grammar and LicenseRef file mapping; it does not embed the entire SPDX License List or independently adjudicate license compatibility. A valid expression is not a legal opinion.

The deprecation validator requires published release history to prove the warning window. It does not infer missing releases or treat repeated patch releases as additional minor releases.
