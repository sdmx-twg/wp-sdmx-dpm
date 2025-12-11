# Model Relationships

Entry point for the SDMX 3.0 ↔ DPM Refit (2.0) relationships. Source of truth for agreements: `../twg/workpackages/sdmx_dpm/docs/meetings/` (latest minutes 1 Dec 2025).

## How to navigate
- [Glossary](01_glossary/index.md): Concepts/Codelists ↔ Properties/Categories, naming conventions.
- [Data Definition](02_data_definition/index.md): Dataflows/DSDs ↔ Report Tables and variables; common table patterns.
- [Other Artifacts](03_other_artifacts/index.md): Reporting taxonomies ↔ Report Modules; rendering artefacts and related constructs.
- [Versioning and Extensibility](04_versioning_and_extensibility/index.md): How the models evolve, how extensions are handled, and serialisation/version constraints.
- [Gaps](05_gaps/index.md): Known loss points and mitigation/open questions.

## Scope
- Focus on the core SDMX–DPM mapping; XBRL is covered only where required to serialise/exchange DPM content.
- Start with glossary and simple data-structure cases; keep sensitive details out of this public repo.

## Backlog
- Defaults and implicit dimensions (including SDMX GSD anchor values).
- Multi-measure datasets vs single generic `OBS_VALUE` handling.
- Stock vs flow, frequency, and XBRL instant vs duration alignment.
- Data-type compatibility and potential information loss.
- Identifier restrictions (e.g., XBRL ID rules) and naming conventions.
- Scope boundaries for XBRL features beyond the DPM use case.

## Near-term actions
- Draft the first glossary mapping (Antonio with Ida) using the agreed structure.
- Add examples for the simple data-structure cases reviewed in meetings.
- Cross-reference background materials as they are cleared for publication.
