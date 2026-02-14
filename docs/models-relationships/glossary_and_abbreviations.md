# Glossary and Abbreviations

This chapter provides definitions of key terms, concepts, and abbreviations used throughout the SDMX-DPM mapping documentation. Terms that have different meanings in SDMX and DPM contexts are explicitly noted.

## Glossary of Terms

### A

**Agency ID**
Component of an SDMX URN identifying the maintaining organization. The Agency ID is a mandatory part of the identity triplet (Agency + ID + Version) for maintainable artefacts.

**Annotation**
Additional metadata or comments attached to artefacts, providing supplementary information beyond the core structural definitions.

**Artefact**
A structured object or component within SDMX or DPM metadata, such as a Codelist, Concept, Dataflow, Category, or Data Structure Definition.

**Attribute**
A component that provides contextual or quality metadata about observations. In SDMX, Attributes are defined in DSDs. In DPM, Attribute Variables serve a similar role.

**Attribute Variable**
DPM variable type corresponding to SDMX Attributes, providing contextual or quality information about observations.

### C

**Cartesian Product**
Mathematical concept describing all possible combinations of dimension values. In data structures, it represents the complete multi-dimensional space defined by all dimensions.

**Categorisation**
SDMX mechanism linking Categories to structural artefacts such as Dataflows, enabling subject-domain organization and navigation.

**Category** (SDMX)
Item within a CategoryScheme that labels a grouping or subject domain. Categories can be hierarchical (single-parent) and are used to organize structural artefacts.

**Category** (DPM)
Value-domain container for related items in DPM. Can be:
- **Enumerated** (`IsEnumerated = TRUE`): possible values are explicitly listed as Items.
- **Non-enumerated** (`IsEnumerated = FALSE`): possible values are not individually listed (e.g. instrument identifiers, highly volatile lists).

**CategoryScheme**
SDMX scheme for organizing Categories into subject domains or reporting taxonomies. Categories within a scheme can be nested to build hierarchical taxonomies.

**Change Logging**
Audit trail of modifications to entities over time, enabling tracking of when and by whom changes were made.

**Code**
Individual value within a Codelist (SDMX). Codes have an ID, name, description, and can be organized hierarchically within the Codelist.

**Codelist**
SDMX enumerated value domain containing Codes. Codelists are maintainable, versioned, can be partial, and support single-parent code hierarchies.

**Compound Item**
DPM Item whose meaning is composed of multiple Property–Item pairs. For example, "Treasury bill" might be composed of instrument type, issuer sector, and maturity. SDMX has no direct equivalent; similar semantics must be modelled using multiple dimensions.

**Concept**
SDMX semantic definition of a business characteristic that can serve as a dimension, attribute, or measure in a DSD. Each Concept has a core representation (enumerated or non-enumerated).

**Concept** (DPM usage)
In DPM architectural context, "Concept" refers to identifiable objects within the model (Category, Item, Variable, Property) that are assigned a Code and Name by a modeller.

**ConceptScheme**
SDMX container that groups related Concepts for a domain. It is maintainable and versioned like other schemes. DPM does not have an explicit ConceptScheme; instead, Properties and Metrics exist in a cross-domain glossary.

**Constraint**
Rules restricting valid value combinations or specifying attachment points for metadata. SDMX defines ContentConstraint (for data) and AttachmentConstraint (for metadata).

**ContentConstraint**
SDMX constraint defining valid data observations, often expressed as CubeRegions with MemberSelections.

### D

**Data Structure Definition (DSD)**
SDMX artefact defining the structure of data through dimensions, attributes, and measures. Corresponds roughly to a DPM Report Table's structure.

**Dataflow**
SDMX construct defining a flow of data with its associated DSD. Represents a specific reporting stream or data publication. Corresponds to a combination of DPM Report Table and its context.

