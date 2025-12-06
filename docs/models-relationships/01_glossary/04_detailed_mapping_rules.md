# 4. Detailed mapping rules

> [!NOTE]
> - Add coding/naming issues here for each mapping
> - Explain the constraints under which a mapping is simple (e.g., an organisation that uses only one Concept Scheme, vs many Concept Schemes), and proposed conventions if simple mapping is not possible.
> - Shall we add here something about versioning and extensibility? Or as a separate chapter?



This chapter provides the detailed rules for each of the high-level correspondences described in chapter 3.
## 4.1 ConceptSchema ↔ DPM Glossary
In the Data Point Model (DPM), there is no construct equivalent to the SDMX `ConceptScheme`.  
In SDMX, each `ConceptScheme` has its own identification space (defined by `agencyId`, `id`, and `version`).  
If concepts from multiple `ConceptSchemes` are combined into a single DPM glossary, identifier collisions may occur (for example, two concepts with the same name, such as `COUNTRY`, but with different meanings). 

### 4.1.1 Basic mapping

To resolve this issue, a namespace can be created for each `ConceptScheme` by adopting an approach based on **composite keys** in the DPM glossary:

---

### Glossary with Composite Keys
In the DPM glossary, define each concept using a composite key in the following format:

```
{agencyID}.{ConceptSchemeId}.{ConceptId}
```

*Example:*
```
ECB.CL_COUNTRY.COUNTRY
```

This ensures uniqueness without renaming the concepts.

---

### *Example ConceptScheme*
```xml
<ConceptScheme id="CL_CONCEPTS" agencyID="ECB" version="1.0">
    <Name xml:lang="en">Statistical Concepts</Name>
    <Description xml:lang="en">Concepts used for macroeconomic indicators</Description>
    <Concept id="FREQ">
        <Name xml:lang="en">Frequency</Name>
        <Description xml:lang="en">Reporting frequency</Description>
        <Representation>
            <CodelistRef id="CL_FREQ" agencyID="ECB" version="1.0"/>
        </Representation>
    </Concept>
    <Concept id="REF_AREA">
        <Name xml:lang="en">Reference Area</Name>
        <Description xml:lang="en">Geographical coverage</Description>
        <Representation>
            <CodelistRef id="CL_AREA" agencyID="ECB" version="1.0"/>
        </Representation>
    </Concept>
    <Codelist id="CL_FREQ" agencyID="ECB" version="1.0">
        <Name xml:lang="en">Frequency</Name>
        <Description xml:lang="en">Reporting frequency codes</Description>
        <Code id="A">
            <Name xml:lang="en">Annual</Name>
        </Code>
        <Code id="Q">
            <Name xml:lang="en">Quarterly</Name>
        </Code>
        <Code id="M">
            <Name xml:lang="en">Monthly</Name>
        </Code>
    </Codelist>
</ConceptScheme>
```

---

## 4.1.2 **Mapping Details: SDMX ConcepSchema → DPM Glossary**

### **Concepts**
| SDMX Concept | Composite Key in DPM Glossary | Description            |
|--------------|--------------------------------|------------------------|
| FREQ         | ECB.CL_CONCEPTS.FREQ          | Reporting frequency    |
| REF_AREA     | ECB.CL_CONCEPTS.REF_AREA      | Geographical coverage  |

### **Codelist for FREQ**
| SDMX Code | Composite Key in DPM Glossary | Description |
|-----------|--------------------------------|-------------|
| A         | ECB.CL_FREQ.A                 | Annual      |
| Q         | ECB.CL_FREQ.Q                 | Quarterly   |
| M         | ECB.CL_FREQ.M                 | Monthly     |


## 4.2 Codelist ↔ Category
An SDMX CodeList is a structural component of the SDMX standard that defines a **set of coded values** for a dimension, attribute, or concept. SDMX CodeList can be mapped to an Enumerated Category in DPM.

### 4.2.1 Basic mapping
- For each **SDMX Codelist**:
  - Create one **Enumerated DPM Category**.

