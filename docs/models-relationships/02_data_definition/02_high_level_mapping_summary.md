# 2. High-level mapping summary

This chapter gives a compact view of how the SDMX and DPM data definition artefacts relate to each other. It complements the detailed descriptions in sections 2.1 and 2.2 and the rule-based mappings in the next chapter.

## 2.1 Tabular mapping

The table below summarises the main correspondences at data definition level. It is intentionally high level; edge cases and technical details are covered later.

| SDMX data definition artefact | DPM data definition artefact | Mapping notes |
| --- | --- | --- |
| DataStructureDefinition (DSD) | Module | Both define the structural metadata for a reporting domain. A DSD specifies components; a Module is the structural container — it is **ModuleVersion** that groups the concrete Variables, Tables, and Operations. |
| Dataflow | ModuleVersion | Both represent structure usage in a specific context. A Dataflow applies a DSD; a ModuleVersion is a deployable version of a Module with concrete artefacts. |
| Dataflow + DSD (convention) | Table | One SDMX Dataflow plus its DSD can correspond to one DPM Table. This is a practical convention, not a strict equivalence. |
| Dimension | KeyVariable | SDMX Dimensions identify observations; DPM KeyVariables serve the same role. For enumerated Properties the allowed values come from the Category; for non-enumerated Properties the Property's DataType (e.g. Date, String) constrains the values directly. |
| TimeDimension | KeyVariable with time-related Property | SDMX has a dedicated TimeDimension type; DPM uses a regular KeyVariable referencing a time-related Property (e.g. `REFERENCE_PERIOD`) whose DataType carries the time semantics. |
| Measure | FactVariable | Both represent the observed/measured value. SDMX Measures have cardinality controls; DPM FactVariable data types are determined by the referenced Property's DataType. |
| DataAttribute | AttributeVariable | Both provide metadata about observations. In DPM, the link from a FactVariable or KeyVariable to its AttributeVariable is modelled via a **ConceptRelation** of type `variable_attribute` (source = FactVariable/KeyVariable, target = AttributeVariable). |
| AttributeRelationship | (implicit in Variable scope) | SDMX explicitly defines attachment levels (dataset, dimension, group, observation, measure). In DPM the attachment is modelled via ConceptRelation type `variable_attribute` but the attachment level is not formally specified. |
| GroupDimensionDescriptor | – | SDMX partial-key groups have no direct DPM equivalent. Similar semantics may be achieved via Variable scoping or Operations. |
| DataConstraint / CubeRegion | SubCategory (on Dimensions) | SDMX constraints restrict allowable values; DPM uses SubCategories to define allowed Items for a Dimension's Property. |
| Series / Observation | Variable instance (data point) | An SDMX series key maps to a DPM Variable's dimensional signature; observations map to reported values for that Variable. |
| – | Table / TableVersion | DPM Tables define visual/logical rendering; SDMX has no equivalent (presentation is outside the information model). |
| – | Header / Cell | DPM Headers define table axis positions (with glossary-term links); Cells are their intersections resulting in Variables. No SDMX counterpart. |
| – | FilingIndicatorVariable | DPM-specific artefact indicating whether a table should be reported; no direct SDMX equivalent. |
| – | Framework | DPM top-level container binding a set of Modules to a legislative/regulatory domain. SDMX has no equivalent; ProvisionAgreements (a common first guess) serve a different purpose — they model data-supply contracts, not regulatory groupings. |
| – | Release | DPM publication milestone (code, date, isCurrent) that bundles ModuleVersions. SDMX uses versioning and validity periods but has no dedicated release artefact that ties multiple structures to a reporting period. |

## 2.2 Graphical mapping overview

The diagram below shows the main data definition artefacts on each side and their high-level correspondences.

