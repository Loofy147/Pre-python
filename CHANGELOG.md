# Changelog

## Unreleased

### Documentation and architecture review

- Reframed chipcup as an evidence-coordinating Python release-assurance project, rather than a replacement packaging checker.
- Added implementation-status inventory separating current behavior, known limitations, and target capabilities.
- Documented current receipt orchestration and the parallel legacy GateReport path.
- Added target evidence, claim, relationship, provenance, and policy models.
- Added CLI input/output and current exit behavior reference.
- Added ecosystem integration boundaries for Griffe, pydistcheck, Twine, packaging, SPDX, and PyPI attestations.
- Added security and trust model, adversarial validation plan, comparative benchmark design, staged roadmap, and prioritized open decisions.
- Recorded known gaps without claiming that documentation changes fix code defects.

### Existing implementation

- Replaced the first gate's flattened pass/fail sequence with a multi-sorted result record retaining all seven boundary results.
- Made the receipt-cycle dependencies explicit.
- Added PEP 440 version-row selection, PEP 508 marker logs, selected protocol sets, and wheel public-export comparison.
- Added sdist/wheel metadata and package-surface checks; CI builds the wheel from the sdist.
- Added the measured teacup fixture and supplemental LicenseRef text mapping.
- Added native platform warning evidence and degraded-operation checks.

## 0.1.0 — Initial alpha metadata

The initial alpha package included experimental subpackages and a release-gate prototype. No GitHub Release or package-index publication is asserted by this changelog entry.
