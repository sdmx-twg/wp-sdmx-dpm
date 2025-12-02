# 3. High-level mapping summary

The table below summarises the primary correspondences; the detailed rules and edge cases are covered in subsequent chapters.

| SDMX artefact | DPM artefact | Notes |
| --- | --- | --- |
| Codelist | Category (enumerated) | Basic one-to-one mapping (per codelist). Codelist without Codes can be treated similar to Non-Enumerated Category. |
| Geospatial Codelist | Category (enumerated) + external semantics | Model as a normal Category; geospatial semantics handled by convention or external metadata. |
| Extended Codelist (subset only) | Subcategory | Extended Codelist that only restricts an existing codelist maps to a Subcategory over the corresponding Category. |
| Extended Codelist (with extra codes) | Subcategory + additional Category/CategoryItems (workaround) | Base subset → Subcategory; additional codes require explicit modelling in DPM. |
| Code | Category Item (Simple) | One-to-one mapping including code, label, description and agency. |
| Compound Code structure | Category Item (Compound) | DPM captures composition links; mapping back to SDMX loses composition, retaining only a Code. |
| Hierarchy (single codelist) | Subcategory hierarchy | Hierarchical codes become parent–child relationships between Subcategory items. |
| Hierarchy (mixed codelists) | – (no direct equivalent) | Cannot be represented as a single Subcategory; must be simplified or documented externally. |
| Concept (qualitative) | Property | Enumerated or non-enumerated based on representation; `property_is_metric = false`. |
| Concept (quantitative) | Metric | Concept used as a measure; `property_is_metric = true`. |
| Concept Scheme | – | No direct DPM equivalent; its identity drives ownership and IDs for Properties/Metrics. |

