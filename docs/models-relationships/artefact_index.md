# Artefact index

Master index of every SDMX 3.1 and DPM 2.0 Refit class covered (or deliberately deferred) in these mapping guidelines. For each class the table records its counterpart in the other model (where one exists) and the section(s) where it is documented.

This file is generated/maintained by hand and is the canonical reference for the cross-section structure used throughout the Models Relationships chapters. When a class's section assignment changes, update this file.

## Section legend

| Section | Scope |
|---------|-------|
| **§00 Basics** | Foundational identification, multilingual, and common conventions shared by all artefacts |
| **§01 Glossary** | Semantic-layer artefacts (codelists, concepts, items, properties, hierarchies, subsets, compound items) |
| **§02 Data Definition** | Data-structure artefacts (DSDs, dataflows, tables, headers, cells, variables, constraints) |
| **§03 Other Artefacts** | Real cross-model correspondences for classification and reporting taxonomy (CategoryScheme/Framework, ReportingTaxonomy/ModuleVersion, related maps) |
| **§04 Versioning & Extensibility** | Ownership/identity, lifecycle (Release, Deactivation), generic Annotation extension mechanism, version evolution rules |
| **§05 Gaps** | Artefacts that have no counterpart in the other model, plus representation/precision gaps and proposals |

## How to read the tables

- **Counterpart**: name of the matching class in the other model. `—` means no direct counterpart.
- **Section(s)**: where the class is documented. A class may appear in more than one section when it is used in multiple roles (e.g. `Annotation` is the SDMX extension mechanism — covered in §04 — but also appears as a recognised marker in §00, §01, §02, §03 cross-references).
- **Direction notes**: a one-line summary of any asymmetry, partiality, or convention used.

## SDMX 3.1 classes

### Foundational / metaclasses

| SDMX class | Counterpart in DPM | Section(s) | Direction notes |
|------------|--------------------|------------|-----------------|
| AnnotableArtefact (abstract) | DPMClass | §00 | Foundation; not directly mapped |
| IdentifiableArtefact (abstract) | Concept | §00 | Foundation |
| NameableArtefact (abstract) | Concept (Name + Description) | §00 | Multilingual rules in §00 §2.3 |
| VersionableArtefact (abstract) | Versioned DPM Concepts | §00 + §04 | Versioning model in §04 §1.1 |
| MaintainableArtefact (abstract) | Concept with Owner | §00 + §04 | `agencyID` ↔ `Owner` (§04 §3.1) |

### Glossary layer

| SDMX class | Counterpart in DPM | Section(s) | Direction notes |
|------------|--------------------|------------|-----------------|
| ItemScheme (abstract) | Category | §01 | Glossary container abstraction |
| Item (abstract) | Item | §01 | |
| Codelist | Category (enumerated) | §01 §3.1 | 1:1 mapping |
| ValueList | Category (enumerated, no semantics) | §01 §3.1 | Treated like Codelist |
| GeoCodelist | Category | §01 §3.1.5 | Geometry not modelled in DPM |
| Code | Item via ItemCategory | §01 §3.3 | Round-trip via `Signature` field |
| Value | Item | §01 §3.3 | |
| Concept | Property | §01 §3.5 | Includes `IsMetric` flag handling |
| ConceptScheme | — (DPM has single glossary) | §01 §3.5.6 | DPM-only edge: scheme container has no direct DPM counterpart |
| ConceptSchemeMap | ConceptRelation (partial) | §01 §3.5.6 | |
| RepresentationMap | (no general DPM target) | §01 + §02 | Used at glossary or data-definition boundary |
| Hierarchy | SubCategory + SubCategoryItem | §01 §3.4.3 | Cross-codelist hierarchies are a gap (§05 §1.3.2) |
| HierarchicalCode | (within Hierarchy) | §01 §3.4.3 | |
| Level | (within Hierarchy) | §01 §3.4.3 | |
| HierarchyAssociation | — | §01 + §05 | No direct DPM counterpart |
| CodelistExtension | SubCategory / SuperCategory | §01 §3.2, §3.4.1 + §04 §2.1 | Approximate; partial loss documented in §04 |
| InclusiveCodeSelection / ExclusiveCodeSelection | (no DPM equivalent) | §01 §3.2.2.3 + §05 | Approximate via SubCategory enumeration |

### Data-definition layer