#### SDMX Codelist Key Features
- **Identification**: `id`, `agencyID`, `version`
- **Content**:
  - One or more **Code** elements (e.g., ES, FR, DE)
  - Each Code includes:
    - `id` (unique identifier)
    - `Name` (human-readable label)
    - Optional: description, order, references
- **Multilingual support**: Labels can be provided in multiple languages
- **Reusable**: Can be referenced in multiple Data Structure Definitions (DSDs)

#### **Example ConceptScheme**
```xml
<Codelist id="CL_COUNTRY" agencyID="ECB" version="1.0">
  <Name xml:lang="en">Country</Name>
  <Description xml:lang="en">List of countries for ECB reporting (from SDMX CodeList CL_COUNTRY)</Description>
  <Code id="ES">
    <Name xml:lang="en">Spain</Name>
  </Code>
  <Code id="FR">
    <Name xml:lang="en">France</Name>
  </Code>
</Codelist>
```

### 4.2.2 Mapping details

| Attribute | Value |
|---|---|
| CategoryID | (system-generated, e.g., 1001) |
| Code | {agencyID}.{ConceptSchemeId}.{CodelistId}|
| Name | Codelist.Name |
| Description | Codelist.Description|
| IsEnumerated | TRUE |
| IsSuperCategory | FALSE |
| IsActive | TRUE |
| IsExternalRefData | FALSE |
| RefDataSource | NULL |
| RowGUID | (system-generated UUID) |

## Example Mapping details

| Attribute | Value |
|---|---|
| CategoryID | (system-generated, e.g., 1001) |
| Code | ECB.CS_REPORTING.CL_COUNTRY |
| Name | Country |
| Description | List of countries for ECB reporting (from SDMX CodeList CL_COUNTRY) |
| IsEnumerated | TRUE |
| IsSuperCategory | FALSE |
| IsActive | TRUE |
| IsExternalRefData | FALSE |
| RefDataSource | NULL |
| RowGUID | (system-generated UUID) |

### 4.2.2 Extended Codelists and Super Categories

- **Extended Codelist (subset-only)**:
  - If an Extended Codelist only restricts a base codelist to a subset of its codes (no new codes):
    - Map the base codelist to a Category.
    - Create a **Subcategory** representing the subset, linked to that Category.

- **DPM Super Category**:
  - Super Categories correspond generally to **Extended Codelists** in SDMX:
    - every Super Category can be expressed as an Extended Codelist (grouping codes from a base codelist); but
    - not every Extended Codelist maps back to a Super Category (some are better seen as Subcategories).

- **Extended Codelist with additional codes**:
  - SDMX allows Extended Codelists to introduce **extra codes** not present in the base codelist.
  - DPM Subcategories can only contain items from a single Category; they cannot directly introduce entirely new items that are not in the Category.
  - Recommended approach:
    - Map the subset of base codes to a **Subcategory**.
    - For additional codes:
      - either extend the underlying Category with new Category Items (documenting that they originate from an Extended Codelist only), or
      - treat them as part of a separate Category/CategoryItem set and document the relationship (e.g. in the versioning/extensibility section).

### 4.2.3 Geospatial Codelists

- **Geospatial Codelist → Category (enumerated)**:
  - Create a Category and Category Items in the same way as for a normal codelist.
  - Note that geospatial aspects (geometry, CRS, etc.) have no direct slot in DPM; they must be handled via:
    - naming conventions,
    - external metadata, or
    - extended attributes in implementations.

## 4.3 Code ↔ Category Item

### 4.3.1 Simple codes

- For each **Code** in an SDMX Codelist (or Extended Codelist that does not introduce additional semantics):
  - Create a **Simple Category Item** in the corresponding Category.
  - Map:
    - SDMX `agencyID` (if present at code level) or codelist `agencyID` → Category Item owner.
    - Code `id` → Category Item code.
    - Code name and description → Category Item name and description.
  - Default flags (as in ECB Simplified Approach):
    - `is_default = false`,
    - `is_compound = false`,
    - `is_obsolete = false`.

### 4.3.2 Compound Category Items

- **DPM Compound Category Item** encodes a composition of multiple items across categories (e.g. the “Treasury bill” example in the report).

