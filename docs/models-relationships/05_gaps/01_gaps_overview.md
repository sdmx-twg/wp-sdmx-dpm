# 1. Gaps overview

This chapter provides a systematic analysis of semantic gaps, representation mismatches, and potential information loss when transforming between SDMX and DPM. Understanding these gaps is essential for designing robust bidirectional mappings and for documenting where manual intervention or conventions are required.

## 1.1 Types of gaps

Gaps between SDMX and DPM fall into three categories:

| Gap type | Description | Impact |
|----------|-------------|--------|
| **Semantic gaps** | Concepts that exist in one model but have no counterpart in the other | Requires convention or extension to represent |
| **Representation gaps** | Concepts that exist in both models but are structured differently | Requires transformation logic; may lose precision |
| **Implicit vs explicit gaps** | Information that is explicit in one model but implicit (or derived) in the other | Requires inference or defaults during transformation |

## 1.2 Gap inventory by layer

### Glossary layer gaps

| Gap | SDMX | DPM | Notes |
|-----|------|-----|-------|
| Concept grouping | ConceptScheme (explicit container) | Single cross-domain glossary | DPM Properties are not grouped into schemes; organisation is via Categories and ownership |
| Compound values | No dedicated artefact | CompoundItem | SDMX must use multiple dimensions or structured codes to represent compound values |
| Cross-codelist hierarchy | Hierarchy (multi-parent, cross-codelist) | SubCategory (single Category) | DPM SubCategories are limited to one Category; complex SDMX Hierarchies may not map exactly |
| Super category | Extended Codelist (approximation) | SuperCategory (explicit) | DPM SuperCategories explicitly unite Categories; SDMX Extended Codelists have different semantics |
| Generic subject classification | CategoryScheme / Category | No direct counterpart | SDMX CategoryScheme is generic and retrofittable; DPM partitions classification across Framework/Module/Category/SuperCategory. Used as a backdoor for DPM-only navigation — see [§2.12](02_specific_gap_analysis.md#212-categoryscheme-sdmx-backdoor-for-dpm-only-classification) |
| Glossary versioning | Explicit Codelist/ConceptScheme versions | Release-based change log; no explicit item version | DPM versioning is implicit/snapshot-based and ModuleVersion-anchored — a major interoperability challenge raised as a recommendation to the DPM Alliance, see [§2.13](02_specific_gap_analysis.md#213-dpm-glossaryversioning-recommendation-to-the-dpm-alliance) |

### Data definition layer gaps

| Gap | SDMX | DPM | Notes |
|-----|------|-----|-------|
| Time dimension | TimeDimension (dedicated type) | Dimension with time Property | SDMX enforces time semantics via component type; DPM relies on Property definition |
| Partial key groups | GroupDimensionDescriptor | No equivalent | DPM cannot directly model intermediate attachment levels |
| Attribute attachment | AttributeRelationship (5 levels) | Implicit in AttributeVariable.subject | SDMX attachment levels are explicit; DPM attachment is implicit |
| Key enumeration | DataKeySet (explicit series) | No equivalent | DPM constraints operate at value-domain level, not key-combination level |
| Rendering / presentation | Not modelled | Table / Header / Cell | SDMX excludes presentation; DPM has a complete rendering layer |
| Filing indicator | No equivalent | FilingIndicatorVariable | DPM-specific artefact for table-level reporting control |
| Open/closed table patterns | Not modelled | Headers with fixed Context vs Key Headers on open axes | DPM distinguishes open and closed axes; SDMX has no equivalent |

### Organisational layer gaps

| Gap | SDMX | DPM | Notes |
|-----|------|-----|-------|
| Organisation schemes | Dedicated schemes per role | Single Organisation with role attribute | Different modelling approaches for the same concept |
| Domain wrapper | No direct counterpart | Framework | DPM Framework groups Modules under one regulatory/statistical domain; SDMX bridges via CategoryScheme convention — see [§2.11](02_specific_gap_analysis.md#211-framework-dpm-feature-without-sdmx-equivalent) |
| Provisioning | ProvisionAgreement / Datasource | Not modelled | DPM focuses on requirements; provisioning is external |
| Process / lineage | Process / ProcessStep | Not modelled | DPM does not model data production workflows |
| Generic annotation | Annotation (key-value) | Typed description fields | SDMX is more flexible; DPM is more structured |
| Release milestone | Versioning only | Release (with applicationDate) | DPM has explicit temporal publication; SDMX uses version validity |
| Soft delete | Version validity (validFrom/validTo) | Deactivation artefact | Different mechanisms for lifecycle management |
| Supporting documents / attachments | Referential metadata (structured reports only) | Document modules (to be confirmed with EBA) | Binary file transmission not natively supported by SDMX; relevant future extension, not central — see [§2.14](02_specific_gap_analysis.md#214-supporting-documents-binary-attachments-future-extension) |

## 1.3 Critical semantic gaps

The following gaps have significant impact on bidirectional transformation and require careful handling.

### 1.3.1 Compound Items (DPM → SDMX)

**Problem**: DPM CompoundItems encode multiple Property–Item pairs in a single Item. SDMX has no equivalent.

**Example**: A CompoundItem "Treasury bill" composed of:
- Instrument type = "Debt security"
- Issuer sector = "General government"
- Original maturity = "Up to 18 months"

**Mitigation options**:
1. **Decompose into dimensions**: Map each Property to an SDMX Dimension; lose the single-item semantics.
2. **Structured code**: Encode the composition in the Code id/name; lose machine-readability.
3. **Annotation**: Store the composition in Annotations; lose standard processing.

### 1.3.2 Cross-codelist Hierarchies (SDMX → DPM)

**Problem**: SDMX Hierarchies can span multiple Codelists and support multiple parents. DPM SubCategories are limited to a single Category.

**Example**: A geographic hierarchy mixing ISO country codes and NUTS region codes with multiple parent relationships.

**Mitigation options**:
1. **SuperCategory**: Create a DPM SuperCategory uniting the underlying Categories; flatten to single-parent.
2. **Multiple SubCategories**: Create separate SubCategories for each source Codelist.
3. **Lossy conversion**: Accept that some hierarchical relationships cannot be represented.

### 1.3.3 Attribute attachment levels (SDMX → DPM)

**Problem**: SDMX explicitly models 5 attachment levels (Dataflow, Dimension, Group, Observation, Measure). DPM AttributeVariables reference a subject Variable but do not specify level.

**Example**: An SDMX DataAttribute attached at GroupRelationship level (partial key).

**Mitigation options**:
1. **Convention**: Define attachment level as part of the AttributeVariable's dimensional signature.
2. **Flatten to observation**: Attach all attributes at observation level; duplicate values where needed.
3. **Metadata**: Store the original attachment level in a description or extension field.

### 1.3.4 Rendering layer (DPM → SDMX)

**Problem**: DPM Tables, Headers, and Cells have no SDMX equivalent. SDMX intentionally excludes presentation.

**Mitigation options**:
1. **External specification**: Document rendering separately (e.g. in a companion PDF or implementation guide).
2. **Annotations**: Store rendering hints in SDMX Annotations; non-standard and limited.
3. **Accept loss**: Acknowledge that rendering information is lost in SDMX representation.

## 1.4 Representation precision gaps

These gaps involve information that exists in both models but may lose precision during transformation.

### 1.4.1 Data type mapping

SDMX and DPM have overlapping but not identical data type systems.

| SDMX FacetValueType | DPM DataType / FactDataType | Notes |
|---------------------|----------------------------|-------|
| `String` | `String` | Direct mapping |
| `Integer` | `Integer` | Direct mapping |
| `Decimal` | `Decimal` | Direct mapping |
| `Boolean` | `Boolean` | Direct mapping |
| `DateTime`, `Date`, `Time` | `Date` | DPM has only Date; time precision may be lost |
| `observationalTimePeriod` | (time Property) | SDMX has richer time period semantics |
| `Duration` | – | No DPM equivalent |
| `URI` | `String` | Semantic loss |
| `XHTML` | `String` | Formatting lost |
| – | `Monetary` | DPM-specific; maps to Decimal with unit |
| – | `Percentage` | DPM-specific; maps to Decimal with semantics |

### 1.4.2 Facet constraints

SDMX Facets provide fine-grained constraints (minLength, maxLength, pattern, minValue, maxValue, decimals, etc.). DPM has DataTypes but less granular facet controls.

**Impact**: Constraints may be loosened or lost when converting SDMX → DPM.

### 1.4.3 Multilingual text

Both models support multilingual text (SDMX: `InternationalString` pattern; DPM: `InternationalString` type). However, the set of supported languages and fallback behaviour may differ between implementations.

## 1.5 Implicit vs explicit gaps

### 1.5.1 Default values and wildcards

**SDMX**: Wildcards in constraints (e.g. `*` for "all values") and cascadeValues for hierarchies.

**DPM**: Defaults via Category.defaultItem and SubCategory membership.

**Gap**: The semantics of "unspecified" or "all" differ; explicit mapping rules are needed.

### 1.5.2 Observation vs series orientation

**SDMX**: Data can be series-oriented (SeriesKey + Observations) or flat (all dimensions at observation level).

**DPM**: Variables define dimensional signatures; orientation is implicit in the table pattern.

**Gap**: Converting between orientations may require restructuring data.

### 1.5.3 Measure cardinality

**SDMX**: DSDs can have single or multiple Measures with explicit minOccurs/maxOccurs.

**DPM**: Each FactVariable is a single measure; cardinality is implicit in Variable definitions.

**Gap**: Multi-measure SDMX structures may map to multiple DPM FactVariables; the grouping relationship may be lost.
