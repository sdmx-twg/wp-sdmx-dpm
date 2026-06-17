# 2. Constraints and examples

Building on the format comparison in [§1](01_sdmx_csv_xbrl_csv.md), this chapter states the conditions under which SDMX-CSV and XBRL-CSV are mutually consumable, then works one example in each direction.

## 2.1 Conditions for interoperability

A data file in one serialisation can be read with the other model's metadata when **all** of the following hold:

1. **The structural mapping exists.** A Dataflow + DSD ↔ Table correspondence is already established ([Transformation Guidelines §2–3](../transformation-guidelines/02_dpm_to_sdmx.md)), so every column resolves to a known component on both sides.
2. **The full key is recoverable.** Every dimension value is available per observation — either as an explicit SDMX column, or by combining XBRL-CSV per-row columns with report parameters. Implicit/default dimensions must be expanded to explicit members ([§05 §2.1](../models-relationships/05_gaps/02_specific_gap_analysis.md)).
3. **The metric is unambiguous.** Either explicit SDMX Measures are used, or a single `OBS_VALUE` plus a `MEASURE` dimension is absorbed into the DPM FactVariable identity ([§05 §2.2](../models-relationships/05_gaps/02_specific_gap_analysis.md)).
4. **Stock/flow and time granularity are explicit**, so `TIME_PERIOD` ↔ instant/duration can be derived ([§1.5](01_sdmx_csv_xbrl_csv.md)).
5. **Identifiers are normalised reversibly** across the SDMX/DPM/XBRL syntaxes ([§1.4](01_sdmx_csv_xbrl_csv.md)).
6. **Constraints are flattened.** SDMX `ContentConstraint`/`CubeRegion` value restrictions and `cascadeValues` hierarchies are expanded to explicit member lists matching the DPM SubCategories; `DataKeySet` (explicit key combinations) cannot be faithfully expressed in a flat table and needs Operations or enumeration ([§05 §2.1](../models-relationships/05_gaps/02_specific_gap_analysis.md)).

Where a condition fails, the file is still convertible but **lossy or requiring human input**, and the gap should be recorded as an annotation.

## 2.2 Example — reading SDMX-CSV with DPM metadata

Source SDMX-CSV (one row per observation):

```text
STRUCTURE,STRUCTURE_ID,FREQ,REF_AREA,TIME_PERIOD,OBS_VALUE
dataflow,EBA:CBD2(1.0),A,ES,2024,1234.5
```

To consume this with DPM metadata:

1. Resolve `CBD2` to its DPM Table; map columns `FREQ`, `REF_AREA` → KeyVariables, `OBS_VALUE` → FactVariable (per the established mapping).
2. The row's key `{FREQ=A, REF_AREA=ES, TIME_PERIOD=2024}` identifies the DPM data point; `1234.5` is its reported value.
3. To re-serialise as XBRL-CSV, factor the shared context (`FREQ=A`, period `2024`) into report **parameters**, decide period type from the metric's stock/flow (`2024` → `duration` if a flow), and emit the metric value in the table CSV.

Interoperability holds here because every dimension is explicit, there is a single measure, and the period maps cleanly.

## 2.3 Example — reading XBRL-CSV with SDMX metadata

Source XBRL-CSV report package:

```text
# JSON parameters: entityID=LEI123, refPeriod=2024-12-31, FREQ=A
# table t_CBD2.csv
REF_AREA,OBS_VALUE
ES,1234.5
```

To consume this with SDMX metadata:

1. Read the JSON to learn the taxonomy, the bound columns, and the parameters.
2. **Materialise the parameters as explicit dimensions**: every emitted SDMX row must carry `FREQ=A` and a `TIME_PERIOD` derived from `refPeriod` (`2024-12-31` instant → the corresponding SDMX time period), plus the reporting entity if modelled as a component.
3. Map the metric concept to the SDMX Measure and emit one observation per fact:

```text
STRUCTURE,STRUCTURE_ID,FREQ,REF_AREA,TIME_PERIOD,OBS_VALUE
dataflow,EBA:CBD2(1.0),A,ES,2024,1234.5
```

The conversion is faithful provided the period type is known (to translate the instant date into a `TIME_PERIOD`) and the entity is representable as an SDMX component.

## 2.4 Summary

| Direction | Main task | Main risk |
| --- | --- | --- |
| SDMX-CSV → DPM/XBRL | Factor repeated columns into parameters; derive period type | Stock/flow not marked at source |
| XBRL-CSV → SDMX | Materialise parameters as explicit dimension columns | Entity/period not modelled as SDMX components |

In both directions the metadata mapping does the heavy lifting; the serialisation step is a mechanical re-shaping **once** the conditions in [§2.1](#21-conditions-for-interoperability) are met.
