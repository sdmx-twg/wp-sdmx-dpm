# 2. DPM → SDMX

This chapter works a complete DPM-to-SDMX conversion end to end, following the [methodology](01_methodology.md). The detailed rules behind each step live in [§01 §3 Glossary detailed mapping rules](../models-relationships/01_glossary/03_detailed_mapping_rules.md) and [§02 §3 Data Definition detailed mapping rules](../models-relationships/02_data_definition/03_detailed_mapping_rules.md); here we show how they combine.

We convert a small slice of an EBA-style DPM database into SDMX structures.

## 2.1 Source (DPM)

- **Category** `CL_COUNTRY` ("Country") with **Items** `ES` (Spain), `FR` (France).
- **Property** `RCP` ("Residence of counterparty"), enumerated over the geographical-area domain, `IsMetric = FALSE`.
- **Property** `OBS_VALUE`, `IsMetric = TRUE`, DataType Decimal.
- A **Table** `CBD2` ("Consolidated Banking data") with a KeyVariable on `RCP` and a FactVariable on `OBS_VALUE`.

## 2.2 Step 1 — Owner / Agency

Map the DPM Owner (`eba`) to an SDMX `Agency` (`EBA`) in an AgencyScheme. Every artefact emitted below is owned by this agency. See [§04 §3.1 Agency–Organisation](../models-relationships/04_versioning_and_extensibility/03_detailed_mapping_rules.md).

## 2.3 Step 2 — Glossary

### Category → Codelist, Item → Code

Each enumerated Category becomes a Codelist; each Item becomes a Code. The `ItemCategory.Code` becomes the SDMX Code `id`; the Item `Name` becomes the Code `Name` (preserving all languages).

```xml
<Codelist id="CL_COUNTRY" agencyID="EBA" version="1.0">
  <Name xml:lang="en">Country</Name>
  <Code id="ES"><Name xml:lang="en">Spain</Name></Code>
  <Code id="FR"><Name xml:lang="en">France</Name></Code>
</Codelist>
```

Only Items with `IsProperty = FALSE` become Codes. Items with `IsProperty = TRUE` are Properties and are handled next. DPM default-item flags (`IsDefaultItem`, e.g. `x0`) are XBRL-validation machinery and are **not** emitted as Codes.

### Property → Concept

Each Property becomes a Concept in a ConceptScheme owned by the agency. The enumerated representation points at the Codelist mapped above; metric Properties carry a numeric `TextFormat`.

```xml
<ConceptScheme id="STANDALONE_CONCEPTS" agencyID="EBA" version="1.0">
  <Concept id="RCP">
    <Name xml:lang="en">Residence of counterparty</Name>
    <CoreRepresentation>
      <Enumeration><Ref id="CL_GEOG" class="Codelist"/></Enumeration>
    </CoreRepresentation>
  </Concept>
  <Concept id="OBS_VALUE">
    <Name xml:lang="en">Observation value</Name>
    <CoreRepresentation>
      <TextFormat textType="Decimal"/>
    </CoreRepresentation>
  </Concept>
</ConceptScheme>
```

DPM has no explicit ConceptScheme container, so the choice of scheme is **convention-driven**: typically one ConceptScheme per owner (or per semantic domain). The Property's `IsMetric`/DataType drive the representation. `PeriodType` (stock/flow) has no native SDMX home — preserve it as an annotation or in the Concept description (see [§1.3](01_methodology.md)).

## 2.4 Step 3 — Data definition

### Table → Dataflow + DSD

The DPM Table maps to one SDMX Dataflow plus its DSD. `TableVersion.Code` → Dataflow `id`; `TableVersion.Name` → Dataflow `Name`.

- KeyVariables → **Dimensions** (in key order), each referencing the Concept mapped from its Property; enumerated Properties take the Codelist as `LocalRepresentation`.
- FactVariables → **Measures**.
- AttributeVariables → **DataAttributes**, with their `variable_attribute` ConceptRelation re-expressed as an `AttributeRelationship`.

```xml
<DataStructure id="EBA_CBD2" agencyID="EBA" version="1.0">
  <DataStructureComponents>
    <DimensionList>
      <Dimension id="RCP" position="1">
        <ConceptIdentity><Ref id="RCP" class="Concept"/></ConceptIdentity>
        <LocalRepresentation>
          <Enumeration><Ref id="CL_GEOG" class="Codelist"/></Enumeration>
        </LocalRepresentation>
      </Dimension>
    </DimensionList>
    <MeasureList>
      <Measure id="OBS_VALUE">
        <ConceptIdentity><Ref id="OBS_VALUE" class="Concept"/></ConceptIdentity>
        <LocalRepresentation><TextFormat textType="Decimal"/></LocalRepresentation>
      </Measure>
    </MeasureList>
  </DataStructureComponents>
</DataStructure>

<Dataflow id="CBD2" agencyID="EBA" version="1.0">
  <Name xml:lang="en">Consolidated Banking data</Name>
  <Structure><Ref id="EBA_CBD2" version="1.0" class="DataStructure"/></Structure>
</Dataflow>
```

### Constraints

A DPM SubCategory restricting a Header's allowed Items becomes an SDMX `ContentConstraint` with a `CubeRegion` listing the allowed members for that Dimension. A `cascadeValues` hierarchy must be flattened to explicit members.

### Module / Framework

- The DPM **ModuleVersion** the Table belongs to maps to a **ReportingTaxonomy** (version); ReportingCategories carry the TableGroup navigation. See [§02 §3.4](../models-relationships/02_data_definition/03_detailed_mapping_rules.md).
- The DPM **Framework** has no SDMX equivalent: emit one **CategoryScheme** per Framework, with each Module as a Category, paired with the ReportingTaxonomy. See [§05 §2.11](../models-relationships/05_gaps/02_specific_gap_analysis.md).

## 2.5 What needs review

| Output | Why it needs review |
| --- | --- |
| ConceptScheme grouping | DPM has no scheme; the partition is a convention. |
| `periodType` / stock-flow | No native SDMX target; preserved via annotation. |
| Compound Items | No SDMX counterpart; decompose or annotate. |
| Identifier normalisation | DPM codes may need adjusting to SDMX ID syntax. |

The reverse direction is covered in [§3 SDMX → DPM](03_sdmx_to_dpm.md).
