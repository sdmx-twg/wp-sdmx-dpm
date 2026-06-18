"""Orchestrate SDMX structure -> DPM conversion (glossary -> flat table -> module)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ..config import Conventions, ReviewReport
from ..dpm.writer import DpmWriter
from ..sdmx.source import open_source


@dataclass
class SdmxToDpmResult:
    out_db_path: str
    report: ReviewReport = field(default_factory=ReviewReport)


def convert_structure(
    source: str,
    structure_ref: str,
    out_db_path: str,
    *,
    conventions: Optional[Conventions] = None,
    layers: Optional[list] = None,
) -> SdmxToDpmResult:
    """Load ``structure_ref`` (``agency:id(version)``) from ``source`` and write
    a new DPM SQLite DB at ``out_db_path``. Phase 3 fills the body in."""
    conventions = conventions or Conventions()
    report = ReviewReport()
    _src = open_source(source)
    writer = DpmWriter(out_db_path)
    writer.create_schema()  # NotImplementedError until Phase 3
    return SdmxToDpmResult(out_db_path=out_db_path, report=report)
