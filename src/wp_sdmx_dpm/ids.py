"""Reversible identifier normalisation and annotation helpers.

DPM codes (e.g. ``C_00.01``, ``eba_qAS:qx2004``) routinely contain characters
that are illegal in SDMX ids, whose lexical space is ``[A-Za-z0-9_@$\\-]+``.
We normalise at the boundary and keep the original recoverable via an
annotation, so the round trip is lossless (data-instances mapping rules).
"""

from __future__ import annotations

import re
from typing import Optional

# --- annotation type constants (see detailed_mapping_rules section 2.6) ------
ANN_DPM_SIGNATURE = "DPM_SIGNATURE"          # original DPM signature, e.g. eba_qAS:qx2004
ANN_DPM_CODE = "DPM_CODE"                    # original DPM code before normalisation
ANN_DPM_DEFAULT_ITEM = "DPM_DEFAULT_ITEM"    # which Code is the DPM default Item
ANN_DPM_COMPOUND = "DPM_COMPOUND_COMPONENTS"  # decomposition of a compound item
ANN_DPM_PERIOD_TYPE = "DPM_PERIOD_TYPE"      # stock/flow, no native SDMX home

_INVALID = re.compile(r"[^A-Za-z0-9_@$\-]")


def normalise_sdmx_id(dpm_code: str) -> str:
    """Map an arbitrary DPM code to a syntactically valid SDMX id.

    SDMX (and FMR) require an id to match ``[A-Za-z][A-Za-z0-9_@$\\-]*`` -- it
    must *start with a letter*. Invalid characters are replaced with ``_``; if the
    result does not begin with a letter (e.g. the internal ``_PR``/``_TE``
    categories, or a code starting with a digit), an ``X`` is prepended.

    Pure and deterministic. The original code should be preserved alongside the
    result via :func:`code_annotation` so it can be recovered on the way back.
    """
    if dpm_code is None:
        raise ValueError("dpm_code must not be None")
    normalised = _INVALID.sub("_", dpm_code)
    if not normalised or not normalised[0].isalpha():
        normalised = "X" + normalised
    return normalised


def normalise_codelist_id(dpm_code: str) -> str:
    """Like :func:`normalise_sdmx_id`, but UPPER-CASED -- for Codelist ids only.

    FMR stores every Codelist maintainable id in upper case (e.g. ``qEC`` ->
    ``QEC``) while leaving references *to* it untouched. A lower-case id therefore
    loads (the store matches case-insensitively) but fails strict reference
    resolution at query time (``getConstrainedCodelist`` -> "Could not resolve
    reference ... Codelist"). Emitting the id upper-case -- and routing every
    reference (Concept CoreRepresentation, DSD Dimension Enumeration, Hierarchy
    Code URN) through this same function -- keeps the artefact and all references
    consistent with what FMR persists. Code ids *inside* the codelist are left
    untouched; FMR preserves those.
    """
    return normalise_sdmx_id(dpm_code).upper()


def is_valid_sdmx_id(value: str) -> bool:
    return bool(value) and _INVALID.search(value) is None and value[0].isalpha()


def code_annotation(original_code: str) -> Optional[dict]:
    """Return a DPM_CODE annotation payload iff normalisation changed the code."""
    if original_code is None:
        return None
    if normalise_sdmx_id(original_code) == original_code:
        return None
    return {"type": ANN_DPM_CODE, "text": original_code}


def codelist_code_annotation(original_code: str) -> Optional[dict]:
    """Return a DPM_CODE annotation payload iff the upper-cased codelist id differs.

    Used in place of :func:`code_annotation` for Codelists so the original DPM
    category code (e.g. ``qEC``) is recoverable even when the only change is the
    upper-casing applied by :func:`normalise_codelist_id`.
    """
    if original_code is None:
        return None
    if normalise_codelist_id(original_code) == original_code:
        return None
    return {"type": ANN_DPM_CODE, "text": original_code}


def recover_dpm_code(sdmx_id: str, annotations: Optional[dict] = None) -> str:
    """Recover the original DPM code: prefer a DPM_CODE annotation, else the id."""
    if annotations:
        original = annotations.get(ANN_DPM_CODE)
        if original:
            return original
    return sdmx_id
