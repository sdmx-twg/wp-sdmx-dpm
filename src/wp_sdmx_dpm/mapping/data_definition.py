"""Data-definition-layer mapping (spec section 02_data_definition).

DPM -> SDMX (this module; the user's primary direction)
    Table  -> DataStructureDefinition + Dataflow
    dimension Property (from FactVariable Contexts) -> Dimension
    metric Property (IsMetric)                      -> Measure
    Module -> (annotation on each Dataflow; pysdmx has no ReportingTaxonomy)

For the EBA reality (non-flat tables, isFlat=FALSE) the DSD dimensions are
reconstructed from the union of the table's FactVariable Contexts -- the
(Property, Item) pairs that fix each data point -- per spec section 3.2.7. Each
distinct context Property becomes one Dimension (one-to-one); each distinct
metric Property becomes one Measure.

The SDMX -> DPM (flat-table) direction and the DpmWriter that persists it are
the next slice (Phase 3b).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from pysdmx.model import Annotation
from pysdmx.model import Codelist as _CodelistRef
from pysdmx.model.dataflow import (
    Component,
    Components,
    Dataflow,
    DataStructureDefinition,
    ItemReference,
    Role,
)

from ..config import Conventions, ReviewReport, ReviewSeverity
from ..ids import normalise_codelist_id, normalise_sdmx_id
from .glossary import map_datatype

ANN_DPM_MODULE = "DPM_MODULE"


def _concept_ref(conceptscheme_id: str, agency: str, prop_code: str) -> ItemReference:
    return ItemReference(
        sdmx_type="Concept",
        agency=agency,
        id=normalise_sdmx_id(conceptscheme_id),
        version="1.0",
        item_id=normalise_sdmx_id(prop_code),
    )


def _codelist_ref(agency: str, category_code: str) -> _CodelistRef:
    # Lightweight reference: the writer only needs short_urn (agency:id(version)).
    # Codelist ids are upper-cased to match how FMR persists them (see ids.py).
    return _CodelistRef(id=normalise_codelist_id(category_code), agency=agency, version="1.0")


def _component_from_property(
    prop: Dict[str, Any],
    role: Role,
    conceptscheme_id: str,
    agency: str,
    report: ReviewReport,
) -> Component:
    """Build a DSD Component (Dimension or Measure) from a DPM Property dict."""
    code = prop["code"]
    enum = prop.get("enumeration")
    local_codes = None
    local_dtype = None
    if prop.get("isEnumerated") and enum and enum.get("categoryCode"):
        local_codes = _codelist_ref(agency, enum["categoryCode"])
    else:
        local_dtype = map_datatype(prop.get("dataType"), report, artefact=f"Property:{code}")
    return Component(
        id=normalise_sdmx_id(code),
        required=(role is not Role.ATTRIBUTE),
        role=role,
        concept=_concept_ref(conceptscheme_id, agency, code),
        local_dtype=local_dtype,
        local_codes=local_codes,
        name=prop.get("label"),
    )


def table_to_dsd_and_dataflow(
    table: Dict[str, Any],
    dimension_properties: List[Dict[str, Any]],
    measure_properties: List[Dict[str, Any]],
    *,
    conceptscheme_id: str,
    agency: str,
    module_code: str,
    conventions: Conventions,
    report: ReviewReport,
) -> Optional[Tuple[DataStructureDefinition, Dataflow]]:
    """Map one DPM Table to a DSD + Dataflow (spec 3.2.3 / 3.2.7).

    Returns ``None`` (and flags) for a table that yields no dimensions: SDMX
    requires a DimensionList, so a measure-only DSD would be invalid.
    """
    table_code = table["code"]
    artefact = f"Table:{table_code}"

    dimensions = [
        _component_from_property(p, Role.DIMENSION, conceptscheme_id, agency, report)
        for p in dimension_properties
    ]
    measures = [
        _component_from_property(p, Role.MEASURE, conceptscheme_id, agency, report)
        for p in measure_properties
    ]

    if not dimensions:
        report.add(
            "dsd.no_dimensions",
            "Table yields no dimensions (e.g. a cover/info page); no valid SDMX DSD "
            "can be emitted (a DimensionList is mandatory). Skipped -- a dimension "
            "must be added by convention (e.g. reporting entity / time).",
            artefact=artefact,
            severity=ReviewSeverity.REVIEW,
        )
        return None
    if not measures:
        report.add(
            "dsd.no_measures",
            "Table yields no metric Property; DSD has no Measure.",
            artefact=artefact,
            severity=ReviewSeverity.REVIEW,
        )

    dsd_id = normalise_sdmx_id(f"DSD_{table_code}")
    dsd = DataStructureDefinition(
        id=dsd_id,
        name=table.get("name"),
        description=table.get("description"),
        agency=agency,
        version="1.0",
        components=Components(dimensions + measures),
    )
    dataflow = Dataflow(
        id=normalise_sdmx_id(table_code),
        name=table.get("name"),
        description=table.get("description"),
        agency=agency,
        version="1.0",
        structure=dsd.short_urn,
        annotations=(Annotation(type=ANN_DPM_MODULE, text=module_code),),
    )
    return dsd, dataflow


# === SDMX -> DPM (flat table; persisted by DpmWriter) =======================
_ROLE_TO_VARIABLE_TYPE = {Role.DIMENSION: "key", Role.MEASURE: "fact", Role.ATTRIBUTE: "attribute"}
_DIRECTION = "C"  # flat tables are column-oriented (spec 3.2.6 step 4)


def dsd_to_flat_table(
    dataflow: Any,
    dsd: Any,
    *,
    conventions: Conventions,
    report: ReviewReport,
) -> Dict[str, Any]:
    """Map an SDMX Dataflow+DSD to a flat DPM Table spec (spec 3.2.6).

    Returns a plain dict the :class:`DpmWriter` persists. Each DSD component
    becomes one ordered component (Header + Variable of the matching type);
    Dimensions are keys, the Measure is the fact, DataAttributes are attributes.
    The result is always a flat table (``IsFlat=TRUE``, ``HasOpenRows=TRUE``).
    """
    components: List[Dict[str, Any]] = []
    order = 0
    for comp in list(dsd.components):
        order += 10
        concept = comp.concept
        property_code = getattr(concept, "id", None) or comp.id
        category_code = comp.local_codes.id if comp.local_codes is not None else None
        if category_code is None and getattr(concept, "enum_ref", None):
            category_code = concept.enum_ref.split("=")[1].split(":")[1].split("(")[0]
        components.append(
            {
                "role": comp.role,
                "variable_type": _ROLE_TO_VARIABLE_TYPE.get(comp.role, "fact"),
                "is_key": comp.role is Role.DIMENSION,
                "is_attribute": comp.role is Role.ATTRIBUTE,
                "code": comp.id,
                "name": comp.name,
                "property_code": property_code,
                "category_code": category_code,
                "is_nullable": not comp.required,
                "order": order,
            }
        )

    table_code = dataflow.id
    return {
        "table": {
            "code": table_code,
            "name": dataflow.name,
            "description": dataflow.description,
            "is_flat": conventions.produce_flat_tables,
            "has_open_rows": True,
        },
        "components": components,
    }


def synthesise_module_spec(dataflow: Any, report: ReviewReport) -> Dict[str, Any]:
    """Synthesise the mandatory Module/ModuleVersion for a Dataflow (spec 3.4.2).

    pysdmx exposes no ReportingTaxonomy, so a Module is always synthesised here;
    a DPM_MODULE annotation on the Dataflow (if present) names it.
    """
    module_code = None
    for ann in getattr(dataflow, "annotations", None) or []:
        if ann.type == ANN_DPM_MODULE and ann.text:
            module_code = ann.text
    if module_code is None:
        module_code = f"{dataflow.id}_MODULE"
        report.add(
            "module.synthesised",
            f"No ReportingTaxonomy/DPM_MODULE; synthesised Module {module_code!r} "
            "from the Dataflow.",
            artefact=dataflow.id,
            severity=ReviewSeverity.REVIEW,
        )
    return {
        "code": module_code,
        "name": dataflow.name or module_code,
        "version_number": getattr(dataflow, "version", "1.0"),
        "framework_code": module_code,
        "framework_name": dataflow.name or module_code,
    }
