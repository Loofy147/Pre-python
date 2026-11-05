# Python API reference

## Scope and stability

This document describes the public exports present in the reviewed 0.1.0 Alpha source. The package is experimental. Public exports are not yet a stable compatibility promise, and the current GateReport path is not the same execution path as the receipt-cycle CLI.

The repository is named Pre-python. The distribution and import package are named chipcup.

## Root package

The root package exports:

- __version__
- VersionPolicy
- parse_version
- MarkerPolicy
- evaluate_release
- GateRequest
- GateReport
- legacy_parse_version

VersionPolicy and parse_version are re-exported from chipcup.versions. MarkerPolicy is re-exported from chipcup.markers. GateRequest, GateReport, and evaluate_release are re-exported from chipcup.gate.

The exports are resolved lazily through module-level __getattr__. Accessing legacy_parse_version emits DeprecationWarning on every attribute access by design; the alias is not cached.

## Version API

### VersionPolicy

VersionPolicy is initialized with a PEP 440 version specifier string.

The current methods are:

- accepts(candidate, prereleases=None): tests whether a candidate version satisfies the policy.
- select_matrix_rows(candidate, rows): filters marker rows by each row's version specifier.
- audit_distribution(imported_version, installed_version, specifier=None): compares imported and installed versions and checks specifier membership.

### parse_version

parse_version(value) delegates parsing to packaging.version.Version and returns a Version object.

Example:

    from chipcup import VersionPolicy, parse_version

    candidate = parse_version("0.1.0")
    policy = VersionPolicy(">=0.1.0,<1.0.0")
    assert policy.accepts(candidate)

## Marker API

### MarkerPolicy

MarkerPolicy is initialized with a PEP 508 marker expression and optional extras.

Current methods:

- evaluate(environment=None): evaluates the expression against packaging's default environment merged with the supplied environment and configured extras.
- admits(candidate, protocol=AuditReceipt, environment=None): evaluates the marker and checks a runtime-checkable protocol.

### evaluate_matrix

evaluate_matrix(rows, environment=None) evaluates a sequence of marker rows and returns MarkerMatrixResult.

MarkerRow, MarkerEvaluation, and MarkerMatrixResult are exported by chipcup.markers. Matrix selection and scope are experimental; see POLICY_MODEL.md for the intended future policy contract.

## Legacy GateReport API

chipcup.gate currently exports:

- GateRequest
- GateReport
- evaluate_release

GateRequest identifies sdist and wheel paths, a project root, package name, version specifier, marker rows, environment, license references, deprecation schedules, published releases, and warning observations.

evaluate_release(request) executes the separate GateReport evaluation path. GateReport retains distinct imports, versions, markers, types, build, licenses, and deprecations results and exposes passed and to_dict().

Important: this is a parallel path to runtime.run_receipt_cycle, which is used by the CLI. They have different composition and output structures. Do not treat them as equivalent. Unifying them is a P0 architecture task.

## Evaluator subpackages

The following table summarizes the current __all__ exports by domain. They are experimental implementation APIs, not a stable external adapter interface.

| Module | Exported surface | Purpose |
|---|---|---|
| chipcup.build | ArtifactComparison, ArtifactInfo, accept_type_receipt, compare_artifacts, inspect_artifact, require_license_coverage, close_version_cycle, degraded_build_receipt, evaluate_artifact_receipt, measure_notch, read_artifact_member, validate_notch_profile | Artifact inspection, selected metadata comparison, geometry, and build receipts |
| chipcup.licenses | DEFAULT_LICENSE_REFS, DEFAULT_LICENSE_REF_SUBJECTS, LicenseAuditResult, LicenseNode, check_artifact_license_coverage, check_license_files, license_references, parse_license_expression, validate_compatibility, degraded_license_receipt, receipt_from_build | License expression parsing and file/subject coverage |
| chipcup.types | AuditReceipt, BuildEvidence, Reader, TypeAuditResult, accepts_protocol, audit_public_surface, audit_stub_sets, is_any, load, prepare_build_receipt, degraded_type_receipt, receipt_from_license | Runtime protocol experiments, stub set declarations, and type receipt creation |
| chipcup.markers | MarkerEvaluation, MarkerMatrixResult, MarkerPolicy, MarkerRow, evaluate_matrix, degraded_marker_receipt, receipt_from_types | PEP 508 marker evaluation and marker receipt creation |
| chipcup.deprecations | DeprecationAuditResult, DeprecationSchedule, WarningObservation, capture_warning_observation, validate_license_dependencies, validate_schedules, warn_deprecated, degraded_deprecation_receipt | Warning capture and project-defined warning/removal schedule validation |
| chipcup.imports | EntryPointRef, ImportAudit, ModuleIdentity, assert_module_identity, audit_module, discover_compatible_entry_points, load_module, module_identity, degraded_import_receipt, receipt_from_deprecations | Module identity, public-name checks, namespace and entry-point discovery |
| chipcup.versions | VersionAudit, VersionPolicy, parse_version, degraded_version_receipt, receipt_from_imports | PEP 440 version policy and version receipt creation |

## Receipt contracts

chipcup._contracts is an internal shared module containing AuditVerdict, ReceiptState, BoundaryReceipt, AuditReceipt, BuildEvidence, MatrixRow, and WarningObservation.

These types support the current internal receipt cycle. They are not yet a versioned external evidence schema. BoundaryReceipt is frozen at the dataclass level, but its evidence mapping is not deeply immutable.

runtime.run_receipt_cycle is the current receipt orchestrator used by the CLI. It is an internal execution path, not a declared stable public API.

## CLI versus Python API

For command-line use, see CLI_REFERENCE.md. The CLI requires sdist, wheel, and warning-evidence inputs. It returns a JSON receipt report and uses the current exit behavior described in that reference.

The public root evaluate_release API uses the legacy GateReport path. The CLI uses runtime.run_receipt_cycle. Do not mix their result objects or assume the same policy is evaluated.

## Compatibility policy

Until the project publishes a stable API policy:

- treat 0.1.0 APIs as Alpha;
- pin chipcup to a known version when using it in automation;
- depend on the CLI only where the exact JSON and exit behavior are tested;
- do not depend on internal modules such as _contracts or runtime;
- expect the GateReport API and receipt-cycle report to be reconciled before a stable release.

A future stable API should be built around the versioned evidence and policy contracts, not around every experimental helper currently present.
