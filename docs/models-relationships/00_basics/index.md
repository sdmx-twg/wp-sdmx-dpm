# Basics

This section provides foundational material for understanding the SDMX-DPM interoperability work. Before diving into detailed artefact mappings, it is essential to understand the fundamental differences between the two standards and familiarize yourself with the terminology used throughout this documentation.

## Purpose

The Basics section serves as a prerequisite for the detailed mapping chapters that follow. It establishes:

- **Conceptual foundations**: Understanding how SDMX and DPM approach metadata modelling from different architectural perspectives.
- **Design philosophies**: Recognizing the distinction between exchange-oriented (SDMX) and repository-oriented (DPM) frameworks.
- **Common vocabulary**: Ensuring consistent use and understanding of technical terms across both standards.

## Contents

### [Base Comparison](base_comparison.md)

A comprehensive comparison of SDMX and DPM covering their fundamental architectural differences:

- **Conceptual foundations**: How DPM uses Concepts as primary building blocks versus SDMX's abstract class hierarchy.
- **Architectural approaches**: The DPM meta-model for physical database implementation versus the SDMX Information Model for conceptual exchange.
- **Data access models**: SDMX's distributed API-based approach versus DPM's shared repository model.
- **Object identification**: Database-centric keys with IDPrefix (DPM) versus URN-based global identifiers (SDMX).
- **Ownership models**: Flat organizational ownership in DPM versus hierarchical maintenance agencies in SDMX.

This chapter is essential reading for anyone seeking to understand why certain mapping decisions are made and where information loss or approximation may occur.

### [Glossary and Abbreviations](glossary_and_abbreviations.md)

A comprehensive reference of technical terms, concepts, and abbreviations used throughout the documentation:

- **Glossary of terms**: Alphabetically organized definitions covering SDMX-specific terms (Codelist, Concept, DSD, Hierarchy), DPM-specific terms (Category, Property, Metric, SubCategory), and shared architectural concepts.
- **Abbreviations and acronyms**: Organized by category, including standards and organizations (SDMX, DPM, EBA, EIOPA), technical formats (API, REST, JSON, XML, URN), and data components (DSD, CL_, OBS, REF).
- **Usage notes**: Guidance on terms with different meanings across standards, naming conventions, and common confusions.

This chapter serves as a quick reference while reading the detailed mapping chapters and helps clarify terminology that may be ambiguous across the two standards.

## How to Use This Section

1. **First-time readers**: Start with the [Base Comparison](base_comparison.md) to understand the fundamental differences between SDMX and DPM. This will provide essential context for all subsequent chapters.

2. **Reference lookup**: Use the [Glossary and Abbreviations](glossary_and_abbreviations.md) whenever you encounter unfamiliar terms or need clarification on how a term is used in each standard.

3. **Before detailed mappings**: Complete this section before proceeding to the [Glossary](../01_glossary/index.md), [Data Definition](../02_data_definition/index.md), or other mapping chapters. The foundational knowledge here is assumed in those sections.

## Prerequisites

This documentation assumes:

- Basic familiarity with metadata modelling concepts (schemes, items, hierarchies, data structures).
- Understanding of either SDMX or DPM (not necessarily both).
- Comfort with technical documentation and conceptual diagrams.

No prior knowledge of the detailed SDMX Information Model or DPM metamodel specifications is required—those details are explained as needed throughout the documentation.

## Next Steps

After completing this section, proceed to:

- **[Glossary](../01_glossary/index.md)**: Detailed mappings of glossary artefacts (concepts, codelists, categories, hierarchies).
- **[Data Definition](../02_data_definition/index.md)**: Mappings of data structures (DSDs, Dataflows, Report Tables, Variables).
- **[Other Artifacts](../03_other_artifacts/index.md)**: Additional constructs including reporting taxonomies, modules, and rendering artefacts.
