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

from pysdmx.model import Annotation, Code, Codelist, Concept, Facets
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
# Authoritative proposal: docs/transformation-guidelines/05_data_types_mapping.md.
# DPM codes (from query_datatypes): m monetary, r decimal, i integer,
# p percentage, b boolean, t true, d date, dt date-time, s string (non-empty),
# es string (incl. empty), e enumeration, u URI, o ordinals.
_DATATYPE_MAP: Dict[str, DataType] = {
    "i": DataType.INTEGER,
    "r": DataType.DECIMAL,
    "m": DataType.DECIMAL,    # monetary -> decimal (semantic distinction lost; flagged)
    "p": DataType.DECIMAL,    # percentage -> decimal (no native % type; flagged)
    "o": DataType.INTEGER,    # ordinals -> integer (ordering lost; flagged)
    "s": DataType.STRING,
    "es": DataType.STRING,    # empty-string distinction not expressible in SDMX
    "e": DataType.STRING,     # enumeration scalar fallback (codes carried separately)
    "u": DataType.URI,
    "b": DataType.BOOLEAN,
    "t": DataType.BOOLEAN,    # "true" is a boolean subtype
    "d": DataType.DATE,       # GregorianDay (ISO date)
    "dt": DataType.DATE_TIME,
}

# DPM data type codes whose SDMX mapping is lossy -> the review message to emit.
_LOSSY_DATATYPES: Dict[str, str] = {
    "m": "DPM 'monetary' has no SDMX equivalent; mapped to Decimal (unit/currency lost)",
    "p": "DPM 'percentage' has no SDMX equivalent; mapped to Decimal (% semantics lost)",
    "o": "DPM 'ordinals' has no SDMX equivalent; mapped to Integer (ordering lost)",
}


# Reverse of _DATATYPE_MAP: SDMX DataType -> a representative DPM datatype code.
# Keys are the SDMX DataType *values* (DataType.X.value). DPM has finer numeric
# and temporal types, so several SDMX types collapse onto the closest DPM code.
_SDMX_TO_DPM_DATATYPE: Dict[str, str] = {
    DataType.INTEGER.value: "i",
    DataType.LONG.value: "i",
    DataType.SHORT.value: "i",
    DataType.COUNT.value: "i",
    DataType.DECIMAL.value: "r",
    DataType.FLOAT.value: "r",
    DataType.DOUBLE.value: "r",
    DataType.NUMERIC.value: "r",
    DataType.BOOLEAN.value: "b",
    DataType.DATE.value: "d",                 # GregorianDay
    DataType.DATE_TIME.value: "dt",
    DataType.PERIOD.value: "d",               # ObservationalTimePeriod -> Date
    DataType.BASIC_TIME_PERIOD.value: "d",
    DataType.STRING.value: "es",
    DataType.URI.value: "u",
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
        if code in _LOSSY_DATATYPES:
            report.add(
                "datatype.lossy",
                _LOSSY_DATATYPES[code],
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


def _codelist_ref(agency: str, category_code: str, version: str = "1.0") -> Codelist:
    """A lightweight Codelist reference (id/agency/version only).

    Used as the Concept's enumerated CoreRepresentation: the SDMX-ML writer reads
    only ``short_urn`` from it, so the full code set is not duplicated here.
    """
    return Codelist(id=normalise_sdmx_id(category_code), agency=agency, version=version)


def _facets_for(prop: Dict[str, Any]) -> Optional[Facets]:
    """Map DPM Property facet-like attributes to SDMX Facets (ValueLength -> maxLength)."""
    value_length = prop.get("valueLength")
    if value_length:
        return Facets(max_length=int(value_length))
    return None


def property_to_concept(
    prop: Dict[str, Any], conventions: Conventions, report: ReviewReport
) -> Concept:
    """Map a DPM Property dict to an SDMX Concept with a CoreRepresentation.

    Enumerated properties get an enumerated representation (``codes`` referencing
    the Codelist built from their category); non-enumerated properties get a
    scalar representation (``dtype`` per the data-type mapping, plus ``facets``).
    Both ``codes`` and ``enum_ref`` are set for the enumerated case: ``codes``
    drives SDMX-ML serialisation, ``enum_ref`` carries the URN for URN-based
    tooling and the SDMX->DPM round trip.
    """
    code = prop["code"]
    artefact = f"Property:{code}"
    anns = _annotations(
        code_annotation(code),
        {"type": ANN_DPM_SIGNATURE, "text": prop["signature"]} if prop.get("signature") else None,
        {"type": ANN_DPM_PERIOD_TYPE, "text": prop["periodType"]} if prop.get("periodType") else None,
    )

    enum_ref = None
    codes: Optional[Codelist] = None
    dtype: Optional[DataType] = None
    facets: Optional[Facets] = None
    enumeration = prop.get("enumeration")
    if prop.get("isEnumerated") and enumeration and enumeration.get("categoryCode"):
        agency = conventions.agency_for(prop.get("owner"))
        category_id = normalise_sdmx_id(enumeration["categoryCode"])
        codes = _codelist_ref(agency, enumeration["categoryCode"])
        enum_ref = _codelist_urn(agency, category_id)
    else:
        dtype = map_datatype(prop.get("dataType"), report, artefact=artefact)
        facets = _facets_for(prop)

    return Concept(
        id=normalise_sdmx_id(code),
        name=prop.get("label"),
        description=prop.get("description"),
        dtype=dtype,
        facets=facets,
        codes=codes,
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
