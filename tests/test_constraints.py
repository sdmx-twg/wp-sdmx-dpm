"""Phase 4 tests: DPM -> SDMX constraint layer (Variables -> DataConstraint).

Closed tables (no open axes) -> DataKeySet (enumerated series keys); open tables
-> CubeRegion (per-dimension value lists). A dimension a data point leaves
unassigned takes the Category default Item, made explicit either way.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from wp_sdmx_dpm.config import Conventions, ReviewReport
from wp_sdmx_dpm.mapping import constraints as CN

DB_PATH = Path(__file__).resolve().parents[1] / "input" / "dpm_4.2.1_20260606.db"
requires_db = pytest.mark.skipif(not DB_PATH.exists(), reason="input DPM DB not present")


def test_open_table_builds_cube_region_with_explicit_default():
    report = ReviewReport()
    constraint = CN.table_to_content_constraint(
        {"code": "C_28.00", "name": "Concentration"},
        ["qFI", "qSR"],
        keys=[{"qFI": "qx2006", "qSR": "qx2011"}, {"qFI": "qx0", "qSR": "qx2011"}],
        uses_default={"qFI": True, "qSR": False},
        closed=False, agency="EBA", conventions=Conventions(), report=report,
    )
    assert constraint is not None
    assert constraint.id == "C_28_00_CONSTRAINTS" and constraint.agency == "EBA"
    assert constraint.constraint_attachment.dataflows == (
        "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=EBA:C_28_00(1.0)",
    )
    assert not constraint.key_sets  # open -> CubeRegion, not a DataKeySet
    region = constraint.cube_regions[0]
    by_dim = {kv.id: sorted(v.value for v in kv.values) for kv in region.key_values}
    assert by_dim == {"qFI": ["qx0", "qx2006"], "qSR": ["qx2011"]}
    assert any(f.code == "constraint.default_item_explicit" for f in report.flags)


def test_closed_table_builds_data_key_set():
    report = ReviewReport()
    constraint = CN.table_to_content_constraint(
        {"code": "C_26.00", "name": "Limits"},
        ["qEBF"],
        keys=[{"qEBF": "qx0"}, {"qEBF": "qx2011"}],
        uses_default={"qEBF": True},
        closed=True, agency="EBA", conventions=Conventions(), report=report,
        datapoint_count=4,  # 4 data points -> 2 series keys (metric collapse)
    )
    assert constraint is not None
    assert not constraint.cube_regions  # closed -> DataKeySet, not a CubeRegion
    keyset = constraint.key_sets[0]
    keys = [
        {kv.id: kv.value for kv in k.keys_values} for k in keyset.keys
    ]
    assert {"qEBF": "qx0"} in keys and {"qEBF": "qx2011"} in keys
    assert any(f.code == "constraint.datakeyset" for f in report.flags)
    # Data points differing only by metric collapse -> flagged as a gap (§2.2.5).
    assert any(f.code == "constraint.metric_collapse" for f in report.flags)


def test_no_keys_yields_no_constraint():
    report = ReviewReport()
    constraint = CN.table_to_content_constraint(
        {"code": "C_00.01", "name": "cover"}, [], keys=[], uses_default={},
        closed=True, agency="EBA", conventions=Conventions(), report=report,
    )
    assert constraint is None
    assert any(f.code == "constraint.empty" for f in report.flags)


@requires_db
def test_read_constraint_values_fills_default_for_contextless_datapoints():
    from wp_sdmx_dpm.dpm.reader import DpmReader

    with DpmReader(str(DB_PATH)) as reader:
        module = reader.read_module("COREP_LE")
        by_code = {t["code"]: t for t in module["tables"]}
        # C_26.00: closed, 4 data points, 3 context-less (qEBF defaults to qx0),
        # 1 pins qEBF -> two distinct series keys.
        tv = by_code["C_26.00"]["tableVersionId"]
        dim_pids, _ = reader.read_table_components(tv)
        cv = reader.read_table_constraint_values(tv, dim_pids)
    (qebf,) = dim_pids
    assert cv["usesDefault"][qebf] is True
    default = cv["dims"][qebf]["defaultItemCode"]
    codes = {next(iter(k.values())) for k in cv["keys"]}
    assert default in codes and len(cv["keys"]) == 2


@requires_db
def test_convert_corep_le_constraints_closed_vs_open_and_validate():
    import re

    from pysdmx.io import read_sdmx
    from pysdmx.model.constraint import DataConstraint
    from pysdmx.model.dataflow import DataStructureDefinition, Dataflow

    from wp_sdmx_dpm.convert.dpm_to_sdmx import convert_module
    from wp_sdmx_dpm.sdmx.serializer import partition_stages, serialize

    res = convert_module(str(DB_PATH), "COREP_LE")  # default layers incl. constraints
    constraints = {
        cn.id: cn for cn in res.objects if isinstance(cn, DataConstraint)
    }
    dataflows = {o.id for o in res.objects if isinstance(o, Dataflow)}
    dims_by_df = {
        dsd.id.replace("DSD_", "", 1): {c.id for c in dsd.components.dimensions}
        for dsd in res.objects if isinstance(dsd, DataStructureDefinition)
    }
    assert constraints

    # C_26.00 is a closed table -> DataKeySet (series keys), incl. the default qx0.
    c26 = constraints["C_26_00_CONSTRAINTS"]
    assert c26.key_sets and not c26.cube_regions
    keyed = {kv.value for k in c26.key_sets[0].keys for kv in k.keys_values}
    assert "qx0" in keyed and "qx2011" in keyed

    # C_28.00 is open (HasOpenRows) -> CubeRegion.
    c28 = constraints["C_28_00_CONSTRAINTS"]
    assert c28.cube_regions and not c28.key_sets

    # Every constraint attaches to a present Dataflow; every component id is a
    # Dimension of that Dataflow's DSD (whether in a CubeRegion or a DataKeySet).
    for cn in constraints.values():
        df_id = re.search(
            r"Dataflow=EBA:([^(]+)\(", cn.constraint_attachment.dataflows[0]
        ).group(1)
        assert df_id in dataflows
        ids = {kv.id for r in cn.cube_regions for kv in r.key_values}
        ids |= {kv.id for ks in cn.key_sets for k in ks.keys for kv in k.keys_values}
        assert ids and ids <= dims_by_df[df_id]

    # The constraints tier serialises and passes pysdmx schema validation.
    tiers = dict(partition_stages(res.objects))
    xml = serialize(tiers["constraints"], "sdmx-ml")
    assert read_sdmx(io.BytesIO(xml.encode())) is not None
