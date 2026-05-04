# 3. Detailed mapping rules

After the meeting on 2026-05-04, the substantive content of this chapter has been redistributed:

- **Module / ModuleVersion ↔ ReportingTaxonomy / ReportingCategory**, **Categorisation**, and **ReportingTaxonomyMap** moved to [§02 §3.4](../02_data_definition/03_detailed_mapping_rules.md#34-reporting-bundle-reportingtaxonomy-reportingcategory-moduleversion). Module is core to the DPM data-definition layer.
- **Framework ↔ CategoryScheme convention** moved to [§05 §2.11](../05_gaps/02_specific_gap_analysis.md#211-framework-dpm-feature-without-sdmx-equivalent). Framework has no SDMX counterpart; the CategoryScheme convention is a workaround.
- **CategoryScheme as backdoor** for DPM-only classification documented in [§05 §2.12](../05_gaps/02_specific_gap_analysis.md#212-categoryscheme-sdmx-backdoor-for-dpm-only-classification).
- **CategorySchemeMap** remains a gap: [§05 §2.9](../05_gaps/02_specific_gap_analysis.md#29-categoryschememap-sdmx-feature-without-dpm-equivalent).
- **OrganisationSchemeMap**: [§04 §3.3](../04_versioning_and_extensibility/03_detailed_mapping_rules.md#33-organisationschememap).

The only content remaining here is the registry of SDMX mapping artefacts (§3.1).

## 3.1 Cross-reference: registry of SDMX mapping artefacts

The full SDMX map family and where each member is documented:

| SDMX map type            | Source/target layer            | Documented in                                                                                                                       |
|--------------------------|--------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| StructureMap             | Data definition (DSD/Dataflow) | [§02 §3.2](../02_data_definition/03_detailed_mapping_rules.md#32-dsd-table-as-structural-collections)                              |
| RepresentationMap        | Glossary / data definition     | [§02 §3.2](../02_data_definition/03_detailed_mapping_rules.md#32-dsd-table-as-structural-collections), [§01 §3.3](../01_glossary/03_detailed_mapping_rules.md#33-code-category-item) |
| ConceptSchemeMap         | Glossary (Concepts/Properties) | [§01 §3.5.6](../01_glossary/03_detailed_mapping_rules.md#356-conceptscheme-handling)                                                |
| CategorySchemeMap        | No DPM equivalent (workaround) | [§05 §2.9](../05_gaps/02_specific_gap_analysis.md#29-categoryschememap-sdmx-feature-without-dpm-equivalent)                          |
| ReportingTaxonomyMap     | §02 (ModuleVersions)           | [§02 §3.4.7](../02_data_definition/03_detailed_mapping_rules.md#347-reportingtaxonomymap)                                                                                                                          |
| OrganisationSchemeMap    | §04 (Organisations)            | [§04 §3.3](../04_versioning_and_extensibility/03_detailed_mapping_rules.md#33-organisationschememap)                                |
