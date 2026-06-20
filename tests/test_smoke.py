"""Phase 1 smoke tests: libraries import, input DB loads, scaffolding wires up.

The DB test is skipped automatically if the (gitignored, ~400MB) input DB is
absent, so the suite still runs in a clean checkout.
"""

from __future__ import annotations

from pathlib import Path

import pytest

DB_PATH = Path(__file__).resolve().parents[1] / "input" / "dpm_4.2.1_20260606.db"
requires_db = pytest.mark.skipif(not DB_PATH.exists(), reason="input DPM DB not present")


def test_imports():
    import pysdmx  # noqa: F401
    import dpmcore  # noqa: F401
    from wp_sdmx_dpm import config, ids  # noqa: F401


def test_ids_roundtrip():
    from wp_sdmx_dpm import ids

    assert ids.normalise_sdmx_id("C_00.01") == "C_00_01"
    # ids must start with a letter: leading digit / underscore get an "X" prefix
    assert ids.normalise_sdmx_id("0010") == "X0010"
    assert ids.normalise_sdmx_id("_PR") == "X_PR"
    assert ids.is_valid_sdmx_id("C_00_01")
    assert not ids.is_valid_sdmx_id("C_00.01")
    assert not ids.is_valid_sdmx_id("_PR")
    ann = ids.code_annotation("C_00.01")
    assert ann and ann["text"] == "C_00.01"
    assert ids.code_annotation("ALREADY_OK") is None


def test_review_report():
    from wp_sdmx_dpm.config import ReviewReport, ReviewSeverity

    r = ReviewReport()
    r.add("ismetric.ambiguous", "could not infer", severity=ReviewSeverity.BLOCKING)
    assert r.has_blocking
    assert r.to_dict()["count"] == 1


def test_serializer_roundtrip(tmp_path):
    """A trivial Codelist serialises to SDMX-ML and re-reads."""
    from pysdmx.io import read_sdmx
    from pysdmx.model import Code, Codelist

    from wp_sdmx_dpm.sdmx.serializer import serialize

    cl = Codelist(
        id="CL_TEST",
        name="Test",
        agency="EBA",
        version="1.0",
        items=[Code(id="ES", name="Spain"), Code(id="FR", name="France")],
    )
    out = tmp_path / "cl.xml"
    serialize([cl], "sdmx-ml", str(out))
    assert out.exists() and out.stat().st_size > 0
    msg = read_sdmx(out)
    assert msg is not None


@requires_db
def test_read_corep_le():
    from wp_sdmx_dpm.dpm.reader import DpmReader

    with DpmReader(str(DB_PATH)) as reader:
        module = reader.read_module("COREP_LE")
    assert module["code"] == "COREP_LE"
    assert module["owner"]
    assert len(module["tables"]) >= 1
    table = module["tables"][0]
    for key in ("headers", "cells", "factVariables", "isFlat"):
        assert key in table
