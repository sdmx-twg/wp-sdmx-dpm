"""Glossary-layer mapping (spec section 01_glossary), both directions.

DPM -> SDMX
    enumerated Category  -> Codelist        (full item set; SubCategory
                                             restrictions become constraints)
    Item                 -> Code            (signature preserved as annotation)
    Property             -> Concept         (metric -> dtype+facets;
                                             enumerated -> enum_ref to Codelist)

SDMX -> DPM (pure transform to DPM-shaped dicts; DB persistence is Phase 3)
    Codelist -> Category ; Code -> Item ; Concept -> Property

The functions here are pure: they take dicts (from dpmcore) or pysdmx objects
and return the other side, recording every judgement call on a ReviewReport.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pysdmx.model import Annotation, Code, Codelist, Concept
from pysdmx.model.dataflow import DataType

from ..config import Conventions, ReviewReport, ReviewSeverity
from ..ids import (
    ANN_DPM_DEFAULT_ITEM,
    ANN_DPM_PERIOD_TYPE,
    ANN_DPM_SIGNATURE,
    code_annotation,
    normalise_sdmx_id,
)

# --- DPM DataType (by code) -> SDMX DataType --------------------------------
# DPM codes (from query_datatypes): m monetary, r decimal, i integer,
# p percentage, b boolean, t true, d date, dt date-time, es string, e
# enumeration, u URI, o ordinals.
_DATATYPE_MAP: Dict[str, DataType] = {
    "m": DataType.DECIMAL,    # monetary -> decimal (unit deferred)
    "r": DataType.DECIMAL,
    "i": DataType.INTEGER,
    "p": DataType.DECIMAL,    # percentage -> decimal (no native % type)
    "b": DataType.BOOLEAN,
    "t": DataType.BOOLEAN,    # "true" is a boolean subtype
    "d": DataType.DATE,
    "dt": DataType.DATE_TIME,
    "es": DataType.STRING,
    "s": DataType.STRING,
    "e": DataType.STRING,     # enumeration carried via enum_ref, scalar is string
    "u": DataType.URI,
    "o": DataType.STRING,     # ordinals: ordered enumeration, flagged below
}


# Reverse of _DATATYPE_MAP: SDMX DataType -> a representative DPM datatype code.
# (DPM has finer numeric types; we pick the closest single code.)
_SDMX_TO_DPM_DATATYPE: Dict[str, str] = {
    "Decimal": "r",
    "Integer": "i",
    "Boolean": "b",
    "Date": "d",
    "DateTime": "dt",
    "String": "es",
    "URI": "u",
}


def sdmx_datatype_to_dpm(dtype: Optional["DataType"]) -> str:
    """Map an SDMX DataType to a DPM datatype code (default 'es' = string)."""
    if dtype is None:
        return "es"
    return _SDMX_TO_DPM_DATATYPE.get(getattr(dtype, "value", str(dtype)), "es")


def _annotations(*payloads: Optional[Dict[str, str]]) -> List[Annotation]:
    return [Annotation(type=p["type"], text=p["text"]) for p in payloads if p]


def map_datatype(
    dpm_datatype: Optional[Dict[str, Any]],
    report: ReviewReport,
    *,
    artefact: str = "",
) -> DataType:
    """Map a DPM dataType dict ({code,name}) to an SDMX DataType."""
    code = (dpm_datatype or {}).get("code")
    if code in _DATATYPE_MAP:
        if code == "o":
            report.add(
                "datatype.ordinal",
                "DPM 'ordinals' has no SDMX equivalent; mapped to STRING",
                artefact=artefact,
                severity=ReviewSeverity.REVIEW,
            )
        return _DATATYPE_MAP[code]
    report.add(
        "datatype.unmapped",
        f"Unknown DPM dataType {code!r}; defaulted to STRING",
        artefact=artefact,
        severity=ReviewSeverity.REVIEW,
    )
    return DataType.STRING


# === DPM -> SDMX ============================================================
def _item_to_code(item: Dict[str, Any]) -> Code:
    """Map a DPM Item/SubCategoryItem dict to an SDMX Code.

    Accepts both Category.items ({id,code,name,signature,isDefaultItem}) and the
    enumeration.items shape ({itemId,code,name,signature,isDefaultItem}).
    """
    code = item["code"]
    anns = _annotations(
        code_annotation(code),
        {"type": ANN_DPM_SIGNATURE, "text": item["signature"]} if item.get("signature") else None,
        {"type": ANN_DPM_DEFAULT_ITEM, "text": "true"} if item.get("isDefaultItem") else None,
    )
    return Code(
        id=normalise_sdmx_id(code),
        name=item.get("name"),
        description=item.get("description"),
        annotations=tuple(anns),
    )


def category_to_codelist(
    category: Dict[str, Any], conventions: Conventions, report: ReviewReport
) -> Codelist:
    """Map an enumerated DPM Category dict to an SDMX Codelist."""
    code = category["code"]
    items = [_item_to_code(it) for it in (category.get("items") or [])]
    return Codelist(
        id=normalise_sdmx_id(code),
        name=category.get("name"),
        description=category.get("description"),
        agency=conventions.agency_for(category.get("owner")),
        version="1.0",
        items=items,
        annotations=tuple(_annotations(code_annotation(code))),
    )


def _codelist_urn(agency: str, codelist_id: str, version: str = "1.0") -> str:
    return f"urn:sdmx:org.sdmx.infomodel.codelist.Codelist={agency}:{codelist_id}({version})"


def property_to_concept(
    prop: Dict[str, Any], conventions: Conventions, report: ReviewReport
) -> Concept:
    """Map a DPM Property dict to an SDMX Concept.

    Enumerated properties get an ``enum_ref`` to the Codelist built from their
    category; non-enumerated properties get a scalar ``dtype``.
    """
    code = prop["code"]
    artefact = f"Property:{code}"
    anns = _annotations(
        code_annotation(code),
        {"type": ANN_DPM_SIGNATURE, "text": prop["signature"]} if prop.get("signature") else None,
        {"type": ANN_DPM_PERIOD_TYPE, "text": prop["periodType"]} if prop.get("periodType") else None,
    )

    enum_ref = None
    dtype: Optional[DataType] = None
    enumeration = prop.get("enumeration")
    if prop.get("isEnumerated") and enumeration and enumeration.get("categoryCode"):
        agency = conventions.agency_for(prop.get("owner"))
        enum_ref = _codelist_urn(agency, normalise_sdmx_id(enumeration["categoryCode"]))
    else:
        dtype = map_datatype(prop.get("dataType"), report, artefact=artefact)

    return Concept(
        id=normalise_sdmx_id(code),
        name=prop.get("label"),
        description=prop.get("description"),
        dtype=dtype,
        enum_ref=enum_ref,
        annotations=tuple(anns),
    )


# === SDMX -> DPM (pure transform; persistence in Phase 3) ===================
def codelist_to_category(
    codelist: Codelist, conventions: Conventions, report: ReviewReport
) -> Dict[str, Any]:
    """Map an SDMX Codelist to a DPM Category dict (ready for DpmWriter)."""
    ann = {a.type: a.text for a in (codelist.annotations or [])}
    items = []
    for code in codelist.items or []:
        cann = {a.type: a.text for a in (code.annotations or [])}
        items.append(
            {
                "code": cann.get("DPM_CODE", code.id),
                "name": code.name,
                "description": code.description,
                "signature": cann.get(ANN_DPM_SIGNATURE),
                "isDefaultItem": cann.get(ANN_DPM_DEFAULT_ITEM) == "true",
            }
        )
    if items and not any(it["isDefaultItem"] for it in items):
        _pick_default_item(items, conventions, report, artefact=f"Codelist:{codelist.id}")
    return {
        "code": ann.get("DPM_CODE", codelist.id),
        "name": codelist.name,
        "description": codelist.description,
        "owner": conventions.owner_for(codelist.agency),
        "isEnumerated": True,
        "items": items,
    }


def _pick_default_item(
    items: List[Dict[str, Any]],
    conventions: Conventions,
    report: ReviewReport,
    *,
    artefact: str,
) -> None:
    """DPM Categories need a default Item; SDMX has none. Apply the convention."""
    by_code = {it["code"]: it for it in items}
    for candidate in conventions.default_item_candidates:
        if candidate in by_code:
            by_code[candidate]["isDefaultItem"] = True
            report.add(
                "default_item.convention",
                f"Selected default Item {candidate!r} by convention",
                artefact=artefact,
                severity=ReviewSeverity.INFO,
            )
            return
    report.add(
        "default_item.missing",
        "No default Item found and none could be inferred; one must be chosen",
        artefact=artefact,
        severity=ReviewSeverity.BLOCKING,
    )


def concept_to_property(
    concept: Concept,
    conventions: Conventions,
    report: ReviewReport,
    *,
    is_metric_hint: Optional[bool] = None,
) -> Dict[str, Any]:
    """Map an SDMX Concept to a DPM Property dict (ready for DpmWriter).

    IsMetric derivation: when the Concept is used by a DSD component, the
    component role is authoritative -- pass it via ``is_metric_hint`` (Measure ->
    True, Dimension/Attribute -> False). Otherwise infer (enumerated ->
    dimension; scalar numeric -> metric; else the configured default + a flag).
    """
    ann = {a.type: a.text for a in (concept.annotations or [])}
    artefact = f"Concept:{concept.id}"
    is_enumerated = concept.enum_ref is not None or concept.codes is not None
    numeric = {
        DataType.DECIMAL, DataType.INTEGER, DataType.DOUBLE, DataType.FLOAT,
        DataType.LONG, DataType.SHORT, DataType.NUMERIC, DataType.COUNT,
        DataType.BIG_INTEGER,
    }
    if is_metric_hint is not None:
        is_metric = is_metric_hint
    elif is_enumerated:
        is_metric = False
    elif concept.dtype in numeric:
        is_metric = True
    else:
        is_metric = conventions.ismetric_default_when_ambiguous
        report.add(
            "ismetric.ambiguous",
            f"Could not infer IsMetric for {concept.id!r}; defaulted to {is_metric}",
            artefact=artefact,
            severity=ReviewSeverity.REVIEW,
        )
    category_code = None
    if concept.enum_ref:
        # enum_ref urn: ...Codelist=AGENCY:CLID(version)
        category_code = concept.enum_ref.split("=")[1].split(":")[1].split("(")[0]
    elif concept.codes is not None:
        category_code = concept.codes.id
    return {
        "code": ann.get("DPM_CODE", concept.id),
        "signature": ann.get(ANN_DPM_SIGNATURE),
        "label": concept.name,
        "description": concept.description,
        "isMetric": is_metric,
        "isEnumerated": is_enumerated,
        "categoryCode": category_code,
        "dataTypeCode": sdmx_datatype_to_dpm(concept.dtype),
        "periodType": ann.get(ANN_DPM_PERIOD_TYPE),
        "owner": conventions.owner_for(getattr(concept, "agency", None)),
    }
