# Open Questions

This page is a single register of the items that are **intentionally unresolved** in this documentation, so reviewers can see at a glance what still needs a decision and where the detail lives. Each entry links to its canonical location; the substance is maintained there, not duplicated here.

## Ownership and multi-owner scenarios

Several DPM ownership rules are still being confirmed with the DPM Alliance. The canonical table is [§04 §2.7.2 DPM ownership rules](04_versioning_and_extensibility/02_extensibility_patterns.md#272-dpm-ownership-rules); the driving use case is [§04 §2.8 Multi-owner Items in a shared Category](04_versioning_and_extensibility/02_extensibility_patterns.md#28-multi-owner-items-in-shared-category).

| Question | Status |
| --- | --- |
| May an organisation create its own Module that references Tables owned by another organisation? | Pending |
| May an organisation create its own ReportingTaxonomy/Module referencing Dataflows/Tables owned by another organisation? | Pending |
| May Items in a Category have a different owner from the Category itself? | Pending |
| How do Releases owned by different organisations interact with the release-based change log? | Open |

Until these are resolved, the documentation recommends the conservative default described in [§04 §2.8](04_versioning_and_extensibility/02_extensibility_patterns.md#28-multi-owner-items-in-shared-category).

## Deferred artefact families

Tracked in [Artefact Index → Deferred topics](artefact_index.md#deferred-topics). Not yet mapped in any chapter:

- **MSD / Metadataflow / MetadataAttribute / MetadataConstraint** (reference metadata) — out of scope of the current DPM 2.0 Refit treatment.
- **VTL family** (TransformationScheme, RulesetScheme, etc.) — partial alignment with DPM Operations, mapping not yet specified.
- **DPM Operations component** — internal DPM mechanism; mapping to VTL pending.


