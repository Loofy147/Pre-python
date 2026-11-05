# Changelog

All notable project changes are recorded here. Documentation and target design are distinguished from shipped application behavior.

## Unreleased

### Architecture and product revalidation
- Reframed the strategic target as a Change Assurance Engine while retaining chipcup as the current Python release-assurance prototype.
- Rejected a broad autonomous engineering platform as the first implementation target.
- Added a multi-domain change taxonomy spanning source/API, dependencies, build/release, configuration/infrastructure, schemas, security, CI workflows, AI configuration, deployment, and runtime changes.
- Defined the first vertical slice as Python pull-request-to-release assurance.
- Added explicit impact-coverage states so incomplete static analysis cannot imply no impact.
- Separated evidence validity, trust, completeness, claim status, rule result, severity, and final decision.
- Added hostile-PR execution and agent authority requirements.
- Added ecosystem overlap review, benchmark protocol, customer-validation questions, and gated roadmap.
- Updated implementation status and open decisions without claiming target capabilities are shipped.

### Existing implementation
The reviewed 0.1.0 Alpha source contains a seven-boundary receipt experiment, measured fixture geometry, selected artifact metadata and public-export comparisons, marker evaluation, warning observations, lazy CLI loading, and CI across Python 3.10–3.14 plus native platform jobs.

Known code gaps remain documented in docs/STATUS.md: caller-asserted provenance, incomplete artifact parity, unauthenticated warning JSON, type-stub semantic mismatch, marker-scope defect, hardcoded release identity, and parallel execution paths.

This documentation update changes no application source, CI workflow, package metadata, or runtime capability.
