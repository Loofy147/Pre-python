# CLI reference

## Scope

This reference describes the current chipcup 0.1.0 Alpha CLI on reviewed main commit 7ef2c82fb2ebdf2e08376b154bd6e9f112b6a5ca. It is a Python distribution-audit command, not the target Change Assurance Engine CLI.

## Invocation

~~~bash
python -m chipcup.cli \
  --sdist dist/chipcup-0.1.0.tar.gz \
  --wheel dist/chipcup-0.1.0-py3-none-any.whl \
  --matrix fixtures/audit-matrix.json \
  --warning-evidence warning-evidence/ \
  --project-root . \
  --version-specifier ">=0.1.0,<1.0.0" \
  --build-isolation-verified
~~~

## Arguments

| Argument | Required | Current behavior |
|---|---:|---|
| --sdist | Yes | Path to source distribution archive |
| --wheel | Yes | Path to wheel archive |
| --matrix | No | JSON marker matrix; defaults to fixtures/audit-matrix.json |
| --project-root | No | Project root; defaults to current directory |
| --warning-evidence | Yes | JSON file or directory of warning-observation JSON files |
| --version-specifier | No | PEP 440 specifier; defaults to >=0.1.0,<1.0.0 |
| --build-isolation-verified | No | Caller assertion that archives were built in isolation; defaults false |

The build-isolation flag is not a cryptographic attestation and must not be presented as independent provenance verification.

## Matrix input

The input is a JSON array. Each row currently provides name, expression, stub_set, optional version_specifier, optional environment object, and optional extra. The parser checks basic structure and types; this does not make the complete marker policy contract authoritative.

## Warning evidence input

The input may be a JSON array or a JSON object per file. Each record currently includes release, matrix_row, platform, marker_selected, emitted, and warning_count.

The loader checks basic field types but does not authenticate the producer, bind the observation to a trusted workflow identity, or prove that the record belongs to the exact candidate/source revision.

## Output

The CLI prints a JSON report containing passed, dependency_order, and one entry per receipt. Each receipt records boundary, verdict, state, evidence, and issues.

This is an Alpha receipt report, not a versioned Change Assurance Dossier.

## Current main exit behavior

| Exit | Meaning |
|---:|---|
| 0 | Report passed |
| 1 | Report failed or a general audit exception occurred |
| 3 | A required module could not be imported |
| 2 | Standard argparse usage error for invalid command-line arguments |

The open PR #4 proposes a different stable exit-code enum. It is not part of the reviewed main commit and must not be documented as current behavior until merged and reconciled with receipt semantics.

## Limitations

- published release history is hardcoded to 0.1.0 in the current CLI;
- the CLI does not implement the full historical deprecation-removal decision;
- build isolation is a caller assertion;
- warning JSON is not authenticated;
- there is no general change classification or impact coverage;
- there is no canonical evidence envelope or durable evidence ledger;
- the CLI and public GateReport API use different execution paths.

See STATUS.md and API_REFERENCE.md.