| SDMX class | Counterpart in DPM | Section(s) | Direction notes |
|------------|--------------------|------------|-----------------|
| DataStructureDefinition (DSD) | Table (structural content) | §02 §3.1, §3.2 | Pair with Dataflow; structural content distributed into Headers + Variables |
| Dataflow | Table / TableVersion | §02 §3.1 | Dataflow `id` ↔ TableVersion `Code` |
| DimensionDescriptor | (implicit in Headers) | §02 §3.2 | |
| Dimension | Header / KeyVariable / Cell key | §02 §3.2 | Flat vs non-flat patterns differ |
| TimeDimension | Dimension with time Property | §02 §3.2 + §05 §2.3 | Stock/flow and frequency are gap territory |
| GroupDimensionDescriptor | — | §05 §1.2 | No DPM equivalent |
| MeasureDescriptor | (implicit) | §02 §3.2 | |
| Measure | FactVariable / Cell value | §02 §3.2 | Multi-measure is a gap (§05 §2.2) |
| AttributeDescriptor | (implicit) | §02 §3.2 | |
| DataAttribute | AttributeVariable | §02 §3.2 | Attachment levels are a gap (§05 §1.3.3) |
| AttributeRelationship | AttributeVariable.subject (implicit) | §02 + §05 §1.3.3 | Five SDMX levels, one DPM convention |
| DataConstraint | SubCategory + Variable scope | §02 §3.3 | CubeRegion vs DataKeySet handled separately |
| CubeRegion | SubCategory per Dimension | §02 §3.3.1.1 | Dimension-wise value lists |
| DataKeySet | (no direct equivalent) | §02 §3.3.1.2 + §05 §1.5 | Explicit-key enumeration; gap |
| MemberSelection / MemberValue | Item membership in SubCategory | §02 §3.3 | |
| StructureMap | (no general DPM target) | §02 | StructureMap is data-definition layer |
| FixedValueMap | Header with fixed Context | §02 + §05 §2.1 | |
| Series / Observation | Variable observation | §02 §3.3 | |

### Classification and reporting taxonomy

| SDMX class | Counterpart in DPM | Section(s) | Direction notes |
|------------|--------------------|------------|-----------------|
| CategoryScheme | Framework | §03 §3.1 | 1:1 mapping; scheme `agencyID` → Framework `Owner` |
| Category | Module | §03 §3.1 | Hierarchy flattened; encoded by Module `Code` convention |
| Categorisation | implicit Module membership (via ModuleVersionComposition) | §03 §3.1.5 | Lossy round-trip |
| CategorySchemeMap | ConceptRelation (workaround, not a structural counterpart) | §05 §2.9 | Treated as a gap: rebrand/merge expressed via ConceptRelation rather than a dedicated artefact |
| ReportingTaxonomy | ModuleVersion | §03 §3.2 | Deployable-unit alignment |
| ReportingCategory | TableGroup (optional image inside ModuleVersion) | §03 §3.2 | Partial: only inside the matching ModuleVersion |
| ReportingTaxonomyMap | Module-versions relationship | §03 §3.3 | Cross-version map between ModuleVersions of the same Module |

### Organisations and ownership

| SDMX class             | Counterpart in DPM                        | Section(s) | Direction notes                                          |
| ---------------------- | ----------------------------------------- | ---------- | -------------------------------------------------------- |
| Agency                 | Organisation (role=owner)                 | §04 §3.1   | `id` ↔ `Acronym`; hierarchy flattened                    |
| AgencyScheme           | — (no DPM container)                      | §04 §3.1.5 | DPM has flat list of Organisations                       |
| DataProvider           | Organisation (role=entry_point)           | §04 §3.2   |                                                          |
| DataProviderScheme     | —                                         | §04 §3.2.4 |                                                          |
| DataConsumer           | (Organisation role=responsible, optional) | §04 §3.2.5 | No clear DPM target by default                           |
| DataConsumerScheme     | —                                         | §04 §3.2.5 |                                                          |
| OrganisationUnit       | (Organisation, optional)                  | §04 §3.2.5 | Catch-all; map only when role is documented              |
| OrganisationUnitScheme | —                                         | §04 §3.2.5 |                                                          |
| Contact                | Organisation.URI (partial)                | §04 §3.1   | First `Contact.URI` only; remaining contact details lost |
| OrganisationSchemeMap  | Organisation rename / ConceptRelation     | §04 §3.3   |                                                          |

### Provisioning, process, generic extension (no DPM equivalent — §05 gap territory)

| SDMX class | Counterpart in DPM | Section(s) | Direction notes |
|------------|--------------------|------------|-----------------|
| ProvisionAgreement | — | §05 §2.6 | DPM does not model data-supply contracts; passthrough via `DPM_PROVISION_AGREEMENT` annotation |
| MetadataProvisionAgreement | — | §05 §2.6 (same family) | |
| Datasource (SimpleDatasource, RESTDatasource) | — | §05 §2.6 | Nested in ProvisionAgreement |
| Process | — | §05 §2.7 | DPM does not model production workflows |
| ProcessStep | — | §05 §2.7 | |
| Annotation (generic) | Description / recognised markers | §04 §3.6 | Three-tier rule; cross-cutting marker table maintained in §04 |

### Constraints and metadata