**DataType**
Predefined value type specification. In DPM, DataTypes include integer, decimal, boolean, date, text, and Enumeration. In SDMX, data types are specified through Representations and Facets. Note that boolean fields in the EBA DPM database use `-1` for *true* and `0` for *false* (MS Access convention) — see [Physical database conventions](00_basics/02_detailed_mapping_rules.md#25-physical-database-conventions).

**Default**
Implicit value assumed when not explicitly stated. In DPM, a Category can designate one Item as its default, which is implicitly assumed for a Property of that Category when no explicit Item is specified.

**Dimension**
Component that identifies or disaggregates observations. In SDMX, Dimensions are defined in DSDs. In DPM, Key Variables serve a similar role.

**Direct Access**
Data retrieval approach where users query data directly from a shared repository (DPM approach), typically via SQL or application interfaces.

**Dissemination**
Distribution of data through standardized APIs, enabling consumers to discover and retrieve data (SDMX primary use case).

### E

**Entity-Relationship Diagram**
Visual representation of database structure showing entities, attributes, and relationships. Used in DPM to express the meta-model for physical database implementation.

**Enumerated Representation**
Values specified through a Codelist, ValueList, or GeoCodelist. Contrasts with non-enumerated representations defined by data type and facets.

**Exchange**
Standardized transfer of data and metadata across systems, a core design goal of SDMX.

**Extended Codelist**
SDMX mechanism to restrict, extend, or combine base Codelists. Extension order matters when resolving code conflicts. Extended Codelists can correspond to DPM SubCategories (when restricting) or Super Categories (when combining).

**Extensible**
Capability to add new items or properties while maintaining backward compatibility with existing implementations.

### F

**Facet**
Constraint on non-enumerated representations in SDMX, specifying rules such as minimum/maximum values, patterns, length restrictions, precision, or scale.

**FacetValueType**
SDMX type defining the nature of facet constraints (e.g. numeric range, string pattern, date range).

**Fact Variable**
DPM variable type corresponding to SDMX Measures, representing the observed or reported value.

**Framework**
DPM organizational container for logical grouping of report structures (Modules and Tables). Frameworks define ownership that is inherited by contained Modules.

### G

**GeoCodelist**
SDMX Codelist specialized for geospatial identifiers, with codes that can reference geometries (e.g. geographic features, coordinate grids).

**Globally Unique Identifier**
Identifier ensuring uniqueness across systems and organizations. SDMX uses URNs; DPM uses RowGUIDs.

**GUID (Globally Unique Identifier)**
UUID assigned to each entity in DPM for change logging and synchronization across databases.

### H

**Hierarchy**
SDMX maintained artefact defining parent–child relationships among codes, possibly across multiple Codelists and with multiple parents. Richer than single-parent trees inside a Codelist.

**HierarchicalCode**
Code node within an SDMX Hierarchy that references codes rather than duplicating them, enabling cross-Codelist hierarchies.

**HierarchyAssociation**
SDMX artefact applying a Hierarchy within a specific context (e.g. a Dataflow), allowing different contexts to reuse or tailor the same hierarchical structure.

### I

**IdentifiableArtefact**
Base SDMX abstract class providing basic identity through an ID. Foundation for NameableArtefact and MaintainableArtefact.

**IDPrefix**
First three digits of primary key IDs in DPM physical implementations indicating organizational ownership (e.g. 100 = DPM Metamodel, 101 = EBA, 102 = EIOPA). Enables unique keys when merging models from different databases.

**Implicit Dimension**
Dimension values that are not explicitly represented in data or structures but are understood from context or defaults.

**Information Model**
UML-based conceptual design (SDMX approach) that remains syntax-neutral and implementation-agnostic, focusing on logical structure rather than physical implementation.

**Interoperability**
Ability to exchange data and metadata across different systems, organizations, and standards while preserving semantics.

**Item**
Individual value in an enumerated Category (DPM equivalent of SDMX Code). Items have a code, name, description, and are linked to Categories in a release-aware way.

**ItemScheme**
SDMX pattern for any maintained list (scheme) and its entries (items). Base class for ConceptScheme, Codelist, CategoryScheme, and other scheme types.

### K

**Key Variable**
DPM variable type corresponding to SDMX Dimensions, used to identify or disaggregate observations.

### L

**Lossless Transformation**
Bidirectional mapping between standards that preserves all semantics, enabling round-trip conversion without information loss.

**Lossy Mapping**
Transformation where some information cannot be represented in the target model, resulting in semantic loss or approximation.

### M

**Maintainable Artefact**
SDMX abstract class for objects with versioning, agency ownership, and lifecycle management. Includes Dataflows, Codelists, DSDs, ConceptSchemes, and CategorySchemes. Extends NameableArtefact.

**Maintenance Agency**
Organization responsible for maintaining an SDMX artefact. The Agency ID is a core component of the artefact's identity (Agency + ID + Version).

**Measure**
SDMX component representing the observed or reported value in a data structure. Corresponds to DPM Fact Variables.

**Meta-model**
A "model of the model"—statements and structures defining information requirements. DPM uses a meta-model expressed through entity–relationship structures for physical database implementation.

**Metadata**
Data about data; descriptive information about structure, meaning, quality, and context of observations.

**Metadata Provider**
Organization maintaining reference metadata (Metadata Sets) in SDMX. Distinct from Maintenance Agency, which manages structural metadata.

**Metric**
Informal term for a quantitative Property in DPM (`IsMetric = TRUE`). Metrics have a DataType and are used for numerical values (amounts, ratios, counts). Not a separate artefact in the DPM metamodel, but conceptually distinct from qualitative Properties.

**Module**
DPM sub-container within Frameworks, grouping related tables. Modules inherit their owner from the parent Framework.

**Multi-dimensional Cube**
SDMX conceptualization of data as an n-dimensional structure, where each dimension represents a characteristic and the intersection of dimension values identifies an observation.

### N

**NameableArtefact**
SDMX abstract class extending IdentifiableArtefact with name and description capabilities. Foundation for MaintainableArtefact.

**Non-enumerated Representation**
Values constrained by data type and facets rather than an explicit list. Used for continuous values, dates, free text, or highly volatile value domains.

### O

**Observable**
Something that can be measured or observed, forming the basis for data points in statistical or regulatory reporting.

**Owner / Organisation**
Responsible entity for DPM Concepts. Unlike SDMX's hierarchical agency structure, DPM uses a flat list of Organisations. Each Concept has exactly one Owner.

### P

**Partial**
Flag indicating that a scheme or Codelist disseminates only a subset of items rather than the complete list (`isPartial = true` in SDMX).

**Property**
DPM semantic characteristic used to define information requirements and variables (equivalent to SDMX Concept). Properties always refer to one or more Categories and can be:
- **Qualitative** (`IsMetric = FALSE`): descriptive characteristics.
- **Quantitative** (`IsMetric = TRUE`): identify "what is measured" (Metrics).

**Pull Model**
Data access approach where users actively request data through API queries specifying dimensions and filters (SDMX approach).

### Q

**Qualitative Property**
DPM Property with `IsMetric = FALSE`, providing descriptive characteristics that classify or qualify observations (e.g. country, instrument type, sector).

**Quantitative Property**
DPM Property with `IsMetric = TRUE`, identifying "what is measured". Quantitative Properties (Metrics) have a DataType and indicate whether values are reported at a point in time or over a period.

### R

**Registry**
SDMX metadata catalog that provides visibility into available data and supplies URLs to data located at provider sites. Does not store the data itself, unlike a DPM Repository.

**Release**
DPM construct linking entities to specific versions or states, enabling temporal tracking and release-aware relationships.

**Release-aware**
Property of DPM entities that are linked to specific versions or releases, allowing tracking of changes over time and association with particular regulatory releases.

**Report Table**
DPM artefact roughly corresponding to an SDMX Dataflow + DSD combination. Defines the structure and context for regulatory data collection.

**Reporting Taxonomy**
SDMX organizational structure for grouping Dataflows and DSDs into subject domains or reporting hierarchies, typically using CategorySchemes and Categorisations.

**Representation**
SDMX specification of allowable values for a Concept, either enumerated (via Codelist/ValueList/GeoCodelist) or non-enumerated (via data type and Facets).

**Repository**
DPM shared database containing both metadata and data, following the metamodel structures. All stakeholders access data directly from this common platform.

**RowGUID**
Globally unique identifier (UUID) assigned to every entity in DPM for change logging and synchronization. Ensures uniqueness across distributed databases.

### S

**Scheme**
SDMX maintained container for related items (ConceptScheme, Codelist, CategoryScheme, etc.). Schemes are versioned, maintainable, and owned by an agency. DPM does not use explicit scheme containers; instead, items are organized through cross-domain glossaries and ownership.

**Semantic Loss**
Information that cannot be represented in the target model during transformation between standards, resulting in approximation or loss of meaning.

**Slice**
Multi-dimensional subset of data identified by values for all dimensions except one (typically time). Used in SDMX to conceptualize and retrieve data from multi-dimensional cubes.

**SubCategory**
DPM artefact defining a subset of Items for a given Category, optionally organizing them hierarchically. SubCategories specify which options appear in dropdowns and can provide local labels for Items.

**SubCategoryItem**
Link between a SubCategory and the Items it contains. Supports hierarchical ordering via parent–child relationships and local labels for regulation-specific wording.

**Super Category**
DPM Category flagged as `IsSuperCategory = TRUE`. Brings together other Categories via compositions, enabling Items from several Categories to appear as a single unified value domain. Similar to SDMX Extended Codelists that combine multiple base Codelists.

**Syntax Neutrality**
Capability to serialize metadata and data in multiple formats (XML, JSON, CSV) without changing semantics. Core principle of SDMX Information Model design.

### T

**Table Pattern**
DPM template for structuring tables, including SDMX-like patterns, closed patterns, and open "set axis" patterns.

### U

**UML (Unified Modeling Language)**
Standard notation for modeling object-oriented systems using class diagrams, relationships, and inheritance. Used by SDMX to express the Information Model.

**URN (Universal Resource Name)**
Globally unique identifier string in SDMX composed of an object's identification components: `urn:sdmx:org.sdmx.infomodel.{package}.{class}={agencyID}:{resourceID}({version})`. Ensures interoperability in distributed networks.

**UUID (Universally Unique Identifier)**
Standardized 128-bit identifier format ensuring global uniqueness. Used in DPM as RowGUID for change tracking.

### V

**ValueItem**
Individual entry within an SDMX ValueList, representing a single value in a lightweight enumerated domain.

**ValueList**
SDMX lightweight enumerated value domain without formal "code" semantics, useful for short pick-lists. Contains ValueItem entries.

**Variable**
DPM component defining a characteristic in a report structure. Variables can be Key Variables (dimensions), Fact Variables (measures), or Attribute Variables (attributes).

**Version**
Version string for artefacts (e.g. 1.0, 2.1.0) enabling evolution tracking and ensuring compatibility across different releases. Core component of SDMX identity (Agency + ID + Version).

**Versioning**
Process of managing changes to artefacts over time through version numbers, enabling backward compatibility and change tracking.

## Abbreviations and Acronyms

### Standards and Organizations

**AnaCredit**
Analytical Credit datasets—ECB granular credit and credit risk data framework.

**CDM**
Common Data Model (e.g. ECB CDM), a standardized data structure for a specific domain.

**COREP**
Common Reporting framework—EU banking regulation reporting standard.

**DPM**
Data Point Model—metamodel for defining and implementing regulatory reporting requirements, used by EU financial regulators.

**EBA**
European Banking Authority—EU authority for banking regulation and supervision.

**ECB**
European Central Bank—central bank of the Eurozone, maintains various statistical and regulatory data standards.

**EIOPA**
European Insurance and Occupational Pensions Authority—EU authority for insurance and pensions regulation.

**ISO**
International Organization for Standardization—develops international standards across domains.

**NUTS**
Nomenclature of Territorial Units for Statistics—EU hierarchical system for regional classification.

**SDMX**
Statistical Data and Metadata eXchange—ISO standard (ISO 17369) for exchanging statistical data and metadata.

**Solvency II**
EU regulatory framework for insurance undertakings, including extensive reporting requirements.

**XBRL**
eXtensible Business Reporting Language—standard for electronic communication of business and financial data.

**XBRL-CSV**
CSV serialization format for XBRL, enabling tabular representation of XBRL data.

### Technical Formats and Protocols

**API**
Application Programming Interface—set of protocols and tools for building software applications and enabling system interaction.

**CSV**
Comma-Separated Values—simple tabular data format using commas to separate values.

**GUID**
Globally Unique Identifier—Microsoft implementation of UUID.

**JSON**
JavaScript Object Notation—lightweight data interchange format.

**REST**
Representational State Transfer—architectural style for web services, typically using HTTP methods.

**SQL**
Structured Query Language—standard language for relational database management and querying.

**UML**
Unified Modeling Language—standardized modeling language for object-oriented software design.

**URL**
Uniform Resource Locator—web address specifying the location of a resource.

**URN**
Universal Resource Name—persistent, location-independent identifier within a namespace.

**UUID**
Universally Unique Identifier—128-bit identifier designed to be unique across space and time.

**XML**
eXtensible Markup Language—markup language for encoding documents in human-readable and machine-readable format.

### Data and Structural Components

**CL_**
Prefix for Codelist identifiers in SDMX (e.g. `CL_FREQ` for frequency codelist, `CL_AREA` for area/country codelist).

**CS_**
Prefix for ConceptScheme identifiers in SDMX (e.g. `CS_COMMON` for a common concept scheme).

**DSD**
Data Structure Definition—SDMX artefact defining the complete structure of a dataset through dimensions, attributes, and measures.

**GSD**
Generic Statistical Data—SDMX concept for standard statistical data structures.

**ID**
Identifier—unique reference to an entity or artefact.

**ISIN**
International Securities Identification Number—unique identifier for securities.

**LEI**
Legal Entity Identifier—unique identifier for legal entities participating in financial transactions.

**OBS**
Observation—prefix used in SDMX for observation-related components (e.g. `OBS_VALUE` for the observed value, `OBS_STATUS` for observation status).

**REF**
Reference—prefix often used for reference dimensions or attributes (e.g. `REF_AREA` for reference area/country dimension).

**VID**
Version ID—identifier for specific versions in DPM structures (e.g. SubCategoryVID linking to a versioned SubCategory).

### Process and Methodology

**Refit**
Regulatory Fitness and Performance—EU program for making legislation simpler and less costly (e.g. DPM 2.0 represents the updated DPM version).

**CRS**
Coordinate Reference System—system for defining geospatial coordinates in GeoCodelists.

## Usage Notes

### Terms with Different Meanings Across Standards

Several terms are used in both SDMX and DPM but with different meanings or scope:

- **Concept**: In SDMX, a semantic definition in a ConceptScheme. In DPM architectural discussions, refers broadly to any identifiable model object (Category, Item, Property).
- **Scheme**: SDMX uses explicit scheme containers (ConceptScheme, Codelist as ItemScheme). DPM uses a cross-domain glossary without explicit scheme artefacts.
- **Code vs. Item**: Parallel structures—SDMX Codes within Codelists correspond to DPM Items within Categories.
- **Property vs. Concept**: DPM Properties are semantic characteristics (qualitative or quantitative). SDMX Concepts serve the same role but use different terminology.
- **Registry vs. Repository**: SDMX Registry is a metadata catalog without data storage. DPM Repository is a shared database containing both metadata and data.

### Naming Conventions

- **SDMX identifiers**: Often use prefixes like `CL_` for Codelists, `CS_` for ConceptSchemes, and `DF_` for Dataflows.
- **SDMX URNs**: Follow the format `urn:sdmx:org.sdmx.infomodel.{package}.{class}={agencyID}:{resourceID}({version})`.
- **DPM IDPrefix**: First three digits of primary keys indicate organizational ownership (100, 101, 102, etc.).
- **Qualitative vs. Quantitative**: DPM distinguishes Properties using the `IsMetric` flag; quantitative Properties (`IsMetric = TRUE`) are informally called Metrics.

### Common Confusions

- **Partial** does not mean "incomplete"—it indicates that a scheme intentionally disseminates a subset of items rather than the full list.
- **Extended Codelist** can both restrict (subset) and extend (add codes)—the term covers both operations.
- **Maintainable** refers to artefacts that have agency ownership and versioning—not all artefacts are maintainable (e.g. individual Codes within a Codelist are not).
- **Hierarchy** in SDMX is a richer artefact than simple parent–child relationships within a Codelist—it can span multiple Codelists and support multiple parents.
