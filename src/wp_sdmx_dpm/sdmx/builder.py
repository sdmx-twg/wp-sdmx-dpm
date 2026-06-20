"""Build pysdmx structure objects from DPM dicts.

Turns the JSON-like dicts returned by ``dpmcore`` StructureService into pysdmx
model objects. Phase 2 implements the glossary layer (Codelists +
ConceptScheme); the data-definition layer (DSD/Dataflow) follows in Phase 3.

The per-artefact mapping rules live in :mod:`wp_sdmx_dpm.mapping`; this module
gathers the glossary a module references and assembles the objects for
serialisation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from pysdmx.model import Agency, AgencyScheme, ConceptScheme

from ..config import Conventions, ReviewReport
from ..ids import normalise_sdmx_id
from ..mapping.constraints import table_to_content_constraint
from ..mapping.data_definition import table_to_dsd_and_dataflow
from ..mapping.glossary import (
    category_to_codelist,
    property_to_concept,
    subcategory_to_hierarchy,
)

# The SDMX agency scheme is a fixed maintainable (SDMX:AGENCIES(1.0)) that every
# registry hosts; custom agencies are added as items of it.
_SDMX_AGENCY_SCHEME = ("SDMX", "AGENCIES", "1.0")


class SdmxBuilder:
    """Assemble pysdmx artefacts for a DPM module."""

    def __init__(self, conventions: Conventions, report: ReviewReport):
        self.conventions = conventions
        self.report = report

    # -- organisation layer ------------------------------------------------
    def build_agency_scheme(self, agency_ids: List[str]) -> AgencyScheme:
        """Build the SDMX:AGENCIES scheme carrying the agencies we reference.

        FMR resolves every artefact's ``agencyID`` against an Agency item of
        ``SDMX:AGENCIES(1.0)``; a fresh registry only has ``SDMX`` itself, so the
        converter bundles this scheme to make the output self-contained.
        Submitting it requires ``Action: Replace`` (it updates the existing
        scheme rather than appending a sibling).
        """
        sdmx_agency, scheme_id, version = _SDMX_AGENCY_SCHEME
        agencies = [
            Agency(id=aid, name=self.conventions.agency_name_for(aid))
            for aid in sorted(set(agency_ids))
        ]
        return AgencyScheme(
            id=scheme_id,
            name="SDMX Agency Scheme",
            agency=sdmx_agency,
            version=version,
            items=agencies,
        )

    # -- reference gathering ----------------------------------------------
    @staticmethod
    def gather_references(module: Dict[str, Any]) -> Tuple[Set[str], Set[int]]:
        """Collect (enumerated category codes, property ids) used by a module."""
        category_codes: Set[str] = set()
        property_ids: Set[int] = set()
        for table in module.get("tables") or []:
            variables = (table.get("keyVariables") or []) + (table.get("factVariables") or [])
            for var in variables:
                prop = var.get("property")
                if prop and prop.get("id") is not None:
                    property_ids.add(prop["id"])
                enum = var.get("enumeration")
                if enum and enum.get("categoryCode"):
                    category_codes.add(enum["categoryCode"])
            for header in table.get("headers") or []:
                prop = header.get("property")
                if prop and prop.get("id") is not None:
                    property_ids.add(prop["id"])
        return category_codes, property_ids

    # -- glossary layer ----------------------------------------------------
    def build_glossary(
        self,
        categories: List[Dict[str, Any]],
        properties: List[Dict[str, Any]],
        *,
        conceptscheme_id: str,
        conceptscheme_name: str,
        agency: str,
        hierarchies_by_category: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ) -> List[Any]:
        """Build Codelists (+ Hierarchies) + one ConceptScheme from DPM dicts.

        ``hierarchies_by_category`` maps a Category code to the hierarchical
        SubCategories over it (from :meth:`DpmReader.read_hierarchies`); each
        becomes an SDMX :class:`Hierarchy` over the Category's Codelist. Pass
        ``None`` to emit codelists without hierarchies.
        """
        hierarchies_by_category = hierarchies_by_category or {}
        objects: List[Any] = []
        for category in categories:
            if not category.get("isEnumerated"):
                continue
            objects.append(category_to_codelist(category, self.conventions, self.report))
            for sub in hierarchies_by_category.get(category.get("code"), []):
                hierarchy = subcategory_to_hierarchy(
                    sub, agency=agency, conventions=self.conventions, report=self.report
                )
                if hierarchy is not None:
                    objects.append(hierarchy)

        concepts = [
            property_to_concept(prop, self.conventions, self.report) for prop in properties
        ]
        scheme = ConceptScheme(
            id=normalise_sdmx_id(conceptscheme_id),
            name=conceptscheme_name,
            agency=agency,
            version="1.0",
            items=concepts,
        )
        objects.append(scheme)
        return objects

    # -- data-definition layer --------------------------------------------
    def build_data_definition(
        self,
        table_specs: List[Tuple[Dict[str, Any], List[int], List[int]]],
        prop_index: Dict[int, Dict[str, Any]],
        *,
        conceptscheme_id: str,
        agency: str,
        module_code: str,
    ) -> List[Any]:
        """Build one DSD + Dataflow per table from (table, dim_pids, metric_pids)."""
        objects: List[Any] = []
        for table, dim_pids, metric_pids in table_specs:
            dim_props = [prop_index[p] for p in dim_pids if p in prop_index]
            metric_props = [prop_index[p] for p in metric_pids if p in prop_index]
            built = table_to_dsd_and_dataflow(
                table,
                dim_props,
                metric_props,
                conceptscheme_id=conceptscheme_id,
                agency=agency,
                module_code=module_code,
                conventions=self.conventions,
                report=self.report,
            )
            if built is not None:
                objects += list(built)
        return objects

    # -- constraint layer --------------------------------------------------
    @staticmethod
    def _is_closed_table(table: Dict[str, Any]) -> bool:
        """A table is closed when no axis is open (a finite set of data points).

        Closed tables enumerate their series keys (DataKeySet); open ones (any
        ``hasOpen*`` axis, or a flat SubCategory-driven table) are described
        dimension-wise (CubeRegion). Spec section 3.3.2 / 3.3.8.
        """
        if table.get("isFlat"):
            return False
        return not (
            table.get("hasOpenRows")
            or table.get("hasOpenColumns")
            or table.get("hasOpenSheets")
        )

    def build_constraints(
        self,
        table_specs: List[Tuple[Dict[str, Any], List[int], List[int]]],
        prop_index: Dict[int, Dict[str, Any]],
        constraint_values_by_table: Dict[int, Dict[str, Any]],
        *,
        agency: str,
    ) -> List[Any]:
        """Build one DataConstraint per table from its data-point dimension keys.

        ``constraint_values_by_table`` maps a table's ``tableVersionId`` to the
        per-data-point keys from :meth:`DpmReader.read_table_constraint_values`.
        Each dimension Property's SDMX id is resolved from ``prop_index``; the
        order follows the DSD's dimension order (``dim_pids``). Closed tables
        become a DataKeySet, open tables a CubeRegion.
        """
        objects: List[Any] = []
        for table, dim_pids, _metric_pids in table_specs:
            cv = constraint_values_by_table.get(table.get("tableVersionId")) or {}
            dim_meta = cv.get("dims", {})
            id_by_pid = {
                pid: normalise_sdmx_id(prop_index[pid]["code"])
                for pid in dim_pids
                if pid in prop_index and pid in dim_meta
            }
            ordered_dim_ids = [id_by_pid[pid] for pid in dim_pids if pid in id_by_pid]
            keys = [
                {id_by_pid[pid]: code for pid, code in key.items() if pid in id_by_pid}
                for key in cv.get("keys", [])
            ]
            uses_default = {
                id_by_pid[pid]: flag
                for pid, flag in cv.get("usesDefault", {}).items()
                if pid in id_by_pid
            }
            constraint = table_to_content_constraint(
                table, ordered_dim_ids, keys, uses_default,
                closed=self._is_closed_table(table), agency=agency,
                conventions=self.conventions, report=self.report,
                datapoint_count=cv.get("datapointCount"),
            )
            if constraint is not None:
                objects.append(constraint)
        return objects
