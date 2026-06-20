"""Tests for SDMX-ML version selection and agency bundling (FMR-loadability)."""

from __future__ import annotations

import pytest

from wp_sdmx_dpm.config import Conventions, ReviewReport
from wp_sdmx_dpm.sdmx.builder import SdmxBuilder
from wp_sdmx_dpm.sdmx.serializer import (
    DEFAULT_SDMX_VERSION,
    partition_stages,
    resolve_format,
    serialize,
)
from pysdmx.io.format import Format
from pysdmx.model import Codelist, ConceptScheme, DataStructureDefinition, Dataflow


def test_default_is_sdmx_ml_30():
    # FMR (12) ingests up to SDMX-ML 3.0, so 3.0 is the default dialect.
    assert DEFAULT_SDMX_VERSION == "3.0"
    assert resolve_format("sdmx-ml") is Format.STRUCTURE_SDMX_ML_3_0


def test_explicit_31_opt_in():
    assert resolve_format("sdmx-ml", "3.1") is Format.STRUCTURE_SDMX_ML_3_1


def test_unknown_version_rejected():
    with pytest.raises(ValueError):
        resolve_format("sdmx-ml", "2.1")


def test_json_ignores_version():
    assert resolve_format("json", "3.1") is Format.STRUCTURE_SDMX_JSON_2_0_0


def test_serialize_emits_30_namespace():
    builder = SdmxBuilder(Conventions(), ReviewReport())
    scheme = builder.build_agency_scheme(["EBA"])
    xml = serialize(scheme, "sdmx-ml")
    assert "/sdmxml/schemas/v3_0/" in xml
    assert "/sdmxml/schemas/v3_1/" not in xml


def test_agency_scheme_carries_named_agency():
    builder = SdmxBuilder(Conventions(), ReviewReport())
    scheme = builder.build_agency_scheme(["EBA"])
    assert scheme.id == "AGENCIES"
    assert scheme.agency == "SDMX"
    assert [a.id for a in scheme.items] == ["EBA"]
    assert scheme.items[0].name == "European Banking Authority"


def test_partition_stages_orders_by_dependency_tier():
    from pysdmx.model import Hierarchy

    builder = SdmxBuilder(Conventions(), ReviewReport())
    agency = builder.build_agency_scheme(["EBA"])
    cl = Codelist(id="CL", name="cl", agency="EBA", version="1.0")
    hier = Hierarchy(id="H", name="h", agency="EBA", version="1.0")
    cs = ConceptScheme(id="CS", name="cs", agency="EBA", version="1.0")
    dsd = DataStructureDefinition(id="DSD", name="dsd", agency="EBA", version="1.0",
                                  components=[])
    df = Dataflow(id="DF", name="df", agency="EBA", version="1.0")

    stages = partition_stages([agency, df, cl, cs, hier, dsd])
    labels = [label for label, _ in stages]
    by_label = {label: objs for label, objs in stages}

    # Tiers are returned in dependency order.
    assert labels == ["codelists", "hierarchies", "concepts", "structures"]
    # Hierarchies and concepts (which reference codelists) load AFTER codelists.
    assert labels.index("codelists") < labels.index("hierarchies") < labels.index("concepts")
    assert agency in by_label["codelists"] and cl in by_label["codelists"]
    assert hier in by_label["hierarchies"]
    assert cs in by_label["concepts"]
    # Structures tier preserves input order (df precedes dsd).
    assert by_label["structures"] == [df, dsd]
