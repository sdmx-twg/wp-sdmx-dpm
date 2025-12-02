# 5. Generating the DPM glossary from SDMX

This chapter distils the ECB “Mapping SDMX 3.* to DPM 2.0” and “Simplified Approach” guidance for **Step 1 – Glossary item creation**.

## 5.1 Inputs and assumptions

- SDMX 3.* Dataflows and/or DSDs with:
  - Concept Schemes,
  - Codelists (including Extended Codelists and Hierarchies),
  - Content Constraints.
- DPM 2.0 database with:
  - Organisations,
  - Glossary structures (Category, CategoryItem, Subcategory, Property, Metric, etc.).
- Simplified Approach Excel templates for:
  - Glossary items (Organisation, Category, CategoryItem, SubCategory, Property),
  - Data models (Framework, Module, Attributes, Associations) – used in the next phase.

## 5.2 Step-by-step process

1. **Select SDMX starting point**  
   Choose a Dataflow as the preferred entry point. If no Dataflow exists, use the DSD directly.

2. **Retrieve all referenced artefacts**  
   From the Dataflow/DSD, follow references to:
   - Concept Schemes and Concepts,
   - Codelists and Extended Codelists,
   - Hierarchies,
   - Content Constraints (cube region constraints).

3. **Determine organisations**  
   For each SDMX agency (`agencyID`) appearing in Concept Schemes or Codelists:
   - ensure there is a corresponding DPM Organisation:
     - organisation acronym from `agencyID`,
     - name retrieved from the SDMX registry or known context.

4. **Create Properties and Metrics**  
   For each Concept used in the DSD/Dataflow:
   - apply the decision rule from chapter 4 (Concept ↔ Property / Metric) to determine whether it becomes a Property or Metric;
   - derive data type from the concept’s representation (enumeration vs primitive type and facets);
   - populate default flags as per ECB convention:
     - `is_active = true`,
     - `is_composite = false`,
     - `period_type` left empty unless a specific convention is defined.

5. **Create Categories and Category Items**  
   For each Codelist:
   - create a Category with:
     - owner from `agencyID`,
     - code and name from codelist `id` and label,
     - `is_enumerated = true`, `is_obsolete = false`.
   - for each Code:
     - create a CategoryItem with:
       - `Owned by` from code/agency,
       - `Code`, `Name`, `Description` from the SDMX code,
       - default flags `is_default = false`, `is_compound = false`, `is_obsolete = false`.

6. **Create Subcategories from subsets and hierarchies**  
   - For each codelist:
     - create at least one Subcategory representing the complete list (if needed by the implementation).
   - Use:
     - **Content Constraints** to derive Subcategories representing allowed subsets for a Dataflow/DSD; and
     - **Hierarchies** (single-codelist) to derive Subcategories with parent–child relationships.

7. **Populate Simplified Approach glossary sheets**  
   - Fill the Excel template tables for:
     - `Organisation`,
     - `Category`,
     - `CategoryItem`,
     - `SubCategory`,
     - `Property`.

8. **Validate against existing DPM metadata**  
   - Check for duplicates and inconsistencies in:
     - Organisations,
     - Categories,
     - Properties/Metrics.
   - Flag conflicts (e.g. same ID but different data type or semantics) for manual resolution.

9. **Upload glossary into DPM 2.0**  
   - Import the Simplified Approach glossary file into the DPM 2.0 database via the metadata management tools.
   - Record any manual adjustments (e.g. code renames, ownership changes) for reproducibility.

