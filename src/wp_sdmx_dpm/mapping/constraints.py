"""Constraint-layer mapping (spec section 3.3): DPM Variables -> ContentConstraint.

DPM -> SDMX (this module; the user's primary direction)
    Table's FactVariable Contexts -> one DataConstraint attached to its Dataflow.

A non-flat DPM table does not carry a separate constraint artefact: the set of
its FactVariable Contexts *is* the valid-series space (spec 3.3.2.2). How that
space is expressed in SDMX depends on whether the table is *closed* (no open
axes -- a finite, enumerated set of data points) or *open* (rows/columns/sheets
may be added at report time):

* **Closed table -> DataKeySet** (spec 3.3.8, Option B). The data points are a
  finite set, so the faithful representation enumerates the distinct full
  dimension keys -- one ``Key`` per series. Data points that differ only by
  metric collapse to one series key (SDMX measures are not part of the key).
* **Open table -> CubeRegion** (spec 3.3.8, Option A). An open axis means the key
  set is unbounded, so the space is described dimension-wise: one ``KeyValue``
  per dimension listing the allowed Items.

Where a Context does not pin a dimension Property, that Property takes its
Category **default Item**; SDMX has no implicit default, so the default Item is
listed explicitly (in the CubeRegion values, or as the dimension's value in each
defaulting key). The reader flags this via ``usesDefault``.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from pysdmx.model.constraint import (
    ConstraintAttachment,
    CubeKeyValue,
    CubeRegion,
    CubeValue,
    DataConstraint,
    DataKey,
    DataKeyValue,
    KeySet,
)

from ..config import Conventions, ReviewReport, ReviewSeverity
from ..ids import normalise_sdmx_id


def _dataflow_urn(agency: str, dataflow_id: str, version: str = "1.0") -> str:
    """URN of the Dataflow a constraint attaches to (SDMX 3.0 attachment form)."""
    return (
        f"urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow="
        f"{agency}:{dataflow_id}({version})"
    )


def _new_constraint(table, agency, *, cube_regions=(), key_sets=()):
    table_code = table["code"]
    return DataConstraint(
        id=normalise_sdmx_id(f"{table_code}_CONSTRAINTS"),
        name=f"Allowed values for {table.get('name') or table_code}",
        description=table.get("description"),
        agency=agency,
        version="1.0",
        constraint_attachment=ConstraintAttachment(
            data_provider=None,
            dataflows=(_dataflow_urn(agency, normalise_sdmx_id(table_code)),),
        ),
        cube_regions=tuple(cube_regions),
        key_sets=tuple(key_sets),
    )


def table_to_content_constraint(
    table: Dict[str, Any],
    ordered_dim_ids: List[str],
    keys: List[Dict[str, str]],
    uses_default: Dict[str, bool],
    *,
    closed: bool,
    agency: str,
    conventions: Conventions,
    report: ReviewReport,
    datapoint_count: Optional[int] = None,
    open_key_values: Optional[List[Tuple[str, List[str]]]] = None,
) -> Optional[DataConstraint]:
    """Map one DPM Table's data-point keys to an SDMX DataConstraint.

    ``ordered_dim_ids`` are the context DSD Dimension ids in order; ``keys`` is
    the list of distinct data-point dimension keys (each ``{dim_id: code}``,
    default Item already filled in by the reader); ``uses_default[dim_id]`` flags
    dimensions that defaulted somewhere. ``closed`` selects the representation: a
    DataKeySet of the full keys (closed table) or a CubeRegion of per-dimension
    value lists (open table).

    ``open_key_values`` are the *open-axis* dimensions (only present on open
    tables): ``(dim_id, [allowed item codes])`` pairs for **enumerated** open
    keys, whose rows are open but whose values are confined to the open-axis
    SubCategory subset. They are appended to the CubeRegion after the context
    dimensions. A non-enumerated open key is a DSD Dimension but is left out of
    the constraint (its string values are unconstrained); it never appears here.

    Returns ``None`` (and a flag) when there is nothing to constrain.
    """
    table_code = table["code"]
    artefact = f"Table:{table_code}"
    open_key_values = [kv for kv in (open_key_values or []) if kv[1]]

    if (not ordered_dim_ids or not keys) and not open_key_values:
        report.add(
            "constraint.empty",
            "Table yields no constrained dimension values; no ContentConstraint "
            "emitted (the valid-series space is unrestricted).",
            artefact=artefact,
            severity=ReviewSeverity.INFO,
        )
        return None

    defaulted = [d for d in ordered_dim_ids if uses_default.get(d)]
    if defaulted:
        report.add(
            "constraint.default_item_explicit",
            "Dimensions left unassigned by some data points take the Category "
            f"default Item, made explicit in the constraint: {', '.join(defaulted)}.",
            artefact=artefact,
            severity=ReviewSeverity.INFO,
        )

    if closed:
        # Each distinct data-point key is one valid series key.
        data_keys = []
        for key in keys:
            values = [
                DataKeyValue(id=dim_id, value=key[dim_id])
                for dim_id in ordered_dim_ids
                if dim_id in key
            ]
            if values:
                data_keys.append(DataKey(keys_values=tuple(values)))
        if not data_keys:
            return None
        report.add(
            "constraint.datakeyset",
            f"Closed table: emitted {len(data_keys)} series key(s) as a DataKeySet "
            "(each data point is an explicit series).",
            artefact=artefact,
            severity=ReviewSeverity.INFO,
        )
        if datapoint_count and datapoint_count > len(data_keys):
            report.add(
                "constraint.metric_collapse",
                f"{datapoint_count} data points collapsed to {len(data_keys)} series "
                "key(s): data points differing only by metric share one SDMX series "
                "key (a Measure is not part of the key). The metric-to-key pairing is "
                "not recoverable from the constraint (gap, models-relationships §2.2.5).",
                artefact=artefact,
                severity=ReviewSeverity.REVIEW,
            )
        return _new_constraint(
            table, agency,
            key_sets=[KeySet(keys=tuple(data_keys), is_included=True)],
        )

    # Open table: describe the space dimension-wise.
    key_values = []
    for dim_id in ordered_dim_ids:
        values = []
        for key in keys:
            code = key.get(dim_id)
            if code is not None and code not in values:
                values.append(code)
        if values:
            key_values.append(
                CubeKeyValue(
                    id=dim_id,
                    values=tuple(CubeValue(value=c) for c in sorted(values)),
                )
            )
    # Append the enumerated open keys: their rows are open, but each is confined
    # to the open-axis SubCategory subset, so the constraint lists that subset.
    for dim_id, codes in open_key_values:
        key_values.append(
            CubeKeyValue(
                id=dim_id,
                values=tuple(CubeValue(value=c) for c in sorted(set(codes))),
            )
        )
    if open_key_values:
        report.add(
            "constraint.open_key_values",
            "Open-axis key dimension(s) constrained to their SubCategory subset: "
            f"{', '.join(dim_id for dim_id, _ in open_key_values)}.",
            artefact=artefact,
            severity=ReviewSeverity.INFO,
        )
    if not key_values:
        return None
    return _new_constraint(
        table, agency,
        cube_regions=[CubeRegion(key_values=tuple(key_values), is_included=True)],
    )
