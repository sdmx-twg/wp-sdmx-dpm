"""Orchestrate SDMX structure -> DPM conversion (glossary -> flat table -> module)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from ..config import Conventions, ReviewReport
from ..dpm.writer import DpmWriter
from ..mapping.data_definition import dsd_to_flat_table, synthesise_module_spec
from ..mapping.glossary import codelist_to_category, concept_to_property
from ..sdmx.source import open_source


@dataclass
class SdmxToDpmResult:
    out_db_path: str
    is_valid: bool = False
    tables_written: int = 0
    report: ReviewReport = field(default_factory=ReviewReport)


def convert_structure(
    source: str,
    structure_ref: str,
    out_db_path: str,
    *,
    conventions: Optional[Conventions] = None,
    layers: Optional[List[str]] = None,
) -> SdmxToDpmResult:
    """Load ``structure_ref`` (``AGENCY:ID(VERSION)``) from ``source`` and write a
    new DPM SQLite DB at ``out_db_path`` as a flat table (spec 3.2.6)."""
    conventions = conventions or Conventions()
    report = ReviewReport()
    layers = layers or ["glossary", "data-def"]

    bundle = open_source(source).load_structure(structure_ref)

    table_spec = dsd_to_flat_table(
        bundle.dataflow, bundle.dsd, conventions=conventions, report=report
    )
    # The DSD component role is the authoritative IsMetric source (Measure ->
    # metric; Dimension/Attribute -> not), so hint concept_to_property with it.
    metric_by_code = {c["property_code"]: (c["variable_type"] == "fact")
                      for c in table_spec["components"]}

    categories = [codelist_to_category(cl, conventions, report) for cl in bundle.codelists]
    concepts = [c for cs in bundle.concept_schemes for c in (cs.items or [])]
    properties = [
        concept_to_property(c, conventions, report, is_metric_hint=metric_by_code.get(c.id))
        for c in concepts
    ]
    module_spec = synthesise_module_spec(bundle.dataflow, report)

    writer = DpmWriter(out_db_path, conventions, report)
    try:
        writer.create_schema()
        if "glossary" in layers:
            writer.write_glossary(categories, properties)
        if "data-def" in layers:
            writer.write_flat_table(table_spec, module_spec)
        result = writer.finalise()
    finally:
        writer.close()

    return SdmxToDpmResult(
        out_db_path=result.out_db_path,
        is_valid=result.is_valid,
        tables_written=result.tables_written,
        report=report,
    )