```mermaid
flowchart LR
  subgraph SDMX
    sDSD["DataStructureDefinition"]
    sDataflow["Dataflow"]
    sDim["Dimension"]
    sTimeDim["TimeDimension"]
    sMeasure["Measure"]
    sAttr["DataAttribute"]
    sGroup["GroupDimensionDescriptor"]
    sConstraint["DataConstraint"]
  end

  subgraph DPM
    dModule["Module / ModuleVersion"]
    dTable["Table / TableVersion"]
    dKeyVar["KeyVariable"]
    dFactVar["FactVariable"]
    dAttrVar["AttributeVariable"]
    dSubCat["SubCategory (constraints)"]
    dFiling["FilingIndicatorVariable"]
  end

  sDSD --- dModule
  sDataflow --- dModule
  sDim --- dKeyVar
  sTimeDim --- dKeyVar
  sMeasure --- dFactVar
  sAttr --- dAttrVar
  sConstraint --- dSubCat
```

The lines indicate "primary" correspondences used throughout this document; they do not exclude alternative modelling choices in specific implementations.

## 2.3 Artefacts without a direct counterpart

Not all data definition artefacts have a clean one-to-one mapping. This section highlights the main "asymmetric" cases so that readers are aware of where modelling choices or simplifications are needed.

### 2.3.1 SDMX-only (at data definition level)

- **TimeDimension**
  SDMX has a dedicated component type for time with specific FacetValueTypes (`observationalTimePeriod`, `reportingTimePeriod`, etc.). DPM uses a regular Dimension referencing a time-related Property; the time semantics are implicit in the Property definition rather than enforced by a special component type.

- **GroupDimensionDescriptor**
  SDMX Groups define partial keys for attaching attributes at intermediate levels (e.g. all observations for a country regardless of time). DPM has no direct equivalent; similar requirements are handled through Variable scoping, Operations, or by defining separate AttributeVariables.

- **AttributeRelationship (explicit attachment levels)**
  SDMX explicitly models where attributes attach (dataset, dimension, group, observation, measure). DPM attachment is implicit: an AttributeVariable references its subject Variable, but the "level" is not formally specified in the same way.

- **CategoryScheme / Categorisation**
  SDMX CategorySchemes organise subject domains and Categorisations link Categories to structural artefacts such as Dataflows. DPM achieves similar grouping via Frameworks and Modules, but has no direct counterpart to the Categorisation mechanism that explicitly links a subject-domain category to a data exchange definition.

- **DataConstraint with DataKeySet**
  SDMX DataKeySet enumerates explicit key combinations (specific series). DPM constraints operate at the value-domain level (SubCategories) rather than at the key-combination level; enumerating specific variable instances requires different mechanisms.

### 2.3.2 DPM-only (at data definition level)

- **Table / TableVersion / Header / Cell**
  DPM has a complete rendering layer defining how data collection forms are visually structured. SDMX intentionally excludes presentation concerns from the information model; table layouts are left to implementations or external specifications.

- **FilingIndicatorVariable**
  DPM-specific artefact that indicates whether a table (or parts of it) should be reported. Supports `isOpenTable` for extensible reporting scope. SDMX has no equivalent; similar semantics might be conveyed through constraints or provision agreements but without a dedicated artefact.

- **Open table / Closed table patterns**
  DPM explicitly supports different table patterns (closed, open, SDMX-like) with distinct cell types and rendering rules. SDMX does not model table patterns; the concept of "open" vs "closed" cells is specific to DPM's rendering layer.

- **Framework**
  DPM Frameworks bind a set of Modules to a legislative or regulatory domain (e.g. a specific regulation or directive). SDMX has no equivalent; ProvisionAgreements (a common first guess) are not analogous — they model data-supply contracts between providers and dataflows, not legislative groupings of structures.

- **Release**
  DPM publication milestones that bundle ModuleVersions with a code, date, and `isCurrent` flag. SDMX uses version validity periods (`validFrom`/`validTo`) but has no dedicated release artefact that ties multiple structures to a single reporting period.

These asymmetries are important when designing transformations between the two models. Later chapters discuss how to handle these cases in practice.
