# wp-sdmx-dpm — DPM ↔ SDMX conversion

Bidirectional conversion between the **DPM 2.0 Refit** metamodel and **SDMX 3.1**,
built on [`dpmcore`](https://github.com/Meaningful-Data/dpmcore) (read the DPM
database / write a new one) and [`pysdmx`](https://github.com/bis-med-it/pysdmx)
(build, read, and serialise SDMX structures).

- **DPM → SDMX**: translate a **Module** (read from a DPM SQLite database) into
  SDMX structures — Codelists, a ConceptScheme, and one DSD + Dataflow per table.
  Output as SDMX-ML or SDMX-JSON.
- **SDMX → DPM**: translate an SDMX **structure** (a Dataflow + DSD, read from an
  FMR registry *or* a local SDMX file) into a new, valid DPM SQLite database
  containing the flat table and its glossary.

The authoritative mapping rules live in [`../docs/transformation-guidelines/`](../docs/transformation-guidelines/).

## Install

The package lives under `src/` (src-layout). Install it editable into the
project virtualenv:

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

This pulls in `pysdmx[all]` and `dpmcore`, and registers two console scripts:
`dpm-to-sdmx` and `sdmx-to-dpm`.

## Usage

### DPM → SDMX (translate a Module)

```bash
dpm-to-sdmx \
  --db input/dpm_4.2.1_20260606.db \
  --module COREP_LE \
  --out out/ \
  --format sdmx-ml          # or: json
```

| Option | Meaning |
|--------|---------|
| `--db` | Path to the input DPM SQLite database |
| `--module` | Module code, e.g. `COREP_LE` |
| `--release` | DPM release code (default: latest) |
| `--out` | Output directory |
| `--format` | `sdmx-ml` (SDMX-ML 3.1, default) or `json` (SDMX-JSON 2.0) |
| `--layers` | Comma-separated subset of `glossary,data-def,constraints` (default: `glossary,data-def`) |

Writes `<MODULE>.<ext>` (the structures) and `<MODULE>.review.json` (the review
report, see below) into `--out`.

Example output for `COREP_LE`: 18 Codelists, 1 ConceptScheme, and 4 DSD +
4 Dataflow pairs (28 Dimensions / 25 Measures), validated against the SDMX 3.1
schema.

### SDMX → DPM (translate a structure)

```bash
# from a local SDMX-ML / SDMX-JSON file
sdmx-to-dpm \
  --source path/to/structures.xml \
  --structure "EBA:CBD2(1.0)" \
  --out out/dpm_generated.db

# from an FMR registry endpoint (auto-detected by the http(s):// prefix)
sdmx-to-dpm \
  --source https://registry.example.org/sdmx/v2 \
  --structure "ECB:CBD2(1.0)" \
  --out out/dpm_generated.db
```

| Option | Meaning |
|--------|---------|
| `--source` | FMR endpoint URL **or** a local SDMX file path (auto-detected) |
| `--structure` | Structure reference: `AGENCY:ID(VERSION)`, `AGENCY:ID`, or `ID` |
| `--out` | Output DPM SQLite database path (created fresh) |
| `--layers` | Comma-separated subset of `glossary,data-def,constraints` (default: `glossary,data-def`) |

Produces a new DPM SQLite database holding a **flat** table (`IsFlat=TRUE`), its
glossary (Categories/Items, Properties), and the mandatory Module/ModuleVersion.
The database is verified with dpmcore's `validate_schema()` before the command
returns and is fully queryable via dpmcore's `StructureService`.

## Library use

```python
from wp_sdmx_dpm.convert.dpm_to_sdmx import convert_module
from wp_sdmx_dpm.sdmx.serializer import serialize

result = convert_module("input/dpm_4.2.1_20260606.db", "COREP_LE")
serialize(result.objects, "sdmx-ml", "out/COREP_LE.xml")
print(result.report.to_json())          # review flags
```

```python
from wp_sdmx_dpm.convert.sdmx_to_dpm import convert_structure

result = convert_structure("structures.xml", "EBA:CBD2(1.0)", "out/dpm.db")
print(result.is_valid, result.tables_written)
```

## Conventions and the review report

Every non-deterministic mapping choice is centralised in
[`wp_sdmx_dpm/config.py`](wp_sdmx_dpm/config.py) (`Conventions`): owner↔agency
map, ConceptScheme grouping, `IsMetric` heuristics, default-Item selection,
identifier-normalisation rules.

Judgement-based decisions are **never made silently** — each one records a
`ReviewFlag` on a `ReviewReport` with a severity:

- `info` — a convention was applied (recorded for transparency)
- `review` — a defensible default was chosen; please check it
- `blocking` — no safe default exists; the output is incomplete

The CLIs write/return the report and exit non-zero when a blocking flag is
raised (the artefact is still produced, so it can be inspected). Common flags:
`dsd.no_dimensions` (a cover/info table with no dimensions is skipped),
`reporting_taxonomy.unsupported` (Module grouping recorded as a `DPM_MODULE`
annotation, since pysdmx has no ReportingTaxonomy), `module.synthesised`,
`default_item.missing`.

## Package layout

```
wp_sdmx_dpm/
  config.py            Conventions + ReviewFlag/ReviewReport
  ids.py               reversible DPM<->SDMX id normalisation + annotations
  cli.py               dpm-to-sdmx / sdmx-to-dpm entry points
  dpm/
    reader.py          read modules/glossary from the DPM DB (dpmcore)
    writer.py          write a new DPM SQLite DB (dpmcore ORM)
  sdmx/
    source.py          load SDMX structures (FMR registry or local file)
    builder.py         assemble pysdmx objects for a module
    serializer.py      write SDMX-ML / SDMX-JSON
  mapping/
    glossary.py        Category/Item<->Codelist/Code ; Property<->Concept
    data_definition.py Table<->DSD+Dataflow ; Variables<->Components
    constraints.py     SubCategory<->ContentConstraint  (planned)
  convert/
    dpm_to_sdmx.py     orchestrator: module -> SDMX
    sdmx_to_dpm.py     orchestrator: structure -> DPM DB
```

## Status

| Layer | DPM → SDMX | SDMX → DPM |
|-------|:---------:|:---------:|
| Glossary (Codelists, Concepts) | ✅ | ✅ |
| Data definition (DSD/Dataflow ↔ flat Table) | ✅ | ✅ |
| Constraints (SubCategory ↔ ContentConstraint) | planned | planned |

SDMX → DPM always produces **flat** tables (the DSD is inherently flat). For
DPM → SDMX, non-flat EBA tables have their dimensions reconstructed from the
union of each FactVariable's Context (spec §3.2.7).

## Tests

```bash
.venv/bin/python -m pytest -q
```

Tests that need the (gitignored, ~400 MB) input DPM database skip automatically
when it is absent.
