"""Orchestrate DPM module -> SDMX conversion (glossary -> data def -> constraints)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from ..config import Conventions, ReviewReport, ReviewSeverity
from ..dpm.reader import DpmReader
from ..sdmx.builder import SdmxBuilder

ALL_LAYERS = ["glossary", "data-def", "constraints"]


@dataclass
class DpmToSdmxResult:
    objects: List[Any] = field(default_factory=list)
    report: ReviewReport = field(default_factory=ReviewReport)


def _category_codes_for(properties: List[Dict[str, Any]]) -> Set[str]:
    """Enumerated properties reference a Category that must become a Codelist."""
    codes: Set[str] = set()
    for prop in properties:
        enum = prop.get("enumeration")
        if prop.get("isEnumerated") and enum and enum.get("categoryCode"):
            codes.add(enum["categoryCode"])
    return codes


def convert_module(
    db_path: str,
    module_code: str,
    *,
    release_code: Optional[str] = None,
    conventions: Optional[Conventions] = None,
    layers: Optional[List[str]] = None,
    include_agency: bool = True,
) -> DpmToSdmxResult:
    """Read ``module_code`` from ``db_path`` and build SDMX structures.

    ``layers`` selects which spec layers to emit (default: glossary + data-def).
    The data-definition layer drives which glossary Concepts/Codelists are
    needed (context dimensions + metrics), so glossary gathering unions the
    references from variables/headers with the data-definition components.

    ``include_agency`` (default True) prepends the SDMX:AGENCIES scheme carrying
    the owning agency, so the output is a self-contained, directly-FMR-loadable
    message; set it False to emit only the framework artefacts.
    """
    conventions = conventions or Conventions()
    report = ReviewReport()
    layers = layers or ["glossary", "data-def"]
    builder = SdmxBuilder(conventions, report)
    objects: List[Any] = []

    with DpmReader(db_path) as reader:
        module = reader.read_module(module_code, release_code=release_code)
        agency = conventions.agency_for(module.get("owner"))
        if include_agency:
            objects.append(builder.build_agency_scheme([agency]))
        # One ConceptScheme per Owner/Agency (CS_<AGENCY>), per glossary rule §3.5.6.
        conceptscheme_id = conventions.conceptscheme_id_for(agency)
        prop_index = reader.properties_by_id(release_code=release_code)

        # Per-table components (dimensions from contexts, measures from metrics).
        table_specs: List[Tuple[Dict[str, Any], List[int], List[int]]] = []
        used_property_ids: Set[int] = set()
        for table in module.get("tables") or []:
            dim_pids, metric_pids = reader.read_table_components(table["tableVersionId"])
            table_specs.append((table, dim_pids, metric_pids))
            used_property_ids.update(dim_pids, metric_pids)

        # Also include properties referenced directly by variables/headers.
        _cat_from_vars, prop_ids_from_vars = builder.gather_references(module)
        used_property_ids.update(prop_ids_from_vars)

        if "glossary" in layers:
            properties = [prop_index[p] for p in sorted(used_property_ids) if p in prop_index]
            category_codes = _category_codes_for(properties) | _cat_from_vars
            categories = reader.read_categories(
                list(category_codes), release_code=release_code
            )
            objects += builder.build_glossary(
                categories,
                properties,
                conceptscheme_id=conceptscheme_id,
                conceptscheme_name=conventions.conceptscheme_name_for(agency),
                agency=agency,
            )

        if "data-def" in layers:
            objects += builder.build_data_definition(
                table_specs,
                prop_index,
                conceptscheme_id=conceptscheme_id,
                agency=agency,
                module_code=module_code,
            )
            report.add(
                "reporting_taxonomy.unsupported",
                "pysdmx has no ReportingTaxonomy; the Module grouping is recorded "
                "as a DPM_MODULE annotation on each Dataflow instead.",
                artefact=module_code,
                severity=ReviewSeverity.INFO,
            )

    if "constraints" in layers:
        report.add(
            "layer.constraints.pending",
            "Constraints layer (SubCategory -> ContentConstraint) is Phase 4.",
            artefact=module_code,
            severity=ReviewSeverity.INFO,
        )

    return DpmToSdmxResult(objects=objects, report=report)
