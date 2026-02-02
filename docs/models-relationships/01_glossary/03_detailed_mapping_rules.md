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

### **Example: SDMX ConcepSchema → DPM Glossary**

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

#### **Example Codelist**
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

An SDMX Code is a fundamental element within a Codelist in the SDMX Information Model.

### 4.3.1 Simple codes

- For each **Code** in an SDMX Codelist (or Extended Codelist that does not introduce additional semantics):
  - Create a **Category Item** in the corresponding Category.
  - Map:
    - SDMX `agencyID` (if present at code level) or codelist `agencyID` → Category Item owner.
    - Code `id` → Category Item code.
    - Code name and description → Category Item name and description.
  - Default flags (as in ECB Simplified Approach):
    - `is_default = false`,
    - `is_compound = false`,
    - `is_obsolete = false`.

### SDMX Code <-> DPM Item Mapping Details

| Attribute | Value |
|---|---|
| ItemID | (system-generated, e.g., 5001) |
| Code | {agencyID}.{ConceptSchemeId}.{CodelistId}.{CodeId} |
| Name | Code.Name |
| Description | Code.Description |
| IsActive | TRUE |
| IsExternalRefData | FALSE |
| RefDataSource | NULL |
| RowGUID | (system-generated UUID) |

### SDMX Code <-> DPM CategoryItem Mapping Details

| Attribute | Value |
|---|---|
| CategoryItemID | (system-generated, e.g., 9001) |
| CategoryID | Category.CategoryID |
| ItemID | Item.ItemID |
| IsActive | TRUE |
| RowGUID | (system-generated UUID) |

## SDMX Code <-> DPM Item Examples (from SDMX Codes in CL_COUNTRY)

## Item: Spain (ES)
| Attribute | Value |
|---|---|
| ItemID | (system-generated, e.g., 5001) |
| Code | ECB.CS_REPORTING.CL_COUNTRY.ES |
| Name | Spain |
| Description | NULL |
| IsActive | TRUE |
| IsExternalRefData | FALSE |
| RefDataSource | NULL |
| RowGUID | (system-generated UUID) |

## Item: France (FR)
| Attribute | Value |
|---|---|
| ItemID | (system-generated, e.g., 5002) |
| Code | ECB.CS_REPORTING.CL_COUNTRY.FR |
| Name | France |
| Description | NULL |
| IsActive | TRUE |
| IsExternalRefData | FALSE |
| RefDataSource | NULL |
| RowGUID | (system-generated UUID) |

## SDMX Code <-> DPM CategoryItem Examples (link Category ↔ Items)

> Links Category `ECB.CS_REPORTING.CL_COUNTRY` to each Item.

## Link: Category ↔ Spain (ES)
| Attribute | Value |
|---|---|
| CategoryItemID | (system-generated, e.g., 9001) |
| CategoryID | Category.CategoryID (e.g., 1001) |
| ItemID | Item.ItemID (e.g., 5001) |
| IsActive | TRUE |
| RowGUID | (system-generated UUID) |

## Link: Category ↔ France (FR)
| Attribute | Value |
|---|---|
| CategoryItemID | (system-generated, e.g., 9002) |
| CategoryID | Category.CategoryID (e.g., 1001) |
| ItemID | Item.ItemID (e.g., 5002) |
| IsActive | TRUE |
| RowGUID | (system-generated UUID) |

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

### 4.4.1 Subsets (constraints and partial codelists)

Here’s how you define a subset of codes in SDMX, with examples:

- **Option 1**: Partial Codelist using isPartial
If you want to publish a reduced version of a maintained Codelist:
Key points:
The Codelist keeps the same agencyID, id, and version as the full list.
Add isPartial="true" in the Codelist header.
Include only the codes you need.

- **Option 2**: Using a Constraint
For dynamic subsets or validation rules, use ContentConstraint or AttachmentConstraint.
Key points:
Define a CubeRegion for data or MetadataTargetRegion for metadata.
Use MemberSelection to include/exclude codes.
Support for cascadeValues and wildcard %.

#### 4.4.2 Mapping details
Partial Codelist → DPM SubCategory

The subset of codes is modeled as a SubCategory of that Category.
SubCategory groups selected Items (codes) and can be versioned via SubCategoryVersion (linked to a Release).
Versioning
DPM supports historization: SubCategoryVersion refers to a Release, similar to SDMX versioning.
This allows tracking changes over time (e.g., adding/removing codes).

- Each SubCategory groups Items- Each SubCategory groups Items from the Category `{agencyID}.{ConceptSchemeId}.{CodelistId}`.
- Use SubCategoryVersion for historization.


#### DPM SubCategory Mapping Details

| Attribute           | Value |
|---------------------|-------|
| SubCategoryIDsystem-generated, e.g., 7001) |
| Code                | EU_COUNTRIES |
| Name                | European Union Countries |
| Description         | Subset of EU member states within CL_COUNTRY |
| Owner               | ECB |
| IsActive            | TRUE |
| RowGUID             | (system-generated UUID) |

