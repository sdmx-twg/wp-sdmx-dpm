"""Orchestrate DPM module -> SDMX conversion (glossary -> data def -> constraints)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from ..config import Conventions, ReviewReport
from ..dpm.reader import DpmReader
from ..sdmx.builder import SdmxBuilder


@dataclass
class DpmToSdmxResult:
    objects: List[Any] = field(default_factory=list)
    report: ReviewReport = field(default_factory=ReviewReport)


def convert_module(
    db_path: str,
    module_code: str,
    *,
    release_code: Optional[str] = None,
    conventions: Optional[Conventions] = None,
    layers: Optional[List[str]] = None,
) -> DpmToSdmxResult:
    """Read ``module_code`` from ``db_path`` and build SDMX structures.

    ``layers`` selects which spec layers to emit (default: all implemented).
    The heavy lifting lives in :class:`SdmxBuilder` / :mod:`wp_sdmx_dpm.mapping`
    (Phase 2+).
    """
    conventions = conventions or Conventions()
    report = ReviewReport()
    with DpmReader(db_path) as reader:
        module = reader.read_module(module_code, release_code=release_code)
    builder = SdmxBuilder(conventions, report)
    objects = builder.build_module(module)  # NotImplementedError until Phase 2
    return DpmToSdmxResult(objects=objects, report=report)
