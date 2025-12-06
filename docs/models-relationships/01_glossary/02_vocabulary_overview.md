# 2. Vocabulary overview

## 2.1 SDMX vocabulary artefacts

- **Codelist**  
  Enumerated list of codes for a concept (e.g. `FREQ`, `GEO`). Each codelist is owned by an agency (`agencyID`) and has an identifier (`id`).
  - *Example*: a codelist `CL_AREA_ISO` containing ISO country codes (`ES`, `FR`, `DE`, …) and another codelist `CL_AREA_NUTS` containing EU NUTS region codes (`ES300`, `ES302`, …). Both can be used to represent geographical areas in different levels of detail.

- **Geospatial Codelist**  
  Specialised codelist for geospatial codes. Functionally behaves like a codelist, but carries additional geospatial semantics (e.g. linkage to geometries).

- **Extended Codelist**  
  A codelist that:
  - can restrict a base codelist to a subset of its codes, and/or
  - can extend a base codelist with additional codes that are not present in the base.
  - *Example*: an extended codelist `CL_GEO_AREA` that combines `CL_AREA_ISO` (countries) and `CL_AREA_NUTS` (regions) so that a single representation can be used for the concept “Geographical area” while reusing existing code sets.

- **Code**  
  Individual value in a codelist (or extended codelist), identified by a code ID and label(s) (plus optional description).
  - *Example*: code `ES` labelled “Spain” in `CL_AREA_ISO`, and code `ES300` labelled “Madrid” in `CL_AREA_NUTS`. Both can appear in the extended codelist `CL_GEO_AREA`.

- **Hierarchy**  
  Artefact used to define parent–child relationships over codes, including the possibility to mix codes from different codelists in a single hierarchy.
  - *Example*: a “Geographical hierarchy” where a parent node `EU` groups all EU country codes (`ES`, `FR`, …) and where NUTS codes (e.g. `ES300`) are children of their corresponding country. The hierarchy can reference codes from both `CL_AREA_ISO` and `CL_AREA_NUTS`.

- **Concept Scheme**  
  Grouping of related concepts for a statistical domain. It is a container for concepts, but is not itself used directly in data structures.

- **Concept**  
  Semantic definition of a business characteristic that can be used as:
  - dimension,
  - attribute, or
  - measure
  in a Data Structure Definition (DSD). Concepts are associated with a representation (enumerated via codelists or non-enumerated via data types and facets).
  - *Examples*:
    - `RESIDENCE` and `BIRTH_LOC` concepts with an enumerated representation using `CL_GEO_AREA` (extended codelist over ISO countries and NUTS regions).
    - `NBIRTHS` (Number of births) concept with a non-enumerated integer representation (e.g. constrained to non‑negative values).
    - `FAIR_VAL` (Fair value) concept with a decimal representation (e.g. currency amounts, possibly constrained by scale or range facets).

## 2.2 DPM glossary artefacts

- **Category**
  - **Enumerated Category**: category with a finite list of Category Items (codes).
  - **Non-Enumerated Category**: category with no finite list of items, used with a data type (e.g. decimal, string) rather than a codelist. Conceptually similar to an SDMX concept with a non-enumerated representation.
  - *Examples*:
    - Enumerated Categories: `COUNTRY` containing ISO country Items (`ES`, `FR`, `DE`, …) and `NUTS_REGION` containing EU NUTS Items (`ES300`, `ES302`, …).
    - Non-enumerated Categories: an “Instrument identifier” Category where values are ISINs or LEIs that are not individually listed as Items.

- **Category Item**
  - **Simple Category Item**: basic item of an enumerated category, conceptually similar to an SDMX code.
  - **Compound Category Item**: a Category Item that encodes a composition of other items, e.g. a “Treasury bill” defined as:
    - Type of instrument = “Debt security”,
    - Sector of the issuer = “General governments”,
    - Original maturity = “Up to 18 months”.

- **Subcategory**  
  Artefact that:
  - creates a subset of items from a Category; and / or
  - organises Category Items in a hierarchy (parent–child relationships).
  - *Examples*:
    - A Subcategory “EU Member States” over the `COUNTRY` Category, listing only EU countries for a particular regulation.
    - A hierarchical Subcategory over `NUTS_REGION` where NUTS-0 country items are parents of NUTS-1/NUTS-2/NUTS-3 region items.

- **Super Category**  
  Higher-level grouping mechanism across categories (e.g. grouping related categories or subcategories). In the SDMX mapping, Super Categories are strongly related to Extended Codelists.
  - *Example*: a Super Category `GEO_AREA` that composes the `COUNTRY` and `NUTS_REGION` Categories so that both ISO country Items and NUTS region Items can be used as a single “Geographical area” value domain.

- **Property**  
  Qualitative characteristic used to define variables. Properties may:
  - reference enumerated categories (categorical properties), or
  - be associated with non-enumerated types (e.g. free text, dates).
  - *Examples*:
    - Qualitative Properties `RESIDENCE` and `BIRTH_LOC` referring to the `GEO_AREA` Super Category, so that both countries and regions can be used as values.
    - A qualitative Property “Type of financial instrument” referring to an “Instrument type” Category that includes Items like “Debt security”.

- **Metric**  
  Quantitative characteristic used for numerical values (e.g. GDP, population). Metrics are a specialised form of Property but distinguished explicitly in DPM.
  - *Examples*:
    - Metric `NBIRTHS` (Number of births) with an integer data type and, typically, a non‑negative constraint.
    - Metric `FAIR_VAL` (Fair value) with a decimal data type, representing monetary amounts (e.g. in EUR).

In typical DPM 2.0 implementations (e.g. ECB CDM), these artefacts are consolidated into a **single cross-domain glossary**, whereas SDMX allows multiple concept schemes per domain.