#### SubCategoryVersion
| Attribute           | Value |
|---------------------|-------|
| SubCategoryVID      | (system-generated, e.g., 7101) |
| SubCategoryID       | 7001 |
| StartReleaseID      | 3001 (e.g., Release "2025-Q1") |
| EndReleaseID        | NULL |
| RowGUID             | (system-generated UUID) |


#### DPM SubCategory Examples (Partial Codelist Mapping)

#### SubCategory: EU_COUNTRIES
| Attribute           | Value |
|---------------------|-------|
| SubCategoryID       | 7001 |
| Code                | EU_COUNTRIES |
| Name                | European Union Countries |
| Description         | Subset of EU member states within CL_COUNTRY |
| RowGUID             | (system-generated UUID) |

#### SubCategoryVersion
| Attribute           | Value |
|---------------------|-------|
| SubCategoryVID      | 7101 |
| SubCategoryID       | 7001 |
| StartReleaseID      | 3001 |
| EndReleaseID        | NULL |

#### SubCategoryItems (Members of EU_COUNTRIES)
| Attribute           | Value |
|---------------------|-------|
| SubCategoryVID      | 7101 |
| ItemID              | 5001 |
| Label               | France |
| ParentItemID        | NULL |
| RowGUID             | (system-generated UUID) |

| Attribute           | Value |
|---------------------|-------|
| SubCategoryVID      | 7101 |
| ItemID              | 5002 |
| Label               | Germany |
| ParentItemID        | NULL |
| RowGUID             | (system-generated UUID) |

| Attribute           | Value |
|---------------------|-------|
| SubCategoryVID      | 7101 |
| ItemID              | 5003 |
| Label               | Italy |
| ParentItemID        | NULL |
| RowGUID             | (system-generated UUID) |


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

### 4.5.2 DPM → SDMX
### SDMX Concept → DPM Property Mapping

This template maps **SDMX Concepts** (which can play the role of **dimension**, **attribute**, or **measure**) to **DPM Properties** (and shows how they are later used by Variables).

---

### Mapping details

| Attribute        | Value / Guidance |
|------------------|------------------|
| **PropertyID**   | (system-generated, e.g., 7001) |
| **Code**         | `{agencyID}.{ConceptSchemeId}.{ConceptId}` |
| **Name**         | `Concept.Name` |
| **Description**  | `Concept.Description` (multilingual as needed) |
| **IsMetric**     | `TRUE` if the SDMX Concept is a **measure**; otherwise `FALSE` |
| **DataType**     | Choose from DPM DataType set (e.g., `integer`, `decimal`, `string`, `date`, `boolean`, `enumeration`) |
| **PeriodType**   | `stock` (instant) or `flow` (duration); *only for quantitative metrics where relevant* |
| **IsComposite**  | `TRUE` if this Property represents a composite semantic (rare); otherwise `FALSE` |
| **RowGUID**      | (system-generated UUID) |

---

### Example A — SDMX **Dimension** Concept → DPM Property (+ Key Variable)

**SDMX**
- Concept ID: `COUNTRY`
- Role: **dimension**
- Representation: CodeList of countries (e.g., ISO 3166)

**DPM mapping**
- **Property**
  - `Code`: `EBA.CS_GEO.COUNTRY`
  - `Name`: `Country`
  - `Description`: `Reporting country`
  - `IsMetric`: `FALSE`
  - `DataType`: `enumeration`
  - (Optionally) `IsComposite`: `FALSE`
- **Category** (e.g., `Countries`), with **Items** like `IT`, `ES`, `FR`, …
- **Key Variable** (used when table is open by country)
  - References **Property** = `Country`
  - If needed, restrict selectable values with a **SubCategory** (e.g., `EU_Members`)


---

### Example B — SDMX **Attribute** Concept → DPM Property (+ Attribute Variable)

**SDMX**
- Concept ID: `OBS_STATUS`
- Role: **attribute** (e.g., A – provisional, F – forecast, E – estimated)
- Representation: CodeList of status codes

**DPM mapping**
- **Property**
  - `Code`: `EIOPA.CS_META.OBS_STATUS`
  - `Name`: `Observation status`
  - `Description`: `Quality/status flag of an observation`
  - `IsMetric`: `FALSE`
  - `DataType`: `enumeration`
- **Category** (e.g., `ObservationStatus`), with **Items** like `A`, `E`, `F`, …
- **Attribute Variable**
  - References **Property** = `Observation status`
  - Typically linked to **Fact Variables** that need the status annotation

---

### Example C — SDMX **Measure** Concept → DPM Property (+ Fact Variable)

**SDMX**
- Concept ID: `OBS_VALUE`
- Role: **measure** (e.g., monetary amount)
- Representation: numeric

**DPM mapping**
- **Property**
  - `Code`: `EBA.CS_MEASURE.OBS_VALUE`
  - `Name`: `Observed value`
  - `Description`: `Primary measure/observation value`
  - `IsMetric`: `TRUE`
  - `DataType`: `decimal` (or `integer` as appropriate)
  - `PeriodType`: `stock` (instant) **or** `flow` (duration), depending on the phenomenon
- **Fact Variable**
  - References **Property** = `Observed value`
  - May carry **Context** (e.g., Unit of measure, Currency) through additional Properties/Variables


### 4.5.2 DPM → SDMX

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