| SDMX class | Counterpart in DPM | Section(s) | Direction notes |
|------------|--------------------|------------|-----------------|
| MetadataStructureDefinition (MSD) | — | §05 (deferred) | Not yet covered |
| Metadataflow | — | §05 (deferred) | |
| ReportStructure / MetadataAttribute | — | §05 (deferred) | |
| MetadataAttributeDescriptor | — | §05 (deferred) | |
| MetadataConstraint | — | §05 (deferred) | |
| MetadataProvider / Scheme | — | §05 (deferred) | |

### VTL family

| SDMX class | Counterpart in DPM | Section(s) | Direction notes |
|------------|--------------------|------------|-----------------|
| TransformationScheme | Operation (partial) | §05 (deferred) | Not yet covered |
| RulesetScheme | Operation (partial) | §05 (deferred) | |
| UserDefinedOperatorScheme | — | §05 (deferred) | |
| VtlMappingScheme | — | §05 (deferred) | |
| NamePersonalisationScheme | — | §05 (deferred) | |
| CustomTypeScheme | — | §05 (deferred) | |

## DPM 2.0 Refit classes

### Foundational / metamodel infrastructure

| DPM class | Counterpart in SDMX | Section(s) | Direction notes |
|-----------|---------------------|------------|-----------------|
| Concept (DPM metaclass) | IdentifiableArtefact | §00 | All identifiable DPM objects are Concepts |
| DPMClass | — | §00 | Metamodel reflection |
| DPMAttribute | — | §00 | Metamodel reflection |
| Translation | InternationalString (`xml:lang`) | §00 §2.3 | One Translation row per language |
| Language | (xml:lang) | §00 | Foundation |
| ConceptRelation | ItemSchemeMap / RepresentationMap (partial) | §01 + §03 + §04 | Used at glossary, classification, and organisational layers |
| Reference / Document / DocumentVersion / Subdivision | Annotation `url` (partial) | §00 + §04 | Documentation infrastructure |
| ChangeLog (non-normative) | — | §04 | Implementation log; not part of the DPM standard |

### Glossary layer

| DPM class | Counterpart in SDMX | Section(s) | Direction notes |
|-----------|---------------------|------------|-----------------|
| Category (abstract) | Codelist / ValueList | §01 §3.1 | Enumerated vs non-enumerated |
| Item | Code | §01 §3.3 | Identity via ItemCategory |
| ItemCategory | (Code in Codelist) | §01 §3.3 + §04 §1.2 | Holds `Signature` and `IsDefaultItem` |
| SubCategory | Hierarchy / Codelist subset | §01 §3.4 | Triggered from Codelist Extensions or Constraints |
| SubCategoryItem | (Code member) | §01 §3.4 | |
| SubCategoryVersion | — | §04 §1.2 | Versioned subset |
| SuperCategory | Extended Codelist (additive, partial) | §01 §3.2 + §04 §2.1 | Union of Categories |
| SuperCategoryComposition | (within Extended Codelist) | §01 §3.2 | |
| Property | Concept | §01 §3.5 | `IsMetric` distinguishes qualitative vs quantitative |
| PropertyCategory | (representation linkage) | §01 §3.5.7 | |
| Context | (no SDMX equivalent at glossary level) | §01 + §05 §2.4 | Used by CompoundItem and non-flat tables |
| ContextComposition | (no SDMX equivalent) | §01 + §05 §2.4 | |
| CompoundItem / CompoundItemContext | — | §01 §3.3.5 + §05 §2.4 | DPM-only feature gap |
| DataType | FacetValueType | §01 §3.5.3.5 + §05 §1.4.1 | Partial alignment |

### Data-definition layer

| DPM class | Counterpart in SDMX | Section(s) | Direction notes |
|-----------|---------------------|------------|-----------------|
| Variable (abstract) / VariableVersion | Dimension / Measure / Attribute | §02 §3.2, §3.3 | Type discriminated by subclass |
| FactVariable | Measure | §02 §3.2 | |
| KeyVariable | Dimension | §02 §3.2 | |
| AttributeVariable | DataAttribute | §02 §3.2 | Attachment level is a gap (§05 §1.3.3) |
| FilingIndicatorVariable | — | §02 + §05 §1.2 | DPM-only |
| Dimension (DPM Variables) | (Property reference) | §02 §3.2 | |
| Table | Dataflow + DSD | §02 §3.1 | `IsFlat` flag distinguishes patterns |
| TableVersion | Dataflow version | §02 §3.1 + §04 §1.2 | Versioning behaviour in §04 |
| Header / HeaderVersion | Dimension / Measure (in flat) or composite | §02 §3.2 | Carries Property, Context, or SubCategory |
| Cell / TableVersionCell | Observation key | §02 §3.2 | Cell→VariableVersion link is optional |
| TableGroup | — (proposal: ReportingCategory inside ReportingTaxonomy) | §05 §2.8 | DPM-only; partial image via ReportingCategory |
| TableGroupComposition | — | §05 §2.8 | |
| TableAssociation | — | §05 §2.8 | DPM-only; supports multi-grouping |
| CompoundKey / KeyComposition | (Dimension key set) | §02 §3.2 | |

