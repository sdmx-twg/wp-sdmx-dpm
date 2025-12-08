# Business Case: SDMX-DPM Interoperability Work Package

## 1. Executive Summary

This document outlines the business case for the **SDMX-DPM Interoperability Work Package**, an initiative proposed by the SDMX Technical Working Group (TWG). The primary goal is to establish and document a framework for interoperability between the **Statistical Data and Metadata eXchange (SDMX)** standard and the **Data Point Model (DPM)**.

By bridging the gap between these two dominant standards—SDMX in official statistics and DPM in financial supervision—this work package aims to reduce operational silos, eliminate redundant metadata management, and facilitate seamless data exchange across domains.

## 2. Background and Context

### 2.1. The Challenge: Divergent Standards
Currently, the statistical and supervisory domains operate in parallel but separate ecosystems:

- **SDMX (Statistical Data and Metadata eXchange)**: The global standard for exchanging statistical data, widely used by central banks and international organizations.
- **DPM (Data Point Model)**: A data-centric modeling framework primarily used in the European financial supervision context (e.g., EBA, EIOPA, ECB) and often implemented via XBRL.

While both frameworks share common concepts—such as dimensional structures, classifications, and reporting requirements—they have evolved independently. This divergence has led to:

- **Siloed Data**: Difficulty in integrating statistical and supervisory data, in the organisations that collect both type of data (e.g., EU Central Banks).
- **Duplication of Effort**: Reporting agents (e.g., banks) and institutions often maintain separate pipelines and metadata repositories for each standard, with no shared solution to map metadata concepts across repositories and significant effort required to keep multiple metadata repositories aligned and managed.
- **Interoperability Barriers**: Technical challenges in mapping metadata and data structures between systems.


### 2.2. The Mandate
In June 2025, the SDMX TWG reviewed the potential for interoperability between SDMX and DPM. The review concluded that significant synergies exist and that a formal effort to document and operationalize these links would benefit the entire community. This work package was established to execute on that vision.

## 3. Objectives

The core objective of this work package is to make SDMX-DPM interoperability a practical reality for technical and business stakeholders.

### 3.1. Strategic Objectives
*   **Promote Interoperability**: Demonstrate how SDMX and DPM can coexist and interact, enabling cross-domain data flows.
*   **Enhance Metadata Governance**: Advocate for unified glossary approaches where concepts are shared across reporting frameworks, reducing the need for parallel metadata maintenance.
*   **Support Integrated Reporting**: Align with broader industry trends like the Integrated Reporting Framework (IReF) by enabling metadata-driven approaches that span both statistical and prudential requirements.
* **Support Future Convergence**: Support a convergence path for next releases of both SDMX and DPM methodologies..

> **Example Use Case 1: The Central Bank with single metadata repository**

> Consider a central bank that currently maintains two separate metadata repositories for statistical and prudential data, and even separate metadata-driven reporting systems because of lack of common metadata. By adopting the SDMX-DPM interoperability framework, the bank can combine the two metadata repositories into a single one, and even combine the two reporting systems into a single one.

> **Example Use Case 2: The Unified Reporting Pipeline**

> Consider a commercial bank that currently maintains two separate reporting engines: one for statistical reports (SDMX) and another for prudential supervision (DPM/XBRL). By adopting the SDMX-DPM interoperability framework, the bank can map its internal data once to a unified model. From this single source, it can automatically generate valid reports for both domains, significantly reducing maintenance costs and the risk of data inconsistencies.

### 3.2. Stakeholder Benefits
The framework delivers targeted value across the ecosystem:

| Stakeholder | Key Benefits |
| :--- | :--- |
| **Regulators & Supervisors** | Guidance and tooling that promote better data consistency between statistical and prudential domains; enhanced transparency on data lineage; reduced data silos; potential cost reduction. |
| **Reporting Agents (Banks/Insurers)** | Reduced compliance burden through unified data mapping; lower cost of change for new requirements. |
| **Software Vendors** | Standardized implementation targets; opportunity to build "write once, report everywhere" solutions. |
| **Standard Setters** | Greater adoption through interoperability; reduced friction in standards maintenance. |

### 3.3. Deliverable Objectives
The work package is committed to producing tangible assets:

1.  **Business Case**: A formalized articulation of the value proposition (this document).
2.  **Model Relationship Documentation**: Detailed technical mapping of SDMX 3.0 components to DPM 2.0 elements (and vice versa).
3.  **Transformation Guidance**: Practical algorithms, examples and at least one sample conversion script that demonstrate how to convert metadata (as a prerequisite) and data between CSV-based formats (SDMX-CSV and XBRL-CSV).
4.  **Public Knowledge Base**: A standards interoperability website to serve as a permanent reference for the community, including guidance on mapping patterns, best practices and how versioning is applied across the SDMX and DPM information models and the associated mapping artefacts.

## 4. Risks & Mitigation

To ensure the success of this initiative, the following risks have been identified and addressed:

*   **Complexity of Mappings**: Mapping distinct modeling paradigms (e.g., DPM's rendering artifacts vs. SDMX's structural metadata) can be complex.
    *   *Mitigation*: The project adopts a phased approach, starting with core concepts before tackling edge cases, and will document explicit assumptions and recommended best practices (e.g., stability of concept data types) that enable robust mappings.
*   **Version Drift**: Standards evolve (e.g., SDMX 3.1, DPM Refit).
    *   *Mitigation*: The work package explicitly targets **SDMX 3.1** and **DPM Refit (2.0)**, with a clear versioning policy for the mapping artifacts.
*   **Adoption**: Technical outputs may not be widely adopted without clear guidance.
    *   *Mitigation*: A strong focus on "Transformation Guidance" and practical examples (CSV interoperability) to lower the barrier to entry.

## 5. Scope and Approach

### 5.1. Scope
The work package will focus on:

- **Conceptual Alignment**: Mapping of high-level concepts (SDMX Dimensions, Attributes and Measures to DPM Properties; SDMX code lists to DPM Categories and Category Items; SDMX code list hierarchies to DPM Supercategories and Subcategories).
- **Technical Mapping**: Defining precise transformation rules between **SDMX Information Model (v3.1)** and **DPM Metamodel (v2.0)**.
- **Data Formats**: Addressing interoperability at the data instance level, specifically between SDMX and XBRL-CSV.
- **Communication**: Translating technical findings into accessible content for a broad audience, and presenting the work in relevant SDMX and DPM standard-setting bodies, workshops and conferences.

### 5.2. Approach
The project follows a collaborative, phased approach:

- **Consolidation**: Leveraging existing expert knowledge and the June 2025 presentation as a baseline.
- **Development**: Drafting technical documents and validating them within the TWG and with DPM experts.
- **Publication**: Disseminating findings via a dedicated interoperability website to ensure accessibility and community engagement.

## 6. Conclusion

The SDMX-DPM Interoperability Work Package represents a strategic investment in the future of data exchange. By providing the "missing link" between these two major standards, the project will unlock operational efficiencies, improve data quality, and pave the way for a more integrated global data ecosystem.

To ensure long-term sustainability, the outputs of this work package (including the website and mapping documentation) will be handed over to the SDMX Technical Working Group (TWG) for ongoing maintenance and stewardship upon project completion.
