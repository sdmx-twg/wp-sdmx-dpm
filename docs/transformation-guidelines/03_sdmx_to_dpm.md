# 3. SDMX → DPM

This chapter works the reverse direction: converting an SDMX Dataflow + DSD (with the Codelists and Concepts it references) into a DPM Table and its glossary. It follows the same [methodology](01_methodology.md) — glossary first, then data definition. The authoritative rules are in [§01 §3](../models-relationships/01_glossary/03_detailed_mapping_rules.md) and [§02 §3](../models-relationships/02_data_definition/03_detailed_mapping_rules.md).

A key structural difference to keep in mind: in DPM a Property is spread across four tables (`Item` with `IsProperty = TRUE`, `ItemCategory`, `Property`, `PropertyCategory`) that share one identity. The recipes below produce all of them.

## 3.1 Source (SDMX)

```xml
<Codelist id="CL_FREQ" agencyID="ECB" version="1.0">
  <Name xml:lang="en">Frequency</Name>
  <Code id="A"><Name xml:lang="en">Annual</Name></Code>
  <Code id="Q"><Name xml:lang="en">Quarterly</Name></Code>
</Codelist>

<DataStructure id="ECB_CBD2" agencyID="ECB" version="1.0">
  <DimensionList>
    <Dimension id="FREQ" position="1">
      <ConceptIdentity><Ref id="FREQ" class="Concept"/></ConceptIdentity>
      <LocalRepresentation>
        <Enumeration><Ref id="CL_FREQ" class="Codelist"/></Enumeration>
      </LocalRepresentation>
    </Dimension>
  </DimensionList>
  <MeasureList>
    <Measure id="OBS_VALUE">
      <ConceptIdentity><Ref id="OBS_VALUE" class="Concept"/></ConceptIdentity>
      <LocalRepresentation><TextFormat textType="String" maxLength="30"/></LocalRepresentation>
    </Measure>
  </MeasureList>
</DataStructure>

<Dataflow id="CBD2" agencyID="ECB" version="1.0">
  <Name xml:lang="en">Consolidated Banking data</Name>
  <Structure><Ref id="ECB_CBD2" class="DataStructure"/></Structure>
</Dataflow>
```

## 3.2 Step 1 — Owner / Agency

Map the SDMX `agencyID` (`ECB`) to a DPM Owner via the Agency ↔ Organisation lookup ([§04 §3.1](../models-relationships/04_versioning_and_extensibility/03_detailed_mapping_rules.md)). All artefacts below inherit this owner.

## 3.3 Step 2 — Glossary

### Codelist → Category, Code → Item

| SDMX | DPM | Notes |
| --- | --- | --- |
| `Codelist.id` | `Category.Code` | Set `IsEnumerated = TRUE`, `IsActive = TRUE`. |
| `Code.id` | `ItemCategory.Code` | Plus a `Signature` `{owner}_{category}:{code}`. |
| `Code.Name` | `Item.Name` | All languages preserved; `Item.IsProperty = FALSE`. |

A DPM Category requires a **default Item**. SDMX has no such concept, so default selection is convention-driven: prefer an incoming `DPM_DEFAULT_ITEM` annotation or a known total/wildcard code (`_T`, `_X`); otherwise synthesise one and **flag it for review** (see [§01 §3 default-item handling](../models-relationships/01_glossary/03_detailed_mapping_rules.md)).

### Concept → Property

For each Concept, create the four linked rows:

1. `Item` with `IsProperty = TRUE`, `Name`/`Description` from the Concept.
2. `ItemCategory` linking to the built-in `_PR` properties category, `Code = Concept.id`, with a Signature `{owner}:{concept_id}`.
3. `Property` sharing the Item's identity, carrying `IsMetric` and `DataTypeID`.
4. `PropertyCategory` linking to the semantic-domain Category (from the Concept's enumerated representation; `_NA` when non-enumerated).

`IsMetric` is derived from the representation: numeric `TextFormat` (Decimal/Integer) → `TRUE`; enumerated via Codelist → `FALSE`. Where the representation is ambiguous, fall back to a documented heuristic and flag for review. `OBS_VALUE` above has a String representation but is the measure — treat it as metric per convention.

## 3.4 Step 3 — Data definition

### Dataflow + DSD → Table

One Dataflow + its DSD maps to one DPM Table. For the standard SDMX-style mapping set `IsFlat = TRUE`, `HasOpenRows = TRUE`, `IsAbstract = FALSE`, `IsNormalised = FALSE`. `Dataflow.id` → `TableVersion.Code`; `Dataflow.Name` → `TableVersion.Name`.

### Components → Headers + Variables

| SDMX component | DPM result |
| --- | --- |
| Dimension (in `position` order) | Header (`IsKey = TRUE`) + **KeyVariable**, added to the table's CompoundKey in key order. |
| TimeDimension | KeyVariable on a time-related Property (the dedicated time type collapses to a Date Property + period semantics). |
| Measure | Header (`IsKey = FALSE`) + **FactVariable**. |
| DataAttribute | Header (`IsAttribute = TRUE`) + **AttributeVariable**, linked to its subject FactVariable via a `variable_attribute` ConceptRelation. The SDMX `AttributeRelationship` (attachment level) is captured by the relation but not formally typed. |
| ContentConstraint / CubeRegion | SubCategory on the corresponding Header. `cascadeValues` hierarchies are flattened to explicit members. |

Each Header references the Property mapped in step 2; enumerated Headers may carry a `SubCategoryVID` when a constraint restricts the allowed Items.

### Reporting bundle

The Dataflow must belong to a **Module** (mandatory in DPM): map a ReportingTaxonomy to a Module/ModuleVersion, or — when the SDMX source has no ReportingTaxonomy — materialise a Module anyway so the Table has a home ([§02 §3.4](../models-relationships/02_data_definition/03_detailed_mapping_rules.md)). A CategoryScheme on ingestion is disambiguated heuristically into a Framework or a TableGroup tree (see [§05 §2.12](../models-relationships/05_gaps/02_specific_gap_analysis.md)).

## 3.5 What needs review

| Output | Why it needs review |
| --- | --- |
| Default Item per Category | No SDMX source; synthesised or convention-picked. |
| `IsMetric` / stock-flow | Inferred when the representation is ambiguous. |
| Module materialisation | Synthesised when no ReportingTaxonomy exists. |
| CategoryScheme intent | Framework vs. TableGroup is heuristic. |
| Identifier normalisation | SDMX IDs reversed from any boundary normalisation. |
