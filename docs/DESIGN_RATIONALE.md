# Design rationale

## From a seven-boundary experiment to change assurance

The chipcup prototype organizes release checks around seven receipt boundaries. This was useful for experimenting with typed observations, degraded states, and multi-dimensional reports. It is not sufficient as a long-term product architecture.

A product organized only around formal-system categories risks adding modules without solving a distinct user problem. The teacup fixture remains valuable because a measured notch tolerance makes a regression test load-bearing; it is not the product identity.

## Why change is the organizing subject

A software change links:
- source/API compatibility;
- dependency and license effects;
- security boundaries;
- tests and supported environments;
- build artifacts and provenance;
- release policy and human approval.

The user workflow is concrete: before a change is merged or released, what is affected, what must be verified, and what remains unknown?

## Why not another code reviewer

AI review tools already identify issues and suggest fixes. Rebuilding one duplicates findings and does not solve evidence identity or policy replay. Consume their outputs and focus on whether required obligations were satisfied for the actual subject.

## Why not a universal graph first

A graph represents relationships; it does not guarantee that edges are correct or evidence trusted. Existing code-intelligence and supply-chain graph tools cover adjacent territory. Start with typed records and explicit edges. Add graph storage only after query, scale, and retention needs justify it.

## Why not an agent-first product

Agents are probabilistic and can be influenced by malicious repository content. They may investigate or propose patches, but cannot control policy or certify their own changes. The trusted core must make subject resolution, obligation compilation, evidence validation, and policy evaluation replayable.

## Why Python first

The current code and tests provide a Python release-assurance experiment with concrete defects to close. Python-first creates one reference workflow. It does not prove language-neutral design; a second-language pilot must test that assumption.

## Why an assurance case

No test suite or static analyzer proves arbitrary software correct. A structured dossier can show what was checked, why, against which subject, by which tool/environment, and with what limitations and exceptions. This is more precise than a universal proof or risk score.

## Why coverage is explicit

Static dependency and API analysis cannot observe every dynamic behavior. If the system cannot establish its analysis scope, it must report partial/unknown coverage and trigger a conservative fallback rather than imply no impact.

## Why test prioritization is optional

Predictive selection can reduce feedback time, but selection errors can hide regressions. It may order checks or suggest additional tests. It cannot silently remove policy-required suites or certify full coverage.

## Why the roadmap is gated

The largest risk is building a broad system whose claims cannot be trusted and whose user value is unproven. Correctness, evidence identity, hostile-execution safety, comparative value, and adoption must precede multi-language support, runtime assurance, hosted graph infrastructure, and autonomous repair.
