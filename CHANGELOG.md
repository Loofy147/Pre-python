# Changelog

## Unreleased

- Replaced the first gate's flattened pass/fail sequence with a multi-sorted result record retaining all seven boundary results.
- Made the imports → versions → markers → types → build → licenses → deprecations dependencies explicit.
- Added the real PEP 562 lazy types-to-build edge and moved workflow composition to the `chipcup.audit` console entry point.
- Added PEP 440 version-row selection, PEP 508 marker logs, selected protocol sets, and wheel public-export comparison.
- Added sdist/wheel metadata and package-surface consistency checks; CI now builds the wheel from the sdist.
- Added the fixture file and a supplemental LicenseRef text mapping. The distribution-level License-Expression remains MIT rather than implying per-file scoping.
- Changed removal-window validation to require actual DeprecationWarning observations on all required selected marker rows.
- Added native platform CI coverage and coded type-ignore enforcement.

## 0.1.0 — Initial alpha metadata

The initial alpha package included seven experimental subpackages and a release-gate prototype. No GitHub Release or package-index publication is asserted by this changelog entry.
