"""Build pysdmx structure objects from DPM dicts.

Phase 2+ deliverable. Turns the JSON-like dicts returned by
``dpmcore`` StructureService into pysdmx model objects:
``Codelist``/``Code`` (glossary), ``Concept``/``ConceptScheme`` (glossary),
``DataStructureDefinition``/``Dataflow``/``Components`` (data definition).

The actual mapping logic lives in :mod:`wp_sdmx_dpm.mapping`; this module
assembles the resulting objects into the message ready for serialisation.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..config import Conventions, ReviewReport


class SdmxBuilder:
    """Assemble pysdmx artefacts for a DPM module. (Phase 2/3.)"""

    def __init__(self, conventions: Conventions, report: ReviewReport):
        self.conventions = conventions
        self.report = report

    def build_module(self, module: Dict[str, Any]) -> List[Any]:
        raise NotImplementedError("SdmxBuilder.build_module is implemented in Phase 2/3")
