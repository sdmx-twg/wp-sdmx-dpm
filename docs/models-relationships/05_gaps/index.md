# Gaps

Track where semantics or fidelity may be lost when moving between SDMX, DPM, and the required XBRL serialisation layer.

## Scope
- Identify areas of potential information loss (data types, defaults, implicit dimensions, measure handling).
- Summarise mitigation options or open questions to resolve in future iterations.

## Open items
- Document how defaults and implicit dimensions (e.g., SDMX GSD anchor values) should be expressed in DPM/XBRL-CSV.
- Analyse multi-measure vs single generic `OBS_VALUE` handling and the impact on DPM main properties.
- Align stock vs flow and frequency with XBRL instant vs duration semantics.
