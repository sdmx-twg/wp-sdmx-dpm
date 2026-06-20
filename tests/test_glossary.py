"""Phase 2 tests: glossary-layer mapping, both directions."""

from __future__ import annotations

from pathlib import Path

import pytest

from wp_sdmx_dpm.config import Conventions, ReviewReport, ReviewSeverity
from wp_sdmx_dpm.mapping import glossary as G

DB_PATH = Path(__file__).resolve().parents[1] / "input" / "dpm_4.2.1_20260606.db"
requires_db = pytest.mark.skipif(not DB_PATH.exists(), reason="input DPM DB not present")


def _conv():
    return Conventions()


def test_category_codelist_roundtrip():
    report = ReviewReport()
    conv = _conv()
    category = {
        "code": "C_00.01",  # illegal SDMX id -> normalised, original kept in annotation
        "name": "Country",
        "description": "Geographic area",
        "owner": "EBA",
        "isEnumerated": True,
        "items": [
            {"code": "ES", "name": "Spain", "signature": "eba_GE:ES", "isDefaultItem": False},
            {"code": "_T", "name": "Total", "signature": "eba_GE:_T", "isDefaultItem": True},
        ],
    }
    cl = G.category_to_codelist(category, conv, report)
    assert cl.id == "C_00_01"
    assert cl.agency == "EBA"
    assert len(cl.items) == 2

    back = G.codelist_to_category(cl, conv, report)
    assert back["code"] == "C_00.01"  # recovered from DPM_CODE annotation
    codes = {it["code"]: it for it in back["items"]}
    assert codes["ES"]["signature"] == "eba_GE:ES"
    assert codes["_T"]["isDefaultItem"] is True


def test_default_item_convention_applied():
    """SDMX codelist with no default item -> _T picked by convention."""
    from pysdmx.model import Code, Codelist

    report = ReviewReport()
    cl = Codelist(
        id="CL_X", agency="EBA", version="1.0",
        items=[Code(id="ES", name="Spain"), Code(id="_T", name="Total")],
    )
    cat = G.codelist_to_category(cl, _conv(), report)
    assert {it["code"]: it["isDefaultItem"] for it in cat["items"]}["_T"] is True
    assert any(f.code == "default_item.convention" for f in report.flags)


def test_default_item_missing_is_blocking():
    from pysdmx.model import Code, Codelist

    report = ReviewReport()
    cl = Codelist(id="CL_X", agency="EBA", version="1.0", items=[Code(id="ES")])
    G.codelist_to_category(cl, _conv(), report)
    assert report.has_blocking


def test_metric_property_to_concept():
    report = ReviewReport()
    prop = {
        "code": "mi1", "signature": "mi1", "label": "Threshold", "description": None,
        "owner": "EBA", "isMetric": True, "isEnumerated": False, "periodType": "stock",
        "dataType": {"code": "m", "name": "monetary"}, "enumeration": None,
    }
    concept = G.property_to_concept(prop, _conv(), report)
    assert concept.id == "mi1"
    assert concept.dtype is not None and concept.enum_ref is None
    # period type preserved as annotation
    assert any(a.type == "DPM_PERIOD_TYPE" and a.text == "stock" for a in concept.annotations)

    back = G.concept_to_property(concept, _conv(), report)
    assert back["isMetric"] is True
    assert back["periodType"] == "stock"


def test_enumerated_property_to_concept_uses_enum_ref():
    report = ReviewReport()
    prop = {
        "code": "ei4", "signature": "ei4", "label": "Accounting standard",
        "owner": "EBA", "isMetric": False, "isEnumerated": True, "periodType": None,
        "dataType": {"code": "e", "name": "enumeration"},
        "enumeration": {"categoryCode": "AS", "items": []},
    }
    concept = G.property_to_concept(prop, _conv(), report)
    assert concept.enum_ref == "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=EBA:AS(1.0)"
    back = G.concept_to_property(concept, _conv(), report)
    assert back["isMetric"] is False and back["isEnumerated"] is True


def test_datatype_mapping_flags_unknown():
    from pysdmx.model.dataflow import DataType

    report = ReviewReport()
    assert G.map_datatype({"code": "i"}, report) is DataType.INTEGER
    assert G.map_datatype({"code": "weird"}, report) is DataType.STRING
    assert any(f.code == "datatype.unmapped" for f in report.flags)


@requires_db
def test_convert_corep_le_glossary_serialises(tmp_path):
    from pysdmx.io import read_sdmx
    from pysdmx.model import Codelist, ConceptScheme

    from wp_sdmx_dpm.convert.dpm_to_sdmx import convert_module
    from wp_sdmx_dpm.sdmx.serializer import serialize

    res = convert_module(str(DB_PATH), "COREP_LE", layers=["glossary"])
    codelists = {o.id for o in res.objects if isinstance(o, Codelist)}
    schemes = [o for o in res.objects if isinstance(o, ConceptScheme)]
    assert codelists and len(schemes) == 1
    assert not res.report.has_blocking

    # every enumerated concept must reference a codelist we actually built
    for concept in schemes[0].items:
        if concept.enum_ref:
            clid = concept.enum_ref.split("=")[1].split(":")[1].split("(")[0]
            assert clid in codelists, f"dangling enum_ref to {clid}"

    out = tmp_path / "COREP_LE.xml"
    serialize(res.objects, "sdmx-ml", str(out))
    assert read_sdmx(out) is not None