### Operations and validation

| DPM class | Counterpart in SDMX | Section(s) | Direction notes |
|-----------|---------------------|------------|-----------------|
| Operation / OperationVersion | TransformationScheme item (partial) | §05 (deferred) | Not yet covered |
| OperationScope | — | §05 (deferred) | |
| OperationScopeComposition | — | §05 (deferred) | |
| ExpressionNode (AST) | VTL expression | §05 (deferred) | |
| ModuleParameters | — | §05 (deferred) | DPM-only |

### Packaging and classification

| DPM class | Counterpart in SDMX | Section(s) | Direction notes |
|-----------|---------------------|------------|-----------------|
| Framework | CategoryScheme | §03 §3.1 | Top-level container for a reporting domain |
| Module | Category | §03 §3.1 | Modules are siblings; hierarchy encoded in `Code` |
| ModuleVersion | ReportingTaxonomy | §03 §3.2 | Deployable unit |
| ModuleVersionComposition | ReportingCategory.dataflows | §03 §3.2 | Linkage to TableVersions |
| ModuleParameters | — | §05 (deferred) | DPM-only |

### Organisations

| DPM class | Counterpart in SDMX | Section(s) | Direction notes |
|-----------|---------------------|------------|-----------------|
| Organisation | Agency / DataProvider / DataConsumer / OrganisationUnit | §04 §3.1, §3.2 | Discriminated by `OrganisationRole` |
| OrganisationRole | (scheme membership in SDMX) | §04 §3.1, §3.2 | DPM uses role attribute; SDMX uses scheme type |

### Lifecycle

| DPM class | Counterpart in SDMX | Section(s) | Direction notes |
|-----------|---------------------|------------|-----------------|
| Release | (validFrom convention; no dedicated artefact) | §04 §3.4 | Releases bundle ModuleVersions |
| Deactivation | validTo + Annotation | §04 §3.5 | Soft delete; reason preserved via `DPM_DEACTIVATION_REASON` annotation |
| StartReleaseID / EndReleaseID | validFrom / validTo | §04 §1.3 + §3.4, §3.5 | |
| FromReferenceDate / ToReferenceDate | (no SDMX field) | §04 §3.4 | Application date; preserved via `DPM_FROM_REFERENCE_DATE` annotation |

## Cross-cutting topics

| Topic | Covered in | Notes |
|-------|------------|-------|
| Identification (DPM IDs vs SDMX URNs) | §00 §2.2 | Used by every artefact |
| Multilingual (InternationalString vs Translation) | §00 §2.3 | Used by every nameable artefact |
| Boolean encoding (-1/0) | §00 §2.5.1 | DPM physical convention |
| Recognised SDMX annotation markers (`DPM_SIGNATURE`, `DPM_DEFAULT_ITEM`, `DPM_COMPOUND_COMPONENTS`, `DPM_RELEASE_CODE`, `DPM_FROM_REFERENCE_DATE`, `DPM_DEACTIVATION_REASON`, `DPM_PROVISION_AGREEMENT`, `DPM_PROCESS`, `DPM_TABLEGROUP`, `DPM_AGENCY_PARENT`, `DPM_ID_PREFIX`, `DPM_AGENCY_SCHEME`, `DPM_CATEGORISATION_ID`) | §04 §3.6 (canonical table); cross-references from §00, §01, §02, §03, §05 | One canonical list; sections that need a marker reference §04 §3.6 |

## Deferred topics

The following families are not yet covered in any chapter and are tracked here so they can be picked up in a later pass:

- **MSD / Metadataflow / MetadataAttribute / MetadataConstraint family** — reference metadata is out of scope of the current DPM 2.0 Refit treatment. To be addressed in §05 (or a dedicated §06 chapter) when the project is ready.
- **VTL family** (TransformationScheme, RulesetScheme, VtlMappingScheme, UserDefinedOperatorScheme, NamePersonalisationScheme, CustomTypeScheme) — partial alignment with DPM Operations exists but the mapping has not been specified.
- **DPM Operations component** (Operation, OperationVersion, OperationScope, ExpressionNode AST) — internal DPM mechanism; mapping to VTL pending.

## Maintenance

When moving content between sections or adding new content, also update this file:

1. Find the affected class row(s).
2. Update the **Section(s)** column to reflect the new location.
3. If a new class is added, insert it in the appropriate group and refer to its section(s).
4. If a class is split between sections (e.g. covered briefly in one and detailed in another), list both with the most-detailed section first.
