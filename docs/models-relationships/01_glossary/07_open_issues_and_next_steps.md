# 7. Open issues and next steps

The following topics are identified in the background documents and ECB materials but require further work before being fully stabilised in the glossary mapping:

- **Property vs Metric decision rule**  
  Refine the rule for borderline cases, such as numeric attributes that are not measures, or concepts that appear as both measures and dimensions in different structures.

- **Non-enumerated Categories**  
  Clarify when to model a Non-Enumerated Category explicitly versus relying purely on the data type of a Property/Metric.

- **Compound Category Items in SDMX**  
  Decide how to best expose compound compositions in SDMX (annotations, derived dimensions, etc.) when mapping from DPM so that users understand the underlying structure.

- **Mixed-codelist hierarchies**  
  Define a standard strategy for handling SDMX hierarchies that combine multiple codelists (ignore, split, or document externally).

Next iterations of this document should:
- Add concrete, worked examples (e.g. population by age/sex/geo; a compound item such as “Treasury bill”).
- Link individual rules to specific examples from SDMX and DPM instances in the background materials.

