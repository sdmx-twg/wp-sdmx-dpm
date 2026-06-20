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
    # `codes` is what the SDMX-ML writer serialises into <Enumeration>; it must be set.
    assert concept.codes is not None and concept.codes.id == "AS"
    assert concept.codes.short_urn == "Codelist=EBA:AS(1.0)"
    back = G.concept_to_property(concept, _conv(), report)
    assert back["isMetric"] is False and back["isEnumerated"] is True


def test_enumerated_concept_serialises_enumeration():
    """Regression: the enumerated CoreRepresentation must reach the SDMX-ML output."""
    from pysdmx.model import ConceptScheme

    from wp_sdmx_dpm.sdmx.serializer import serialize

    prop = {
        "code": "ei4", "signature": "ei4", "label": "Accounting standard",
        "owner": "EBA", "isMetric": False, "isEnumerated": True, "periodType": None,
        "dataType": {"code": "e"}, "enumeration": {"categoryCode": "AS", "items": []},
    }
    concept = G.property_to_concept(prop, _conv(), ReviewReport())
    cs = ConceptScheme(id="CS_EBA", name="EBA Concepts", agency="EBA", version="1.0",
                       items=[concept])
    xml = serialize([cs], "sdmx-ml")
    assert "<str:CoreRepresentation>" in xml
    assert "Codelist=EBA:AS(1.0)" in xml


def test_open_property_maxlength_facet():
    prop = {
        "code": "si615", "signature": "si615", "label": "Identifier",
        "owner": "EBA", "isMetric": False, "isEnumerated": False,
        "dataType": {"code": "s"}, "enumeration": None, "valueLength": 255,
    }
    concept = G.property_to_concept(prop, _conv(), ReviewReport())
    assert concept.facets is not None and concept.facets.max_length == 255


def _sample_hierarchy_subcategory():
    # x0 (root) -> {AL, AT}; AT -> ATsub. Codes resolve against the GA codelist.
    return {
        "code": "GA5",
        "name": "EU geographies",
        "description": None,
        "categoryCode": "GA",
        "items": [
            {"code": "x0", "parentCode": None, "name": "All areas"},
            {"code": "AL", "parentCode": "x0", "name": "Albania"},
            {"code": "AT", "parentCode": "x0", "name": "Austria"},
            {"code": "ATsub", "parentCode": "AT", "name": "Austria region"},
        ],
    }


def test_subcategory_to_hierarchy_builds_tree():
    h = G.subcategory_to_hierarchy(
        _sample_hierarchy_subcategory(), agency="EBA", conventions=_conv(),
        report=ReviewReport(),
    )
    assert h.id == "GA5" and h.agency == "EBA" and h.name == "EU geographies"
    assert [c.id for c in h.codes] == ["x0"]            # single root
    root = h.codes[0]
    assert root.urn == "urn:sdmx:org.sdmx.infomodel.codelist.Code=EBA:GA(1.0).x0"
    assert {c.id for c in root.codes} == {"AL", "AT"}   # two children
    at = next(c for c in root.codes if c.id == "AT")
    assert [c.id for c in at.codes] == ["ATsub"]        # nested grandchild


def test_hierarchy_serialises_and_references_codes():
    from wp_sdmx_dpm.sdmx.serializer import serialize

    h = G.subcategory_to_hierarchy(
        _sample_hierarchy_subcategory(), agency="EBA", conventions=_conv(),
        report=ReviewReport(),
    )
    xml = serialize([h], "sdmx-ml")
    assert '<str:Hierarchy id="GA5"' in xml
    assert 'hasFormalLevels="false"' in xml
    assert '<str:HierarchicalCode id="x0">' in xml
    assert "<str:Code>urn:sdmx:org.sdmx.infomodel.codelist.Code=EBA:GA(1.0).AL</str:Code>" in xml
    # mixing a hierarchy with other artefacts in one message is rejected
    from pysdmx.model import Codelist
    with pytest.raises(ValueError):
        serialize([h, Codelist(id="X", name="x", agency="EBA", version="1.0")], "sdmx-ml")


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
    from wp_sdmx_dpm.sdmx.serializer import partition_stages, serialize

    res = convert_module(str(DB_PATH), "COREP_LE", layers=["glossary"])
    codelists = {o.id for o in res.objects if isinstance(o, Codelist)}
    schemes = [o for o in res.objects if isinstance(o, ConceptScheme)]
    assert codelists and len(schemes) == 1
    # one ConceptScheme per agency, named by convention CS_<AGENCY>
    assert schemes[0].id == "CS_EBA"
    assert not res.report.has_blocking

    # every enumerated concept must reference a codelist we actually built
    for concept in schemes[0].items:
        if concept.enum_ref:
            clid = concept.enum_ref.split("=")[1].split(":")[1].split("(")[0]
            assert clid in codelists, f"dangling enum_ref to {clid}"

    # Hierarchies must be serialised in their own tier (pysdmx can't write them
    # alongside other artefacts), so serialise per dependency tier as the CLI does.
    for label, objects in partition_stages(res.objects):
        if not objects:
            continue
        out = tmp_path / f"COREP_LE.{label}.xml"
        serialize(objects, "sdmx-ml", str(out))
        if label != "hierarchies":
            assert read_sdmx(out) is not None
