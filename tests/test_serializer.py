"""Tests for SDMX-ML version selection and agency bundling (FMR-loadability)."""

from __future__ import annotations

import pytest

from wp_sdmx_dpm.config import Conventions, ReviewReport
from wp_sdmx_dpm.sdmx.builder import SdmxBuilder
from wp_sdmx_dpm.sdmx.serializer import (
    DEFAULT_SDMX_VERSION,
    partition_messages,
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


def test_partition_messages_splits_vocabulary_from_structures():
    builder = SdmxBuilder(Conventions(), ReviewReport())
    agency = builder.build_agency_scheme(["EBA"])
    cl = Codelist(id="CL", name="cl", agency="EBA", version="1.0")
    cs = ConceptScheme(id="CS", name="cs", agency="EBA", version="1.0")
    dsd = DataStructureDefinition(id="DSD", name="dsd", agency="EBA", version="1.0",
                                  components=[])
    df = Dataflow(id="DF", name="df", agency="EBA", version="1.0")

    vocabulary, structures = partition_messages([agency, df, cl, cs, dsd])

    assert agency in vocabulary and cl in vocabulary and cs in vocabulary
    assert dsd in structures and df in structures
    # Order within each group is preserved (df precedes dsd in the input).
    assert structures == [df, dsd]
