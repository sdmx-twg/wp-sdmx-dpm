# 2. Specific gap analysis

This chapter provides detailed analysis of specific gap areas that require careful attention when transforming between SDMX and DPM.

## 2.1 Defaults and implicit dimensions

### 2.1.1 The problem

Both SDMX and DPM support the notion of "default" or "implicit" values, but with different mechanisms and semantics.

**SDMX approach**:
- **Wildcards in constraints**: `*` means "all values" for a dimension.
- **cascadeValues**: In MemberSelections, `true` includes child codes, `excludeRoot` includes children but not the parent.
- **Anchor values**: In Generic Series Data (GSD), dimensions with a single allowed value may be omitted from series keys.
- **Fixed values**: StructureMaps can specify FixedValueMaps where a component always has a constant value.

**DPM approach**:
- **Default Item**: A Category can designate one Item as its default (`defaultItem`). When a Property of that Category is used without an explicit value, the default is assumed.
- **Closed cells**: In closed tables, cell intersections imply fixed Property–Item pairs.
- **FilingIndicator defaults**: FilingIndicatorVariables may have default "not reported" semantics.

### 2.1.2 Gap analysis

| Scenario | SDMX | DPM | Gap |
|----------|------|-----|-----|
| Dimension with single allowed value | Can be omitted (anchor) | Must be explicit or use defaultItem | Implicit vs explicit handling differs |
| "All values" wildcard | `*` in constraints | No wildcard; enumerate or use full Category | Wildcard semantics not directly mappable |
| Hierarchical inclusion | cascadeValues on MemberValue | SubCategory membership | Different mechanisms; may not align exactly |
| Fixed constant value | FixedValueMap in StructureMap | Cell with category type | StructureMap context vs rendering context |

### 2.1.3 Recommendations

1. **Document anchor dimensions**: When converting SDMX → DPM, explicitly document which dimensions were anchored and their fixed values.
2. **Use defaultItem sparingly**: DPM defaultItem should only be used when the default is semantically meaningful, not just for convenience.
3. **Expand wildcards**: When converting SDMX constraints with wildcards to DPM, expand to explicit SubCategory membership where feasible.
4. **Preserve in metadata**: Store original SDMX constraint semantics in DPM descriptions for round-trip fidelity.

## 2.2 Multi-measure vs single OBS_VALUE

### 2.2.1 The problem

SDMX supports two measure patterns:
1. **Single generic measure**: One `OBS_VALUE` Measure with a `MEASURE` dimension that identifies what is being measured.
2. **Multiple explicit measures**: Multiple named Measures (e.g. `IMPORTS`, `EXPORTS`) in the MeasureDescriptor.

DPM uses **FactVariables**, where each FactVariable represents one measurable quantity. There is no "measure dimension" pattern; each measure is a separate Variable.

### 2.2.2 Gap analysis

| SDMX pattern | DPM mapping | Issues |
|--------------|-------------|--------|
| Single OBS_VALUE + MEASURE dimension | Multiple FactVariables (one per MEASURE code) | Lose the dimensional relationship; MEASURE becomes implicit in Variable identity |
| Multiple explicit Measures | Multiple FactVariables | Direct mapping; measure grouping may be lost |
| Measure cardinality (minOccurs/maxOccurs) | No equivalent | DPM does not model "optional" vs "mandatory" measures |
| MeasureRelationship for attributes | AttributeVariable.subject | Must create separate AttributeVariables per FactVariable |

### 2.2.3 Example

**SDMX DSD with MEASURE dimension**:
```
Dimensions: REF_AREA, TIME_PERIOD, MEASURE
Measure: OBS_VALUE
MEASURE Codelist: IMPORTS, EXPORTS, BALANCE
```

**DPM mapping**:
```
FactVariable: IMPORTS (dimensions: REF_AREA, TIME_PERIOD)
FactVariable: EXPORTS (dimensions: REF_AREA, TIME_PERIOD)
FactVariable: BALANCE (dimensions: REF_AREA, TIME_PERIOD)
```

The MEASURE dimension is "absorbed" into the Variable identity. The relationship between the three measures (they form a coherent group) is lost unless captured in Module organisation or naming conventions.

### 2.2.4 Recommendations

1. **Prefer explicit measures**: When designing SDMX DSDs intended for DPM conversion, use explicit Measures rather than a MEASURE dimension.
2. **Document measure groups**: When converting MEASURE-dimension patterns, document the original grouping in Module structure or TableGroups.
3. **Naming convention**: Use consistent prefixes or suffixes to indicate related FactVariables (e.g. `TRADE_IMPORTS`, `TRADE_EXPORTS`, `TRADE_BALANCE`).
4. **Round-trip metadata**: Store original SDMX measure pattern in descriptions for bidirectional conversion.

## 2.3 Stock vs flow and temporal semantics

### 2.3.1 The problem

Statistical data has fundamental temporal characteristics:
- **Stock**: Value at a point in time (e.g. balance sheet position on 31 Dec).
- **Flow**: Value over a period (e.g. transactions during Q1).
- **Frequency**: Reporting periodicity (annual, quarterly, monthly, etc.).

SDMX and DPM handle these differently, and XBRL (often used for DPM serialisation) has its own temporal model.

### 2.3.2 SDMX temporal model

- **TimeDimension**: Dedicated component with time-specific FacetValueTypes.
- **FacetValueTypes**: `observationalTimePeriod`, `reportingTimePeriod`, `basicTimePeriod`, `gregorianTimePeriod`, etc.
- **FREQ dimension**: Commonly used to indicate frequency (A, Q, M, D, etc.).
- **Stock/flow**: Not explicitly modelled; typically indicated by Concept semantics or Annotations.

