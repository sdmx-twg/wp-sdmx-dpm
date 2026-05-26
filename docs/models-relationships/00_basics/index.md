# Basics

This section provides foundational material for understanding the SDMX-DPM interoperability work. Before diving into detailed artefact mappings, it is essential to understand the fundamental differences between the two standards and familiarize yourself with the terminology used throughout this documentation.

Versioning is treated here as a **foundational, horizontal topic** rather than a late specialised chapter: because the way each model versions and releases its artefacts underpins almost every mapping rule, the conceptual overview lives in this section and is cross-referenced throughout.

## Purpose

The Basics section serves as a prerequisite for the detailed mapping chapters that follow. It establishes:

- **Design philosophies**: Recognizing the distinction between exchange-oriented (SDMX) and repository-oriented (DPM) frameworks.
- **Conceptual foundations**: Understanding how SDMX and DPM approach metadata modelling from different architectural perspectives.
- **Common vocabulary**: Ensuring consistent use and understanding of technical terms across both standards.

## Contents

### [Base Comparison](01_base_comparison.md)

A comprehensive comparison of SDMX and DPM covering their fundamental architectural differences:

- **Architectural approaches**: The DPM meta-model for physical database implementation versus the SDMX Information Model for conceptual exchange.
- **Conceptual foundations**: How DPM uses Concepts as primary building blocks versus SDMX's abstract class hierarchy.
- **Data access models**: SDMX's distributed API-based approach versus DPM's shared repository model.
- **Object identification**: Database-centric keys with IDPrefix (DPM) versus URN-based global identifiers (SDMX).
- **Ownership models**: Flat organizational ownership in DPM versus hierarchical maintenance agencies in SDMX.

This chapter is essential reading for anyone seeking to understand why certain mapping decisions are made and where information loss or approximation may occur.

### [Glossary and Abbreviations](../glossary_and_abbreviations.md)

A comprehensive reference of technical terms, concepts, and abbreviations used throughout the documentation:

- **Glossary of terms**: Alphabetically organized definitions covering SDMX-specific terms (Codelist, Concept, DSD, Hierarchy), DPM-specific terms (Category, Property, Metric, SubCategory), and shared architectural concepts.
- **Abbreviations and acronyms**: Organized by category, including standards and organizations (SDMX, DPM, EBA, EIOPA), technical formats (API, REST, JSON, XML, URN), and data components (DSD, CL_, OBS, REF).
- **Usage notes**: Guidance on terms with different meanings across standards, naming conventions, and common confusions.

This chapter serves as a quick reference while reading the detailed mapping chapters and helps clarify terminology that may be ambiguous across the two standards.

### [Versioning Overview](03_versioning_overview.md)

A foundational primer on how the two models version and release their artefacts — the horizontal topic that shapes the rest of the documentation:

- **SDMX versioning**: semantic `major.minor.patch` versioning, backward-compatible vs breaking changes, fixed vs flexible version references, with a worked country/currency code-list example.
- **DPM versioning**: structural versioning of Modules/Tables vs release-based change logs for the glossary, and why everything resolves through a ModuleVersion.
- **Releases as snapshots**: DPM Releases as publication packages of the whole repository, related to but distinct from SDMX artefact versions.

The detailed, artefact-level versioning *mapping rules* remain later, in [Versioning and Extensibility](../04_versioning_and_extensibility/index.md).

## How to Use This Section

1. **First-time readers**: Start with the [Base Comparison](01_base_comparison.md) to understand the fundamental differences between SDMX and DPM. This will provide essential context for all subsequent chapters.

2. **Reference lookup**: Use the [Glossary and Abbreviations](../glossary_and_abbreviations.md) whenever you encounter unfamiliar terms or need clarification on how a term is used in each standard.

3. **Versioning context**: Read the [Versioning Overview](03_versioning_overview.md) early — many later mapping rules only make sense once you understand how SDMX versions and DPM releases differ.

4. **Before detailed mappings**: Complete this section before proceeding to the [Glossary](../01_glossary/index.md), [Data Definition](../02_data_definition/index.md), or other mapping chapters. The foundational knowledge here is assumed in those sections.

## Prerequisites

This documentation assumes:

- Basic familiarity with metadata modelling concepts (schemes, items, hierarchies, data structures).
- Understanding of either SDMX or DPM (not necessarily both).
- Comfort with technical documentation and conceptual diagrams.

No prior knowledge of the detailed SDMX Information Model or DPM metamodel specifications is required—those details are explained as needed throughout the documentation.

## Next Steps

After completing this section, proceed to:

- **[Versioning Overview](03_versioning_overview.md)**: How SDMX and DPM version and release artefacts — foundational context for every later chapter.
- **[Glossary](../01_glossary/index.md)**: Detailed mappings of glossary artefacts (concepts, codelists, categories, hierarchies).
- **[Data Definition](../02_data_definition/index.md)**: Mappings of data structures (DSDs, Dataflows, Report Tables, Variables, ReportingTaxonomy ↔ Module/ModuleVersion).
