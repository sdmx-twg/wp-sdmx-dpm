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

Only Items with `IsProperty = FALSE` become Codes. Items with `IsProperty = TRUE` are Properties and are handled next. The DPM **default Item** (`ItemCategory.IsDefaultItem`, e.g. `x0`/`qx0`) *is* emitted as an ordinary Code — it is a real member of the value domain and is referenced by Hierarchies and Constraints — with its default-member status preserved in a `DPM_DEFAULT_ITEM` annotation. (The flag is XBRL-validation machinery: it marks which member a Property assumes when left unstated; SDMX has no implicit default, so the Code stays but the *implicit-default behaviour* is made explicit in constraints — see [Constraints](#constraints) below.)

> **Codelist ids are emitted UPPER-CASE** (e.g. DPM category `qEC` → Codelist `QEC`), and every reference to a Codelist — the Concept `CoreRepresentation`, the DSD Dimension `Enumeration`, and Hierarchy `Code` URNs — uses the same upper-cased id. This is a workaround, *not* an SDMX requirement (lower-case ids are valid SDMX): the Fusion Metadata Registry uppercases every Codelist maintainable id on load but leaves references to it untouched, so a lower-case id loads yet fails strict reference resolution at query time. The original DPM code is preserved in a `DPM_CODE` annotation, so the upper-casing is reversible on the SDMX → DPM path. Code ids *inside* a Codelist, and all other artefact ids (Concept, ConceptScheme, DSD, Dimension), are left as-is — FMR does not alter those. **Revisit and remove this upper-casing once FMR resolves lower-case Codelist references** (see `out/fmr-codelist-id-casing.md`); the single point to change is `ids.normalise_codelist_id()`.

### Hierarchical SubCategory → Hierarchy

For each translated Category, every **hierarchical SubCategory** over it (a `SubCategory` whose `SubCategoryItem`s carry `ParentItemID` links) becomes one SDMX **`Hierarchy`** over the Category's Codelist. Each item becomes a `HierarchicalCode` that *references* a Code in the Codelist by URN (codes are not duplicated), nested to reproduce the parent–child tree. Flat (non-hierarchical) SubCategories are not emitted here.

```xml
<Hierarchy id="GA5" agencyID="EBA" version="1.0" isExternalReference="false" hasFormalLevels="false">
  <Name xml:lang="en">EU geographies</Name>
  <HierarchicalCode id="x0">
    <Code>urn:sdmx:org.sdmx.infomodel.codelist.Code=EBA:GA(1.0).x0</Code>
    <HierarchicalCode id="AT">
      <Code>urn:sdmx:org.sdmx.infomodel.codelist.Code=EBA:GA(1.0).AT</Code>
    </HierarchicalCode>
  </HierarchicalCode>
</Hierarchy>
```

See [§3.4.3 of the glossary mapping rules](../models-relationships/01_glossary/03_detailed_mapping_rules.md#343-hierarchies) for the full rule. pysdmx (1.16) cannot serialise Hierarchies, so the converter writes this tier with a small in-house SDMX-ML writer; the output is FMR-loadable.

### Property → Concept

Each Property becomes a Concept in the single ConceptScheme for the agency, named by convention `CS_<AGENCY>` (e.g. `CS_EBA`). The enumerated representation points at the Codelist mapped above; metric Properties carry a numeric `TextFormat`. See [§5 Data types mapping](05_data_types_mapping.md) for the full representation rules.

```xml
<ConceptScheme id="CS_EBA" agencyID="EBA" version="1.0">
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

DPM has no explicit ConceptScheme container, so the choice of scheme is **convention-driven**: one ConceptScheme per owner/agency, with the conventional id `CS_<AGENCY>` (e.g. `CS_EBA`). The Property's `IsMetric`/DataType drive the representation. `PeriodType` (stock/flow) has no native SDMX home — preserve it as an annotation or in the Concept description (see [§1.3](01_methodology.md)).

## 2.4 Step 3 — Data definition

### Table → Dataflow + DSD

The DPM Table maps to one SDMX Dataflow plus its DSD. `TableVersion.Code` → Dataflow `id`; `TableVersion.Name` → Dataflow `Name`.

- KeyVariables → **Dimensions** (in key order), each referencing the Concept mapped from its Property; enumerated Properties take the Codelist as `LocalRepresentation`.
- FactVariables → **Measures**.
- AttributeVariables → **DataAttributes**, with their `variable_attribute` ConceptRelation re-expressed as an `AttributeRelationship`.

> **Non-flat tables (the EBA reality).** EBA tables are non-flat, so dimensions are not 1:1 Headers but are reconstructed from two sources (models-relationships §3.2.3.2): (1) the **context Properties** — the distinct Properties across all FactVariable Contexts; and (2) the **open keys** — the KeyVariables on the table's open axes (`HasOpenRows/Columns/Sheets`), which never appear in a Context because their rows are instantiated at report time. Both become Dimensions: enumerated ones take their Codelist as `LocalRepresentation`, non-enumerated ones a `TextFormat`. The converter reads the context Properties from the Contexts and appends the open keys after them (`reader.read_table_components` + `reader.read_open_keys`); a Property used as a context dimension is never also a Measure. Example — C_27.00 yields the context dimension `qBEA` plus the open keys `qNCO` (counterparty id type, enumerated → Codelist `QCO`) and `qINC` (individual-clients flag, free text → `TextFormat`).

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

The EBA tables are non-flat: there is no separate DPM constraint artefact — the set of a table's FactVariable **Contexts** *is* its valid-series space (models-relationships §3.3.2.2). Each table produces one `DataConstraint` (SDMX-ML 3.0; `ContentConstraint` in 2.1) attached to its `Dataflow`. The **representation depends on whether the table is closed or open** (models-relationships §3.3.8):

- **Closed table** (`IsFlat=FALSE` and no open axis — `HasOpenRows/Columns/Sheets` all FALSE): the data points are a finite, enumerated set, so the faithful representation is a **`DataKeySet`** listing the distinct full dimension keys — one `Key` (series key) per series. Data points that differ only by metric collapse to one series key (an SDMX measure is not part of the key).
- **Open table** (any open axis) or **flat table**: the key set is unbounded (open rows) or read off SubCategories (flat), so the space is described dimension-wise as a **`CubeRegion`** — one `KeyValue` per dimension listing the allowed Items. A `cascadeValues` hierarchy is flattened to explicit members.

**Open keys in the constraint.** An open table's dimensions include the open keys (above). The context dimensions get their `KeyValue` from the per-data-point keys; the open keys are added separately (their rows are open, so they are absent from those keys): an **enumerated** open key is restricted to the finite Item subset of its open-axis SubCategory and listed as a `KeyValue` (e.g. C_27.00 `qNCO` → `{qx2000, qx2001}`), while a **non-enumerated** open key (e.g. `qINC`) is a Dimension of the DSD but is *omitted* from the `CubeRegion`, leaving it unconstrained. The converter resolves these from `reader.read_open_keys` → `read_table_constraint_values(open_keys=…)` → `table_to_content_constraint(open_key_values=…)`, and records the addition (`constraint.open_key_values`). Open keys arise only on open tables, so they never reach a `DataKeySet`.

```xml
<!-- Closed table (C_26.00): enumerated series keys -->
<DataConstraint id="C_26_00_CONSTRAINTS" agencyID="EBA" version="1.0" role="Allowed">
  <ConstraintAttachment>
    <Dataflow>urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=EBA:C_26_00(1.0)</Dataflow>
  </ConstraintAttachment>
  <DataKeySet isIncluded="true">
    <Key><KeyValue id="qEBF"><Value>qx0</Value></KeyValue></Key>      <!-- default, explicit -->
    <Key><KeyValue id="qEBF"><Value>qx2011</Value></KeyValue></Key>
  </DataKeySet>
</DataConstraint>

<!-- Open table (C_28.00): per-dimension value lists -->
<DataConstraint id="C_28_00_CONSTRAINTS" agencyID="EBA" version="1.0" role="Allowed">
  <ConstraintAttachment>
    <Dataflow>urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=EBA:C_28_00(1.0)</Dataflow>
  </ConstraintAttachment>
  <CubeRegion include="true">
    <KeyValue id="qFI"><Value>qx2006</Value><Value>qx0</Value></KeyValue>  <!-- default explicit -->
  </CubeRegion>
</DataConstraint>
```

**Default Item made explicit.** Each data point (a fact Variable, with a metric) fixes a value for every dimension; a dimension its Context does *not* pin takes that Category's **default Item** (`IsDefaultItem`, `qx0`). DPM leaves this implicit; SDMX has no implicit default. So every data point — including a context-less one (every dimension at its default) — contributes a full key, and the default Item appears explicitly: as that dimension's value in each defaulting series key (DataKeySet), or among the dimension's allowed values (CubeRegion). The review report records the addition (`constraint.default_item_explicit`). *(Earlier the converter counted only context-bearing data points and so missed C_26.00's three context-less points, dropping `qx0`; the denominator is now all fact data points.)*

**Measure in the constraint.** A series key in SDMX is dimensions only; a (non-enumerated) Measure has no key value, so it cannot discriminate series keys (FMR rejects a value-less measure component in a `DataKey`). The valid measures are already declared by the DSD `MeasureList`; SDMX 3.0 *does* allow re-stating them as value-less `<Component>` entries in a `CubeRegion`, but that is redundant with the DSD and pysdmx cannot serialise it. The converter therefore does not put measures in the constraint. (Consequence: data points that differ only by metric — e.g. C_26.00's three `qEBF=qx0` points — collapse to one series key; this is an inherent DPM→SDMX gap, see models-relationships §3.3.8 caveat.)

> **Extended codelists are *not* used to restrict value domains (pysdmx limitation).** Asked whether a Measure's set of allowed values could be constrained: the structural alternative to a `ContentConstraint` is, in SDMX 3.0, a **restrictive Extended Codelist** — a Codelist that `extends` a base Codelist with an `InclusiveCodeSelection`/`ExclusiveCodeSelection` (the modelling equivalent of a DPM SubCategory; see [models-relationships §04 §2.1](../models-relationships/04_versioning_and_extensibility/02_extensibility_patterns.md#21-value-domain-extension)). Used as a component's `LocalRepresentation`, it confines that dimension or measure to the selected subset without a separate constraint artefact.
>
> **The converter does not emit extended codelists, and this is deliberate — do not add it.** The blocker is the writer, not the registry: **pysdmx 1.16's `Codelist` model has no `CodelistExtension`/`extends` field** (only `items` + `sdmx_type`), so an extended codelist simply cannot be serialised — the same class of gap as Hierarchy and the constraint `<Component>`. The converter instead restricts enumerated value domains through the `ContentConstraint` (`CubeRegion`/`DataKeySet`), which pysdmx serialises and FMR resolves.
>
> **FMR materializes extended codelists into standard codelists (verified, `sdmxio/fmr-mysql:latest`).** FMR *reads* an extended codelist on submit — both restrictive (`InclusiveCodeSelection`) and additive (multi-codelist merge with `prefix`) load with status `Success` — but it then **resolves it into an ordinary codelist** for all normal use: the SDMX REST v2 endpoint by default, `?detail=full`, and the GUI all present a plain codelist with the inherited codes inlined as native `<Code>` and no extension marker. The original `<CodelistExtension>` definition survives only as a retrievable source form at `?detail=raw`; it is not surfaced as a first-class artefact anywhere the codelist is consumed. So even setting pysdmx aside, an extended codelist would not round-trip as an *extension* — FMR would flatten it to a standard codelist on the SDMX → DPM path. Net: the resulting *value restriction* would hold in FMR, but (a) pysdmx cannot produce an extended codelist and (b) FMR would convert it to a standard codelist anyway, so the mechanism buys nothing over a `ContentConstraint` here.

Unlike Hierarchies, pysdmx (1.16) *does* serialise `DataConstraint` (both `CubeRegion` and `DataKeySet`), so this tier goes through the standard writer. Because a constraint references its Dataflow (a structure) and the Codelist Codes it lists as values, it is emitted as the **last** dependency tier (`<base>.5_constraints.xml`) and loaded into FMR after the structures — see [the submission-race note](../../out/fmr-structure-submission-race.md). The `constraints` layer requires `data-def` (a constraint with no Dataflow is meaningless) and is on by default.

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
