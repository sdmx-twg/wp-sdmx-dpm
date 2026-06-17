# Data Instances

The [Model Relationships](../models-relationships/index.md) and [Transformation Guidelines](../transformation-guidelines/index.md) sections deal with **metadata** — the structures and vocabulary. This section deals with **data instances**: the actual reported values exchanged as CSV files.

The work package's concept note commits to describing *"the constraints under which SDMX-CSV and XBRL-CSV can be interoperable, meaning that they can be easily used with DPM metadata (for SDMX-CSV) or with SDMX metadata (for XBRL-CSV)"*. That is the subject of this section.

## The two questions

| Question | Meaning |
| --- | --- |
| **Can an SDMX-CSV file be read with DPM metadata?** | The data is serialised in SDMX-CSV, but a consumer holds the DPM definition of the same structure. |
| **Can an XBRL-CSV file be read with SDMX metadata?** | The data is serialised in XBRL-CSV (the de-facto DPM serialisation), but a consumer holds the SDMX definition. |

Both reduce to the same requirement: the **structural mapping must already be in place** (a Dataflow + DSD ↔ Table correspondence from [Transformation Guidelines §2–3](../transformation-guidelines/02_dpm_to_sdmx.md)), and each row/fact in one serialisation must be addressable in the other model's terms.

## Contents

- [1. SDMX-CSV and XBRL-CSV](01_sdmx_csv_xbrl_csv.md) — how the two formats are structured and how their columns/cells align, including identifier rules and time semantics.
- [2. Constraints and examples](02_constraints_and_examples.md) — the conditions under which interoperability holds, with a worked example in each direction.

## Prerequisites

- A completed metadata mapping ([Transformation Guidelines](../transformation-guidelines/index.md)).
- Awareness of the data-instance [Gaps](../models-relationships/05_gaps/02_specific_gap_analysis.md): defaults & implicit dimensions, multi-measure vs `OBS_VALUE`, stock/flow and temporal semantics, and identifier restrictions — these are exactly the points where serialisation-level interoperability can break.

## Scope

XBRL is in scope only as the serialisation needed to exchange DPM content as CSV. XBRL features beyond the DPM/CSV use case are out of scope.
