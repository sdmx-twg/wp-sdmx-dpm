# 5. Data types mapping (proposal)

This file is the **authoritative proposal** for mapping DPM `DataType`s to SDMX
representations and back. It is referenced by the glossary mapping rules
([§01 §3.5.3.5](../models-relationships/01_glossary/03_detailed_mapping_rules.md#3535-data-type-mapping))
and implemented in `src/wp_sdmx_dpm/mapping/glossary.py` (`_DATATYPE_MAP`,
`_SDMX_TO_DPM_DATATYPE`). Any change here must be reflected in that module, and
vice versa.

## 5.1 Where the representation lives

In SDMX, the value domain of a characteristic is the **representation** of a
`Concept` (its *core representation*, the SDMX term sometimes rendered as the
"global representation") or of a DSD `Component` (its *local representation*).
There are two kinds:

| Kind | DPM trigger | SDMX representation |
|------|-------------|---------------------|
| **Enumerated** | `Property.DataType = Enumeration` (`e`) with a `PropertyCategory` | `<Enumeration>` referencing the `Codelist` mapped from the Category |
| **Non-enumerated** | any other `DataType` | `<TextFormat textType="…"/>` (+ optional facets) |

The converter sets the **core representation on the Concept**: enumerated
Concepts reference their Codelist; non-enumerated Concepts carry a `textType`
derived from the table below. This follows the design decision in
[§01 §3.5.7](../models-relationships/01_glossary/03_detailed_mapping_rules.md#357-representation-mapping-core-vs-local)
(PropertyCategory ↔ CoreRepresentation).

> **Implementation note**: pysdmx's SDMX-ML writer emits a Concept's enumerated
> representation only from the `codes` field (a `Codelist` reference), **not**
> from `enum_ref`. The converter therefore sets `Concept.codes` to a lightweight
> Codelist reference (id/agency/version) so the `<Enumeration>` is serialised;
> `enum_ref` is also set for URN-based tooling and round-tripping.

## 5.2 DPM → SDMX data type correspondence

The full DPM `DataType` catalogue and its SDMX target. The **SDMX `textType`**
column is the value written into `<TextFormat textType="…"/>`; the **pysdmx
`DataType`** column is the enum member used in code.

| DPM code | DPM name | Classification | pysdmx `DataType` | SDMX `textType` | Lossy? |
|----------|----------|----------------|-------------------|-----------------|--------|
| `e`  | Enumeration | Enumerated | — (enumeration) | — (Codelist ref) | No |
| `i`  | Integer | Open (numeric) | `INTEGER` | `Integer` | No |
| `r`  | Decimal | Open (numeric) | `DECIMAL` | `Decimal` | No |
| `m`  | Monetary | Open (numeric) | `DECIMAL` | `Decimal` | **Yes** — currency/unit semantics lost |
| `p`  | Percentage | Open (numeric) | `DECIMAL` | `Decimal` | **Yes** — % semantics lost |
| `o`  | Ordinals | Open (numeric) | `INTEGER` | `Integer` | **Yes** — ordering/labels lost |
| `s`  | String (non-empty) | Open (text) | `STRING` | `String` | No |
| `es` | String (incl. empty) | Open (text) | `STRING` | `String` | minor — empty-string distinction not expressible |
| `u`  | URI | Open (text) | `URI` | `URI` | No |
| `b`  | Boolean | Open (logical) | `BOOLEAN` | `Boolean` | No |
| `t`  | True | Open (logical) | `BOOLEAN` | `Boolean` | minor — subtype collapsed to Boolean |
| `dt` | Date time | Open (temporal) | `DATE_TIME` | `DateTime` | No |
| `d`  | Date | Open (temporal) | `DATE` | `GregorianDay` | No |

**Lossy mappings emit a `datatype.lossy` review flag** (`m`, `p`, `o`) so the
loss is surfaced for human review rather than silently applied.

### Design decisions (open for review)

- **`d` Date → `GregorianDay`.** A DPM Date is a calendar date, so the ISO date
  type `GregorianDay` (e.g. `2011-06-17`) is the most faithful target. The
  alternative `ObservationalTimePeriod` is more appropriate when the date is a
  *reporting period* in a time series; it can be selected per-Concept when that
  is known. (The earlier draft in §01 §3.5.3.5 proposed `ObservationalTimePeriod`
  as the default — this file supersedes that choice.)
- **`o` Ordinals → `Integer`.** SDMX has no ordered-enumeration scalar type. The
  numeric ordinal value is preserved; the value labels and ordering semantics are
  not. An alternative is to model ordinals as an enumerated Codelist with
  `is_sequence` facets — out of scope for the automatic mapping.
- **`m` Monetary / `p` Percentage → `Decimal`.** SDMX has no monetary or
  percentage scalar type. See §5.4 for why this cannot be recovered automatically.

## 5.3 Facets

DPM open properties carry a few facet-like attributes. Only `ValueLength` has a
clean SDMX target:

| DPM | SDMX facet | Direction |
|-----|------------|-----------|
| `ValueLength` (integer) | `maxLength` in `<TextFormat>` | Bidirectional |
| – | `minLength` | No DPM equivalent |
| – | `minValue` / `maxValue` | No DPM equivalent |
| – | `pattern` (regex) | No DPM equivalent |
| – | `decimals` | No DPM equivalent |

On SDMX → DPM, only `maxLength` is preserved (in `ValueLength`); other facets are
documented in the Property description but not enforced at the schema level.

## 5.4 SDMX → DPM type selection

Reverse mapping picks the closest DPM `DataType`. Because DPM has finer numeric
and temporal types than SDMX exposes in a `textType`, several SDMX types collapse
onto one DPM code:

| SDMX `textType` (pysdmx `DataType`) | DPM code | DPM name |
|-------------------------------------|----------|----------|
| `Integer` / `Long` / `Short` / `Count` | `i` | Integer |
| `Decimal` / `Float` / `Double` / `Numeric` | `r` | Decimal |
| `Boolean` | `b` | Boolean |
| `GregorianDay` (`DATE`) | `d` | Date |
| `ObservationalTimePeriod` / `BasicTimePeriod` | `d` | Date |
| `DateTime` | `dt` | Date time |
| `String` | `es` | String (incl. empty) |
| `URI` | `u` | URI |
| *(enumerated — Codelist reference)* | `e` | Enumeration |
| *(anything else)* | `es` | String (default) |

> **Monetary / Percentage upgrade**: nothing in an SDMX `Decimal` representation
> distinguishes a monetary amount or a percentage from a plain decimal, so the
> automatic mapping always yields DPM `Decimal` (`r`). When a Concept is known to
> be monetary or a percentage, the `DataType` should be **manually upgraded** to
> `Monetary` (`m`) or `Percentage` (`p`) as a post-mapping step (a per-Concept
> configuration table can drive this in bulk). Concept-name analysis is **not**
> used automatically because it is unreliable.
