# Versioning and Extensibility

Outline how SDMX and DPM artefacts evolve, how extensions are managed, and which serialisation/version constraints must be respected for interoperability.

## Scope
- Align versioning practices between SDMX artefacts (Dataflows, DSDs, Codelists) and DPM artefacts (Report Tables, Modules, Categories).
- Define extension patterns (e.g., extended codelists, additional properties/variables) that remain interoperable across SDMX and DPM.
- Capture identifier and serialisation constraints (including XBRL-CSV) that influence versioning or extension choices.
- Note expectations for backward/forward compatibility when exchanging updates between communities.

## Open items
- Decide naming/versioning conventions that keep SDMX IDs, DPM IDs, and any XBRL-derived IDs aligned.
- Document how to announce and manage extensions without breaking downstream consumers (e.g., optional vs required additions).
- Add examples of minor vs major changes and how they propagate through serialisations.
