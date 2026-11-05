# CLI reference

## Scope

This document describes the current CLI on the reviewed main branch. It does not document the richer exit-code mapping proposed in an unmerged pull request.

The installed console command is chipcup.audit. The module form is python -m chipcup.cli.

## Install for development

    python -m pip install -e ".[test]"

This installs the checkout in editable mode and installs the optional test/build tools.

## Audit command

    python -m chipcup.cli --sdist PATH --wheel PATH --warning-evidence PATH [--matrix PATH] [--project-root PATH] [--version-specifier SPECIFIER] [--build-isolation-verified]

### Arguments

| Argument | Required | Current behavior |
|---|---:|---|
| --sdist | Yes | Path to the source distribution archive |
| --wheel | Yes | Path to the wheel archive |
| --warning-evidence | Yes | JSON file or directory containing warning observation JSON files |
| --matrix | No | Marker matrix JSON; defaults to fixtures/audit-matrix.json |
| --project-root | No | Project root for source fixtures and license text; defaults to current directory |
| --version-specifier | No | PEP 440 specifier for the installed distribution; defaults to >=0.1.0,<1.0.0 |
| --build-isolation-verified | No | Caller assertion that the supplied archives were built in isolation; default is false in the CLI |

The build-isolation flag is not a signature, attestation, trusted-build-system check, or cryptographic provenance verifier. A user can supply the flag even if the archives were not built in isolation. The current code then treats the assertion as verified. This behavior must be replaced before production use.

## Marker matrix input

The current fixture is a JSON array. Each row includes a name, PEP 508 expression, stub-set name, PEP 440 version specifier, explicit environment, and optional extra.

Example shape:

    [
      {
        "name": "linux",
        "expression": "sys_platform == 'linux'",
        "stub_set": "posix",
        "version_specifier": ">=0.1.0,<1.0.0",
        "environment": {
          "sys_platform": "linux",
          "platform_system": "Linux"
        }
      }
    ]

The current CLI validates basic field types and passes rows to the receipt cycle. It is not a general supported-platform policy editor. Duplicate row IDs, conflicting scopes, and policy authorization need stronger validation.

## Warning evidence input

The capture script is scripts/capture_warning_evidence.py.

    python scripts/capture_warning_evidence.py --release RELEASE --matrix PATH --output PATH

The release is supplied by the caller. The matrix defaults to fixtures/audit-matrix.json. Output is one JSON observation for the native platform executing the script.

The current observation includes:

- release;
- matrix_row;
- marker_selected;
- emitted;
- warning_count;
- platform.

A warning file is mutable input. The current loader validates basic field types, but it does not cryptographically authenticate the collector, prove the native environment, verify the source commit, bind the event to a published index record, or prevent forged/duplicated observations. Treat it as untrusted evidence.

## Current output

The CLI prints a JSON object containing:

- dependency_order;
- passed;
- receipts.

Each receipt contains boundary, verdict, state, evidence, and issues. The current evidence contents differ by evaluator and are not yet a versioned public JSON schema.

Do not build external automation around undocumented dictionary keys until a versioned schema is introduced.

## Current exit behavior

On reviewed main:

| Exit | Meaning |
|---:|---|
| 0 | The receipt cycle reports passed |
| 1 | A receipt cycle failure or general audit error |
| 2 | argparse usage error |
| 3 | Required module import failed |

This is the current behavior, not a stable future contract. The open pull request proposing detailed exit codes is not merged into the reviewed main commit. Review it against STATUS.md and the product's final decision model before adopting it.

## Current CI workflow

The repository CI:

- installs the checkout in editable mode;
- runs pytest with DeprecationWarning treated as an error;
- checks evaluator import boundaries;
- runs execution-proof tests;
- runs mypy on the configured Python 3.13 lane;
- captures warning evidence on Ubuntu, Windows, and macOS;
- builds an sdist and a wheel from that sdist;
- runs Twine description validation;
- executes the receipt cycle and uploads the distributions as a workflow artifact.

Important limitation: the workflow does not install the exact wheel it just built into a clean isolated environment and then audit that installed wheel. The current installed metadata/import evidence can therefore describe the editable checkout rather than the newly built wheel.

## Recommended use

Use the CLI to reproduce the repository's current experiment and inspect its receipts. Do not use it as the sole control for publishing a production package, making an automated API removal decision, or verifying build provenance.
