# Validation and comparative benchmark

## Two proof goals

The project must establish:
1. **Assurance correctness:** invalid, stale, incomplete, forged, contradictory, or wrong-subject evidence cannot produce an incorrect ALLOW.
2. **Incremental value:** the system finds, connects, or explains consequential risks that a competent baseline does not, without unacceptable latency or false blocks.

A green CI run is not a substitute for either goal.

## Current repository evidence

Reviewed main commit 7ef2c82fb2ebdf2e08376b154bd6e9f112b6a5ca has:
- pytest on Python 3.10–3.14;
- DeprecationWarning treated as an error;
- import-boundary checks;
- degraded-operation and geometry tests;
- mypy on the configured lane;
- native warning capture on Ubuntu, Windows, and macOS;
- sdist build and wheel-from-sdist build;
- Twine description-rendering validation;
- receipt-cycle audit and artifact upload.

Main CI run 42054977699 completed successfully. This proves only the configured checks for that commit. It does not prove semantic stub agreement, complete artifact parity, authenticated warnings, trusted provenance, historical removal eligibility, complete impact analysis, or product differentiation.

## Baseline

Declare the baseline before experiments. For Python, use a competent combination of:
- Griffe API snapshot comparison;
- pytest and the required test suite;
- mypy where applicable;
- packaging for PEP 440 and PEP 508;
- pydistcheck and archive inspection;
- Twine description check;
- pinned SPDX License List;
- available PyPI/SLSA provenance verification;
- existing CI/security scanner/review process.

Do not use a deliberately incomplete baseline.

## Corpus

Include chipcup as a controlled fixture and public Python projects with accessible release history:
- dynamic or generated code;
- optional extras and platform markers;
- native/platform-specific wheels;
- public deprecation history;
- non-trivial package metadata/license declarations.

Record exact repository, base/head commits, tags, build inputs, artifact digests, dependencies, runtime/platform, tool/policy versions, and resource limits.

## Seeded mutant families

| Family | Mutants | Expected behavior |
|---|---|---|
| API | remove symbol, change signature/default, move module, alter re-export | identify breakage and map to compatibility policy |
| Deprecation | remove before warning window, omit warning on one platform, replay old warning JSON | reject or leave UNKNOWN |
| Dependencies | vulnerable version, license change, unpinned dependency, lockfile drift | produce obligations and bind findings |
| Build | missing/extra/modified file, wheel from wrong source, malformed metadata | fail identity/parity checks |
| Provenance | wrong digest, untrusted builder, replayed attestation, forged caller assertion | never mark provenance verified |
| Markers | missing required row, false marker with unknown contract, environment mismatch | preserve policy scope and selected-row semantics |
| Evidence | duplicate, stale, truncated, malformed, conflicting, revoked record | reject or mark unknown/conflicting |
| Workflow | elevated token, unpinned action, privileged PR execution, secret access | flag trust-boundary violation |
| Impact | reflection, dynamic import, generated code, plugin discovery, unsupported syntax | report coverage limitation and fallback |
| Agent | prompt injection, self-approval, policy edit, malicious patch | block prohibited action; require independent verification |

Run single mutants first, then selected combinations.

## Experimental protocol

- Pre-register hypothesis, baseline, corpus, mutants, metrics, and thresholds.
- Run baseline and candidate on identical immutable subjects.
- Use clean isolated environments and equivalent compute.
- Establish ground truth independently.
- Repeat runs to measure nondeterminism.
- Retain raw outputs and exact tool/configuration versions.
- Report results by mutant family.
- Perform ablations for impact analysis, obligation compilation, evidence binding, provenance, and history.
- Obtain independent reproduction for a sample.

## Metrics

| Metric | Meaning |
|---|---|
| Critical false-pass rate | Mandatory seeded violation incorrectly yields ALLOW |
| Obligation recall | Required obligations generated from independently labeled changes |
| Obligation precision | Generated obligations that are genuinely applicable |
| Impact coverage | Independently identified affected subjects covered by declared analysis |
| Evidence completeness | Required evidence matching identity/trust rules |
| Subject mismatch rejection | Wrong-subject evidence rejected |
| Finding precision/recall | Actionable finding quality against ground truth |
| False-block rate | Valid changes blocked without policy basis |
| Decision replay rate | Fixed inputs reproduce the same decision |
| Runtime overhead | Added time and compute |
| Developer review burden | Time understanding, dismissing, and resolving output |
| Test execution cost | Runtime under equivalent required coverage |

No single aggregate score should hide family-level failures.

## Delivery outcomes

DORA's current metrics include change lead time, deployment frequency, failed-deployment recovery time, change fail rate, and deployment rework rate: https://dora.dev/guides/dora-metrics/.

Use them as contextual team outcomes, not direct proof that this product caused improvements. Avoid optimizing one metric as a target.

## Acceptance

Before public differentiation claims:
- no critical false-pass in the declared adversarial corpus;
- wrong-subject/untrusted producer cases fail closed;
- obligations trace to policy;
- exact wheel from sdist is installed and checked;
- unsupported constructs remain visible;
- decision replay is deterministic;
- false-block rate and CI overhead meet thresholds registered before the experiment;
- baseline and raw results are reproducible.

Report corpus, exclusions, baseline configuration, commits/artifacts, tool/environment versions, ground truth, per-family results, false passes/blocks, timing/cost, uncertainty, and protocol deviations.
