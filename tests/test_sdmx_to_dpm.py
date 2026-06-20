"""Phase 3b tests: SDMX -> DPM flat table + DpmWriter (file source)."""

from __future__ import annotations

from pathlib import Path

import pytest

from pysdmx.io import write_sdmx
from pysdmx.io.format import Format
from pysdmx.model import Code, Codelist, Concept, ConceptScheme
from pysdmx.model.dataflow import (
    Component,
    Components,
    Dataflow,
    DataStructureDefinition,
    DataType,
    ItemReference,
    Role,
)


def _cref(item):
    return ItemReference(sdmx_type="Concept", agency="EBA", id="CS_T", version="1.0", item_id=item)


def _write_cbd2(path: str, *, area_has_total: bool = True) -> None:
    """A small flat structure: 2 dims, 1 measure, 1 attribute."""
    area_items = [Code(id="ES", name="Spain"), Code(id="FR", name="France")]
    if area_has_total:
        area_items.append(Code(id="_T", name="Total"))
    cl_freq = Codelist(id="CL_FREQ", name="Frequency", agency="EBA", version="1.0",
                       items=[Code(id="A", name="Annual"), Code(id="_T", name="Total")])
    cl_area = Codelist(id="CL_AREA", name="Area", agency="EBA", version="1.0", items=area_items)
    cs = ConceptScheme(id="CS_T", name="Concepts", agency="EBA", version="1.0", items=[
        Concept(id="FREQ", name="Frequency",
                enum_ref="urn:sdmx:org.sdmx.infomodel.codelist.Codelist=EBA:CL_FREQ(1.0)"),
        Concept(id="REF_AREA", name="Reference area",
                enum_ref="urn:sdmx:org.sdmx.infomodel.codelist.Codelist=EBA:CL_AREA(1.0)"),
        Concept(id="OBS_VALUE", name="Observation value", dtype=DataType.DECIMAL),
        Concept(id="OBS_STATUS", name="Observation status", dtype=DataType.STRING)])
    comps = [
        Component(id="FREQ", required=True, role=Role.DIMENSION, concept=_cref("FREQ"),
                  local_codes=Codelist(id="CL_FREQ", agency="EBA", version="1.0")),
        Component(id="REF_AREA", required=True, role=Role.DIMENSION, concept=_cref("REF_AREA"),
                  local_codes=Codelist(id="CL_AREA", agency="EBA", version="1.0")),
        Component(id="OBS_VALUE", required=True, role=Role.MEASURE, concept=_cref("OBS_VALUE"),
                  local_dtype=DataType.DECIMAL),
        Component(id="OBS_STATUS", required=False, role=Role.ATTRIBUTE, concept=_cref("OBS_STATUS"),
                  local_dtype=DataType.STRING, attachment_level="Observation"),
    ]
    dsd = DataStructureDefinition(id="DSD_CBD2", name="CBD2", agency="EBA", version="1.0",
                                  components=Components(comps))
    df = Dataflow(id="CBD2", name="Consolidated banking", agency="EBA", version="1.0",
                  structure=dsd.short_urn)
    write_sdmx([cl_freq, cl_area, cs, dsd, df], Format.STRUCTURE_SDMX_ML_3_1, output_path=path)


def test_sdmx_file_to_dpm_db_is_valid_and_traversable(tmp_path):
    from dpmcore import connect
    from dpmcore.server.params import ReleaseKeyword, StructureParams

    from wp_sdmx_dpm.convert.sdmx_to_dpm import convert_structure

    src = tmp_path / "cbd2.xml"
    _write_cbd2(str(src))
    out = tmp_path / "out.db"

    res = convert_structure(str(src), "EBA:CBD2(1.0)", str(out))
    assert res.is_valid is True
    assert res.tables_written == 1
    # no spurious IsMetric ambiguity: roles are authoritative
    assert not any(f.code == "ismetric.ambiguous" for f in res.report.flags)

    with connect(f"sqlite:///{out.resolve()}") as db:
        p = StructureParams(owners=["*"], ids=["*"], release=ReleaseKeyword.LATEST, release_code=None)
        mods, _ = db.services.structure.query_modules(
            params=p, detail="full", references="children", limit=10)
        assert mods, "expected at least one module"
        table = mods[0]["tables"][0]
        assert table["code"] == "CBD2"
        assert table["isFlat"] is True
        # 4 components -> 4 headers; 2 non-key (measure + attribute) -> 2 cells
        assert len(table["headers"]) == 4
        assert len(table["cells"]) == 2
        cats, _ = db.services.structure.query_categories(params=p, detail="full", limit=20)
        assert {"CL_FREQ", "CL_AREA"} <= {c["code"] for c in cats}


def test_missing_default_item_is_blocking(tmp_path):
    """A codelist with no inferable default Item raises a blocking flag."""
    from wp_sdmx_dpm.convert.sdmx_to_dpm import convert_structure

    src = tmp_path / "cbd2.xml"
    _write_cbd2(str(src), area_has_total=False)  # CL_AREA: ES/FR, no _T
    out = tmp_path / "out.db"
    res = convert_structure(str(src), "EBA:CBD2(1.0)", str(out))
    # DB is still materialised and valid, but flagged for human review
    assert res.is_valid is True
    assert any(f.code == "default_item.missing" for f in res.report.flags)
    assert res.report.has_blocking


def test_structure_ref_parsing():
    from wp_sdmx_dpm.sdmx.source import parse_structure_ref

    assert parse_structure_ref("EBA:CBD2(1.0)") == ("EBA", "CBD2", "1.0")
    assert parse_structure_ref("EBA:CBD2") == ("EBA", "CBD2", None)
    assert parse_structure_ref("CBD2") == (None, "CBD2", None)
