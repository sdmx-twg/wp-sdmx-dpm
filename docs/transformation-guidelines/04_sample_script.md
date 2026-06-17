# 4. Sample conversion script

The [`dpm_to_sdmx`](https://github.com/antonio-olleros/dpm_to_sdmx) repository is the reference implementation that demonstrates the [DPM → SDMX](02_dpm_to_sdmx.md) glossary mapping on real EBA data. It satisfies the work package's commitment to provide *at least one sample conversion script* ([Business Case §3.3](../business-case/index.md)).

## 4.1 What it does

The tool reads an **EBA DPM Access database** (`.accdb`) and emits SDMX structure XML. It covers the **glossary layer** of the methodology ([§1.1](01_methodology.md)) — the prerequisite for any data-definition or data-instance conversion.

| Aspect | Detail |
| --- | --- |
| **Language** | Python 3.11 (Poetry-managed) |
| **Dependencies** | `pyodbc` (Access connectivity), `pysdmx[data]` (SDMX structure creation) |
| **Input** | An EBA DPM Access database file |
| **Source tables** | `Category`, `Item`, `ItemCategory`, `Property`, `PropertyCategory`, `DataType` |

## 4.2 Outputs

Three XML files are written to `output/`:

| File | Contents | Maps to chapter |
| --- | --- | --- |
| `agency_scheme.xml` | EBA organisational metadata | [§2.2 Owner / Agency](02_dpm_to_sdmx.md) |
| `codelists.xml` | DPM Categories as SDMX Codelists, Items as Codes | [§2.3 Category → Codelist](02_dpm_to_sdmx.md) |
| `properties.xml` | DPM Properties as SDMX Concepts with data types | [§2.3 Property → Concept](02_dpm_to_sdmx.md) |

## 4.3 How to run

```bash
poetry install
# edit the database path variable at the top of the script, then:
poetry run python generate_sdmx_glossary.py
```

No other parameters are required.

## 4.4 Mapping behaviour worth noting

- **Data-type mapping** across the DPM types (integer, decimal, string, boolean, date) into SDMX `TextFormat` text types — this is the deterministic representation mapping from [§3.3 Concept → Property](03_sdmx_to_dpm.md), applied in reverse.
- **Property ↔ Codelist linkage** — enumerated Properties are connected to the Codelist derived from their Category, mirroring [§2.3](02_dpm_to_sdmx.md).
- **Deduplication** of Items and Concepts, since the same value can appear across multiple DPM rows.
- **Exclusion of internal categories** (DPM bookkeeping categories such as `_PR`) that should not surface as published Codelists.

## 4.5 Scope and limitations

- The script implements the **glossary layer only**. The data-definition layer (Tables → Dataflow + DSD) and the data-instance layer (CSV reports) shown in [§2](02_dpm_to_sdmx.md) and [Data Instances](../data-instances/index.md) are not yet automated — they are documented here as manual recipes.
- It targets the EBA DPM Access distribution specifically; other DPM repositories may use different table layouts.
- Convention-driven and judgement-based outputs ([§1.2](01_methodology.md)) — ConceptScheme grouping, stock/flow, compound items — are not resolved automatically and should be reviewed.