- **DPM → SDMX**:
  - Map Compound Category Item → **Code**:
    - one Code in SDMX represents the compound item;
    - the internal structure (links to other Category Items) is not represented in core SDMX.
  - This mapping is lossy: composition information is lost unless captured via annotations or external documentation.

- **SDMX → DPM** (creating compound items):
  - If a particular Code is known (from business rules or ECB mappings) to represent a combination of other dimensions/categories:
    - model it as a Compound Category Item in DPM, with explicit links to the constituent Category Items;
    - even though SDMX does not encode that composition explicitly.
  - This is mainly a design choice on the DPM side; SDMX does not force it.

## 4.4 Subsets and hierarchies

### 4.4.1 Subsets (constraints and extended codelists)

Subsets of codelists (e.g. “codes allowed in a specific Dataflow”) can arise from:
- Extended Codelists (subset-only), and/or
- SDMX **Content Constraints** (cube region constraints).

Mapping rules:

- **Subset derived from Extended Codelist or Constraints**:
  - Create a **Subcategory** under the mapped Category.
  - The items of the Subcategory correspond to the allowed Category Items for the context (Dataflow/DSD).
  - Use constraint metadata (e.g. include/exclude, cascade flags) to determine which items belong to the Subcategory.

### 4.4.2 Hierarchies

- **Hierarchy over a single codelist**:
  - When an SDMX Hierarchy only includes codes from one codelist:
    - map the codelist to a Category,
    - represent the hierarchy using a Subcategory that carries parent–child relationships between Category Items.

- **Hierarchy over multiple codelists**:
  - DPM Subcategories must draw items from a single Category; they cannot directly represent a hierarchy that mixes items from multiple categories.
  - In such cases:
    - the mapping to DPM is not direct and is generally considered **out of scope** for strict interoperability;
    - the hierarchy should be handled via:
      - separate hierarchies per Category, and/or
      - external documentation.

## 4.5 Concept ↔ Property / Metric

### 4.5.1 DPM → SDMX

- **Metric → Concept used as measure**:
  - For each DPM Metric:
    - create an SDMX Concept in a dedicated Concept Scheme (e.g. “Metrics”),
    - set its representation according to the Metric’s data type,
    - use it as a measure in DSDs.

- **Property → Concept used as dimension/attribute**:
  - For each DPM Property:
    - create an SDMX Concept in a Concept Scheme (e.g. “Properties”),
    - set its representation:
      - enumerated (codelist) if linked to a Category/Subcategory, or
      - non-enumerated (facet-based) otherwise,
    - use it as a dimension or attribute in DSDs.

### 4.5.2 SDMX → DPM: decision rule

When generating DPM glossary entries from SDMX Concepts, use the following rule:

1. **Collect all uses of each Concept** across DSDs/Dataflows:
   - track whether the concept is used as:
     - Time dimension,
     - other Dimension,
     - Attribute,
     - Measure.

2. **If the Concept is used as a Measure** (or only as a measure dimension in multi-measure datasets):
   - map it to a **Metric** (`property_is_metric = true`),
   - attach the appropriate numeric data type.

3. **Otherwise**, map it to a **Property** (`property_is_metric = false`):
   - if the concept has an enumerated representation (codelist/extended codelist), link the Property to the corresponding Category/Subcategory;
   - if the concept has a primitive representation (integer, decimal, date, string, etc.), configure the Property with that data type.

4. **Concept Scheme handling**:
   - do not attempt to map Concept Schemes themselves;
   - use the Concept Scheme’s agency and ID to drive ownership and naming in the DPM glossary.

### 4.5.3 Enumerated vs non-enumerated concepts

- **Enumerated Concepts** (with codelist-based representations):
  - Map their codelists/extended codelists to Categories/Subcategories (as above).
  - Configure the Property/Metric to reference those Categories/Subcategories.

- **Non-enumerated Concepts**:
  - Map directly to Properties/Metrics with an appropriate non-enumerated data type (derived from SDMX facets).
  - Do not create Categories unless there is a specific reason to treat the values as a category.