### 2.3.3 DPM temporal model

- **Time Property**: A regular Property referencing a time-related Category.
- **Period types**: Implementation-defined; may distinguish instant vs duration.
- **Stock/flow**: May be indicated by Property semantics or FactVariable dataType.

### 2.3.4 XBRL temporal model

- **Instant**: Point in time (e.g. `2024-12-31`).
- **Duration**: Period with start and end (e.g. `2024-01-01` to `2024-12-31`).
- **periodType**: Concepts are declared as `instant` or `duration` in the taxonomy.

### 2.3.5 Gap analysis

| Aspect | SDMX | DPM | XBRL | Gaps |
|--------|------|-----|------|------|
| Time representation | TimeDimension + FacetValueType | Dimension with time Property | Period element (instant/duration) | Different granularity and semantics |
| Stock vs flow | Implicit (Concept semantics) | Implicit (Property semantics) | Explicit (periodType) | XBRL is most explicit; SDMX/DPM require inference |
| Frequency | FREQ dimension (common convention) | Property or Category | Not directly modelled | SDMX has strongest convention |
| Point-in-time | observationalTimePeriod values | Date values | instant element | Similar but format differs |
| Period | reportingTimePeriod values | Date range or convention | duration element | Representation differs |

### 2.3.6 Alignment challenges

1. **SDMX → DPM**: TimeDimension FacetValueTypes must map to appropriate DPM time Properties. The rich SDMX time semantics (reporting vs observational) may be simplified.

2. **DPM → XBRL**: DPM does not always distinguish stock/flow; the XBRL periodType must be inferred from Property semantics or explicitly configured.

3. **Frequency handling**: SDMX FREQ is a dimension; DPM may model frequency as a Property or derive it from the time period format; XBRL does not have a frequency concept.

### 2.3.7 Recommendations

1. **Explicit stock/flow marker**: Add a Property or annotation indicating stock vs flow when designing DPM structures intended for XBRL serialisation.
2. **Frequency alignment**: Establish conventions for how SDMX FREQ values map to DPM time Categories and XBRL period formats.
3. **Time period normalisation**: Define canonical time period formats that work across all three models.
4. **Documentation**: Clearly document temporal semantics in Property/Concept descriptions to enable correct inference.

## 2.4 Compound items — SDMX feature gap

### 2.4.1 The gap

SDMX has no explicit construct for expressing that a single code is *composed of* multiple values across different dimensions or categories. Every code in a Codelist is a flat, atomic value with no built-in mechanism to encode its internal structure.

DPM provides an explicit **Compound Category Item**: an item that declares its composition via a set of Property–Item pairs (a `Context` with `ContextCompositions`). This makes the multi-dimensional semantics machine-readable and reusable across tables and validation rules. See [glossary mapping rules §3.3.5](../01_glossary/03_detailed_mapping_rules.md#335-compound-item--known-limitation) for the mapping consequences.

### 2.4.2 DPM use case

The canonical example is a financial instrument such as "Treasury bill" (`TBILL`). In SDMX it appears as a flat code in `CL_INSTRUMENT` with no internal structure. In DPM it is a Compound Item explicitly composed of:

- Type of financial instrument (Property) = "Debt security" (Item)
- Sector of the issuer (Property) = "General governments" (Item)
- Original maturity (Property) = "Up to 18 months" (Item)

This composition enables DPM to use `TBILL` directly in slicing, aggregation, and cross-table validation without duplicating the business logic. SDMX cannot express this at the vocabulary level; the semantics must be documented externally or approximated via workarounds (see [§3.3.6](../01_glossary/03_detailed_mapping_rules.md#336-sdmx-workarounds-for-compound-item-semantics)).

### 2.4.3 Previous SDMX proposal

A compound item feature was previously proposed for inclusion in SDMX, inspired in part by the DPM model and similar needs expressed by the IMF. The proposal was rejected during standardisation. The precise version cycle and rejection rationale are not documented here; this section records that the gap is known and was previously considered.

### 2.4.4 Future SDMX candidate

The DPM compound item pattern provides a concrete, well-specified use case that could support revisiting the feature in a future SDMX version. Key arguments for reconsideration:

- **Expressiveness**: Compound items allow vocabulary-level encoding of multi-dimensional semantics that are currently left to documentation or external business rules.
- **Interoperability**: Without native compound item support, DPM→SDMX conversion is necessarily lossy for these structures.
- **Reuse**: Explicit composition at the codelist level enables automated validation and aggregation that SDMX currently cannot perform without out-of-band knowledge.

## 2.5 Summary of mitigation strategies

| Gap area | Primary mitigation | Secondary mitigation |
|----------|-------------------|---------------------|
| Defaults / implicit dimensions | Explicit documentation | Metadata preservation |
| Multi-measure patterns | Naming conventions + Module structure | Round-trip metadata |
| Stock vs flow | Explicit markers (Property/Annotation) | Documentation |
| Temporal semantics | Canonical formats + conventions | Transformation rules |
| Compound Items (§2.4) | Decomposition + documentation | Annotations (DPM_COMPOUND_COMPONENTS) |
| Cross-codelist hierarchies | SuperCategory + flattening | Accept partial loss |
| Attribute attachment | Convention-based mapping | Flatten to observation |
| Rendering | External specification | Accept loss for SDMX |
