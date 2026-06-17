# 1. SDMX-CSV and XBRL-CSV

This chapter describes the two CSV serialisations and how a single observation is expressed in each, so that the alignment in [§2](02_constraints_and_examples.md) can be made precise.

## 1.1 SDMX-CSV at a glance

SDMX-CSV (the SDMX 3.x flat serialisation) is a single table where **each row is one observation**:

- Leading control columns identify the structure and the action: `STRUCTURE` (e.g. `dataflow`), `STRUCTURE_ID` (the artefact reference, e.g. `EBA:CBD2(1.0)`), and optionally `ACTION`.
- The remaining columns are one per **component**, headed by the component `id`: every Dimension, the Measure(s), and the Attributes.
- A row therefore carries the full key (all dimension values), the observed value, and any attribute values in one line.

```text
STRUCTURE,STRUCTURE_ID,FREQ,REF_AREA,TIME_PERIOD,OBS_VALUE,OBS_STATUS
dataflow,EBA:CBD2(1.0),A,ES,2024,1234.5,A
dataflow,EBA:CBD2(1.0),A,FR,2024,2345.6,A
```

The structure is **dimensional and open**: the DSD defines the dimension space, and the file lists the observations that exist within it.

## 1.2 XBRL-CSV at a glance

XBRL-CSV (the Open Information Model CSV serialisation, the de-facto DPM format) is a **report package**, not a single file:

- A **JSON metadata document** declares the taxonomy (the DPM taxonomy), the tables, the columns, and report-level **parameters** (e.g. the reporting entity and reference period).
- One or more **CSV table files** carry the cells. Each column is bound by the JSON to a concept (the metric) or to a dimension; each row contributes one or more **facts**.
- A fact resolves to a **metric (concept) + period + entity + a set of dimension members**. Dimensions and the period/entity are often supplied once as parameters and combined with the per-row dimension columns.

```text
# parameters in JSON: entityID=LEI123, refPeriod=2024-12-31
# table t_CBD2.csv:
REF_AREA,OBS_VALUE
ES,1234.5
FR,2345.6
```

The structure is **closed/explicit**: the taxonomy enumerates which data points (metric × dimensional context) are valid, and the CSV reports values for those points.

## 1.3 Structural alignment

| Concern | SDMX-CSV | XBRL-CSV | Alignment |
| --- | --- | --- | --- |
| Unit of a row | One observation | One row → one or more facts | A row aligns when one XBRL-CSV row yields exactly one fact per metric column. |
| Dimensions | Explicit columns, all in every row | Mix of per-row columns and JSON parameters | DPM↔SDMX dimension mapping ([Transf. §3.4](../transformation-guidelines/03_sdmx_to_dpm.md)) must resolve each parameter into an explicit dimension value. |
| Measured value | `OBS_VALUE` (or explicit measures) | The fact's value, keyed by the metric concept | See multi-measure handling, [§05 §2.2](../models-relationships/05_gaps/02_specific_gap_analysis.md). |
| Entity / reporter | An attribute or dimension if modelled | A report parameter (e.g. LEI) | SDMX must carry the entity as an explicit component to round-trip. |
| Reference period | `TIME_PERIOD` column | Period parameter / fact period (instant or duration) | See [§1.5](#15-time-instant-vs-duration). |

The single most important difference: SDMX-CSV repeats the **full dimensional key on every row**, whereas XBRL-CSV factors shared context into JSON **parameters**. Interoperability requires materialising those parameters as explicit columns (SDMX direction) or factoring repeated columns into parameters (XBRL direction).

## 1.4 Identifier restrictions

Component and code identifiers must satisfy both models' syntaxes:

- SDMX `id`s and Codelist Codes follow SDMX ID/URN rules (restricted character set, no spaces).
- DPM codes are typically alphanumeric, may be longer, and allow underscores.
- XBRL QName-based identifiers (concepts, dimensions, members) have their own lexical rules.

**Recommendation:** normalise identifiers at the boundary (replace spaces/special characters, keeping a reversible map); the conversion is lossless as long as the map is published and applied in reverse on import (see [§05 identifier restrictions](../models-relationships/05_gaps/02_specific_gap_analysis.md)).

## 1.5 Time: instant vs. duration

- SDMX represents time with `TIME_PERIOD` and a TimeDimension whose facet value type carries the intended granularity.
- XBRL distinguishes **instant** (a point in time, typical of stock/balance figures) from **duration** (a period, typical of flow figures), driven by the concept's `periodType`.
- DPM carries this as the Property's stock/flow / `PeriodType`.

For interoperability, the stock/flow classification must be explicit so that a `TIME_PERIOD` can be rendered as an XBRL `instant` (stock) or `duration` (flow), and vice versa. Where it is not marked in the source it is a judgement-based step ([Transf. §1.2](../transformation-guidelines/01_methodology.md)) and must be supplied. This is the data-instance face of [§05 §2.3 stock/flow & temporal](../models-relationships/05_gaps/02_specific_gap_analysis.md).
