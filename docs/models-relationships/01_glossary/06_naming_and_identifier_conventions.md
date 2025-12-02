# 6. Naming and identifier conventions

- **ID preservation**
  - Preserve SDMX IDs for Concepts, Codelists and Codes wherever feasible to ease traceability.
  - Avoid case changes that could lead to confusing differences (`GEO` vs `geo`). All three standards (SDMX, DPM, XBRL) are effectively case-sensitive.

- **Prefixes and suffixes**
  - In Simplified Approach implementations, some fields may split IDs into prefix/postfix (e.g. to encode ownership or domain).
  - For Subcategory items, it is common to prefix item codes with the agency and category IDs to ensure uniqueness.

- **Extended Codelist extra codes**
  - Codes that exist only in Extended Codelists must be given explicit treatment in DPM (new CategoryItems and documentation) and should be clearly marked as extensions.

