"""Phase 3a tests: DPM -> SDMX data-definition layer (DSD + Dataflow)."""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from wp_sdmx_dpm.config import Conventions, ReviewReport
from wp_sdmx_dpm.mapping import data_definition as DD

DB_PATH = Path(__file__).resolve().parents[1] / "input" / "dpm_4.2.1_20260606.db"
requires_db = pytest.mark.skipif(not DB_PATH.exists(), reason="input DPM DB not present")


def _dim_prop(code, category_code):
    return {"code": code, "label": code, "isMetric": False, "isEnumerated": True,
            "dataType": {"code": "e"}, "enumeration": {"categoryCode": category_code}}


def _metric_prop(code, dt="m"):
    return {"code": code, "label": code, "isMetric": True, "isEnumerated": False,
            "dataType": {"code": dt}, "enumeration": None}


def test_table_to_dsd_builds_dimensions_and_measures():
    report = ReviewReport()
    built = DD.table_to_dsd_and_dataflow(
        {"code": "C_26.00", "name": "LE1"},
        [_dim_prop("qBLT", "NC")],
        [_metric_prop("mi1"), _metric_prop("mi2")],
        conceptscheme_id="CS_COREP", agency="EBA", module_code="COREP_LE",
        conventions=Conventions(), report=report,
    )
    assert built is not None
    dsd, dataflow = built
    assert dsd.id == "DSD_C_26_00"
    assert len(dsd.components.dimensions) == 1
    assert len(dsd.components.measures) == 2
    # dimension references its concept and codelist
    dim = dsd.components.dimensions[0]
    assert dim.concept.item_id == "qBLT" and dim.concept.id == "CS_COREP"
    assert dim.local_codes is not None and dim.local_codes.id == "NC"
    # dataflow links the DSD and records the module
    assert dataflow.id == "C_26_00" and dataflow.structure == dsd.short_urn
    assert any(a.type == "DPM_MODULE" and a.text == "COREP_LE" for a in dataflow.annotations)


def test_table_with_no_dimensions_is_skipped_and_flagged():
    report = ReviewReport()
    built = DD.table_to_dsd_and_dataflow(
        {"code": "C_00.01", "name": "cover"},
        [], [_metric_prop("mi1")],
        conceptscheme_id="CS_COREP", agency="EBA", module_code="COREP_LE",
        conventions=Conventions(), report=report,
    )
    assert built is None
    assert any(f.code == "dsd.no_dimensions" for f in report.flags)


@requires_db
def test_read_table_components(tmp_path):
    from wp_sdmx_dpm.dpm.reader import DpmReader

    with DpmReader(str(DB_PATH)) as reader:
        module = reader.read_module("COREP_LE")
        # C_28.00 is a rich table: many context dimensions + metrics
        by_code = {t["code"]: t for t in module["tables"]}
        dim, metric = reader.read_table_components(by_code["C_28.00"]["tableVersionId"])
    assert len(dim) > 5 and len(metric) > 0
    assert not (set(dim) & set(metric))  # a context dim is never also a measure


@requires_db
def test_convert_corep_le_data_def_validates():
    from pysdmx.io import read_sdmx
    from pysdmx.model.dataflow import DataStructureDefinition, Dataflow

    from wp_sdmx_dpm.convert.dpm_to_sdmx import convert_module
    from wp_sdmx_dpm.sdmx.serializer import partition_stages, serialize

    res = convert_module(str(DB_PATH), "COREP_LE", layers=["glossary", "data-def"])
    dsds = [o for o in res.objects if isinstance(o, DataStructureDefinition)]
    dfs = [o for o in res.objects if isinstance(o, Dataflow)]
    assert dsds and len(dsds) == len(dfs)

    # every component's concept ref must resolve to a built concept
    from pysdmx.model import ConceptScheme
    concept_ids = {c.id for cs in res.objects if isinstance(cs, ConceptScheme) for c in cs.items}
    for dsd in dsds:
        for comp in dsd.components:
            assert comp.concept.item_id in concept_ids

    # serialised structure passes pysdmx schema validation (per dependency tier;
    # the hierarchies tier uses the in-house writer, not pysdmx)
    for label, objects in partition_stages(res.objects):
        if not objects:
            continue
        xml = serialize(objects, "sdmx-ml")
        if label != "hierarchies":
            assert read_sdmx(io.BytesIO(xml.encode())) is not None
