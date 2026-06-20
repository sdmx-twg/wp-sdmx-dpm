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
    layers = layers or ["glossary", "data-def", "constraints"]
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
        constraint_values_by_table: Dict[int, Dict[str, Any]] = {}
        need_constraints = "constraints" in layers and "data-def" in layers
        for table in module.get("tables") or []:
            tvid = table["tableVersionId"]
            context_dims, metric_pids = reader.read_table_components(tvid)
            open_keys = reader.read_open_keys(table)
            # DSD dimensions = context Properties + open keys (spec 3.2.7). Open
            # keys (KeyVariables on open axes) are dimensions the FactVariable
            # Contexts never mention; append them after the context dimensions,
            # de-duplicated, and never count them as measures.
            dim_pids = list(context_dims)
            seen = set(dim_pids)
            for pid in (k["propertyId"] for k in open_keys):
                if pid not in seen:
                    seen.add(pid)
                    dim_pids.append(pid)
            metric_pids = [p for p in metric_pids if p not in seen]
            table_specs.append((table, dim_pids, metric_pids))
            used_property_ids.update(dim_pids, metric_pids)
            if need_constraints:
                # Context dims drive the per-data-point keys; open keys carry
                # their own (open-axis SubCategory) allowed values separately.
                constraint_values_by_table[tvid] = (
                    reader.read_table_constraint_values(
                        tvid, context_dims, open_keys=open_keys
                    )
                )

        # Also include properties referenced directly by variables/headers.
        _cat_from_vars, prop_ids_from_vars = builder.gather_references(module)
        used_property_ids.update(prop_ids_from_vars)

        if "glossary" in layers:
            properties = [prop_index[p] for p in sorted(used_property_ids) if p in prop_index]
            category_codes = _category_codes_for(properties) | _cat_from_vars
            categories = reader.read_categories(
                list(category_codes), release_code=release_code
            )
            hierarchies = reader.read_hierarchies(
                list(category_codes), release_code=release_code
            )
            objects += builder.build_glossary(
                categories,
                properties,
                conceptscheme_id=conceptscheme_id,
                conceptscheme_name=conventions.conceptscheme_name_for(agency),
                agency=agency,
                hierarchies_by_category=hierarchies,
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
            if "data-def" not in layers:
                report.add(
                    "layer.constraints.needs_data_def",
                    "Constraints attach to a Dataflow; the 'data-def' layer must "
                    "also be selected to emit them. Skipped.",
                    artefact=module_code,
                    severity=ReviewSeverity.REVIEW,
                )
            else:
                objects += builder.build_constraints(
                    table_specs,
                    prop_index,
                    constraint_values_by_table,
                    agency=agency,
                )

    return DpmToSdmxResult(objects=objects, report=report)


def convert_glossary(
    db_path: str,
    *,
    release_code: Optional[str] = None,
    conventions: Optional[Conventions] = None,
    include_agency: bool = True,
) -> DpmToSdmxResult:
    """Build the *whole* glossary (Codelists + Hierarchies + Concepts), no module.

    Unlike :func:`convert_module`, this does not filter by what a module uses:
    every enumerated Category becomes a Codelist carrying all its Items, every
    hierarchical SubCategory becomes a Hierarchy, and every Property becomes a
    Concept. Artefacts are grouped by owning Agency -- one ``CS_<AGENCY>``
    ConceptScheme per agency -- and a single ``SDMX:AGENCIES`` scheme bundles all
    agencies referenced. This is the practical unit for sharing/importing the
    glossary: importing a Codelist brings everything related to it.
    """
    conventions = conventions or Conventions()
    report = ReviewReport()
    builder = SdmxBuilder(conventions, report)
    objects: List[Any] = []

    with DpmReader(db_path) as reader:
        # Emit *every* enumerated Category as a Codelist -- including "internal"
        # ones (e.g. the "_PR"/"_TE" property categories) -- because Concepts may
        # reference them via their enumerated representation; dropping them would
        # leave dangling references. The whole-glossary export is deliberately
        # complete and self-contained.
        categories = [
            c
            for c in reader.read_all_categories(release_code=release_code)
            if c.get("isEnumerated")
        ]
        hierarchies = reader.read_hierarchies(release_code=release_code)
        properties = list(reader.properties_by_id(release_code=release_code).values())

    # Group categories and properties by owning agency so each agency gets its
    # own ConceptScheme (and its codelists carry the right agencyID).
    cats_by_agency: Dict[str, List[Dict[str, Any]]] = {}
    for category in categories:
        agency = conventions.agency_for(category.get("owner"))
        cats_by_agency.setdefault(agency, []).append(category)
    props_by_agency: Dict[str, List[Dict[str, Any]]] = {}
    for prop in properties:
        agency = conventions.agency_for(prop.get("owner"))
        props_by_agency.setdefault(agency, []).append(prop)

    agencies = sorted(set(cats_by_agency) | set(props_by_agency))
    if include_agency:
        objects.append(builder.build_agency_scheme(agencies))

    for agency in agencies:
        objects += builder.build_glossary(
            cats_by_agency.get(agency, []),
            props_by_agency.get(agency, []),
            conceptscheme_id=conventions.conceptscheme_id_for(agency),
            conceptscheme_name=conventions.conceptscheme_name_for(agency),
            agency=agency,
            hierarchies_by_category=hierarchies,
        )

    return DpmToSdmxResult(objects=objects, report=report)
