# 2. Vocabulary overview

## 2.1 SDMX vocabulary artefacts

- **Codelist**  
  Enumerated list of codes for a concept (e.g. `FREQ`, `GEO`). Each codelist is owned by an agency (`agencyID`) and has an identifier (`id`).

- **Geospatial Codelist**  
  Specialised codelist for geospatial codes. Functionally behaves like a codelist, but carries additional geospatial semantics (e.g. linkage to geometries).

- **Extended Codelist**  
  A codelist that:
  - can restrict a base codelist to a subset of its codes, and/or
  - can extend a base codelist with additional codes that are not present in the base.

- **Code**  
  Individual value in a codelist (or extended codelist), identified by a code ID and label(s) (plus optional description).

- **Hierarchy**  
  Artefact used to define parent–child relationships over codes, including the possibility to mix codes from different codelists in a single hierarchy.

- **Concept Scheme**  
  Grouping of related concepts for a statistical domain. It is a container for concepts, but is not itself used directly in data structures.

- **Concept**  
  Semantic definition of a business characteristic that can be used as:
  - dimension,
  - attribute, or
  - measure
  in a Data Structure Definition (DSD). Concepts are associated with a representation (enumerated via codelists or non-enumerated via data types and facets).

## 2.2 DPM glossary artefacts

- **Category**
  - **Enumerated Category**: category with a finite list of Category Items (codes).
  - **Non-Enumerated Category**: category with no finite list of items, used with a data type (e.g. decimal, string) rather than a codelist. Conceptually similar to an SDMX concept with a non-enumerated representation.

- **Category Item**
  - **Simple Category Item**: basic item of an enumerated category, conceptually similar to an SDMX code.
  - **Compound Category Item**: a Category Item that encodes a composition of other items, e.g. a “Treasury bill” defined as:
    - Type of instrument = “Debt securities”,
    - Issuer Sector = “Central governments”,
    - Original maturity = “Up to 1 year”.

- **Subcategory**  
  Artefact that:
  - creates a subset of items from a Category; and / or
  - organises Category Items in a hierarchy (parent–child relationships).

- **Super Category**  
  Higher-level grouping mechanism across categories (e.g. grouping related categories or subcategories). In the SDMX mapping, Super Categories are strongly related to Extended Codelists.

- **Property**  
  Qualitative characteristic used to define variables. Properties may:
  - reference enumerated categories (categorical properties), or
  - be associated with non-enumerated types (e.g. free text, dates).

- **Metric**  
  Quantitative characteristic used for numerical values (e.g. GDP, population). Metrics are a specialised form of Property but distinguished explicitly in DPM.

In typical DPM 2.0 implementations (e.g. ECB CDM), these artefacts are consolidated into a **single cross-domain glossary**, whereas SDMX allows multiple concept schemes per domain.

