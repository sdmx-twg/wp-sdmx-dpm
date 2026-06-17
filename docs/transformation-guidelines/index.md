# Transformation Guidelines

This section provides practical guidance for transforming structures and data between SDMX and DPM in both directions. Where the [Model Relationships](../models-relationships/index.md) section explains *what* corresponds to *what*, this section explains *how* to perform a conversion in practice — the order of operations, the deterministic vs. judgement-based steps, and worked examples end to end.

## Contents

- [1. Methodology](01_methodology.md) — the overall transformation approach: metadata-first, what is deterministic, and where human input is required.
- [2. DPM → SDMX](02_dpm_to_sdmx.md) — a worked example converting a DPM glossary and table into SDMX structures.
- [3. SDMX → DPM](03_sdmx_to_dpm.md) — the reverse direction, converting an SDMX Dataflow + DSD into a DPM Table.
- [4. Sample conversion script](04_sample_script.md) — walkthrough of the `dpm_to_sdmx` reference implementation.

## Prerequisites

These guidelines assume familiarity with:

- The artefact correspondences in [Glossary mapping](../models-relationships/01_glossary/02_high_level_mapping_summary.md) and [Data Definition mapping](../models-relationships/02_data_definition/02_high_level_mapping_summary.md).
- The known [Gaps](../models-relationships/05_gaps/index.md), which determine where a transformation is lossless, lossy, or requires conventions.
- The [Glossary & Abbreviations](../models-relationships/glossary_and_abbreviations.md) for terminology.

## Scope

- The focus is the core SDMX 3.1 ↔ DPM 2.0 mapping. Serialisation-level (CSV report) interoperability is covered separately in [Data Instances](../data-instances/index.md).
- Examples use the EBA DPM conventions where a concrete convention is needed (e.g. item codes, `_PR` properties category), as these are the most widely deployed.

## Existing repositories

- [DPM to SDMX](https://github.com/antonio-olleros/dpm_to_sdmx) — reference Python implementation that converts an EBA DPM Access database into SDMX structure XML. See [§4](04_sample_script.md).
