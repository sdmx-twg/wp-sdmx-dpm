"""Serialise pysdmx structure objects to SDMX-ML or SDMX-JSON.

Wraps :func:`pysdmx.io.write_sdmx`. SDMX-ML output defaults to **3.0**, the
highest SDMX-ML version the Fusion Metadata Registry (FMR 12) can ingest, so the
generated file loads directly into a registry. SDMX-ML 3.1 (aligned with the
project's mapping spec) is available via ``sdmx_version="3.1"`` for tooling that
supports it. SDMX-JSON 2.0 is the machine-friendly alternative.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from pysdmx.io import write_sdmx
from pysdmx.io.format import Format
from pysdmx.model import (
    AgencyScheme,
    Codelist,
    ConceptScheme,
    Hierarchy,
    HierarchyAssociation,
)

# FMR cannot reliably resolve a reference to an artefact that arrives in the
# *same* submission (intermittent code-100 "Could not resolve reference" — see
# out/fmr-structure-submission-race.md). The converter therefore emits one
# message per dependency tier, each loaded as a separate POST in this order:
#   1. codelists  — agencies + codelists (the value domains everything points at);
#   2. concepts   — concept schemes + hierarchies (Concepts reference Codelists
#                   via their enumerated core representation);
#   3. structures — everything else (DSDs, Dataflows, Constraints, CategorySchemes)
#                   which reference both codelists and concepts.
# Agencies lead tier 1 because every artefact's agencyID resolves against them.
# Each tier's references are persisted by the previous POST, so validation is
# deterministic regardless of intra-message ordering.
_STAGE_TYPES: Tuple[Tuple[str, Tuple[type, ...]], ...] = (
    ("codelists", (AgencyScheme, Codelist)),
    ("concepts", (ConceptScheme, Hierarchy, HierarchyAssociation)),
)


def partition_stages(objects: Any) -> List[Tuple[str, List[Any]]]:
    """Split artefacts into ordered ``(label, objects)`` FMR submission tiers.

    Returns the tiers in dependency order: ``codelists`` (agencies + codelists),
    ``concepts`` (concept schemes + hierarchies), then ``structures`` (everything
    else). Order within each tier is preserved. Empty tiers are still returned;
    callers skip them.
    """
    stages: Dict[str, List[Any]] = {label: [] for label, _ in _STAGE_TYPES}
    structures: List[Any] = []
    for obj in objects:
        for label, types in _STAGE_TYPES:
            if isinstance(obj, types):
                stages[label].append(obj)
                break
        else:
            structures.append(obj)
    ordered = [(label, stages[label]) for label, _ in _STAGE_TYPES]
    ordered.append(("structures", structures))
    return ordered

# SDMX-ML structure format per requested version. 3.0 is the default because it
# is the newest dialect FMR accepts; 3.1 is opt-in for spec-aligned output.
_SDMX_ML_BY_VERSION = {
    "3.0": Format.STRUCTURE_SDMX_ML_3_0,
    "3.1": Format.STRUCTURE_SDMX_ML_3_1,
}
DEFAULT_SDMX_VERSION = "3.0"

_JSON_FORMATS = {"json", "sdmx-json"}
_XML_FORMATS = {"sdmx-ml", "xml"}


def resolve_format(name: str, sdmx_version: str = DEFAULT_SDMX_VERSION) -> Format:
    key = name.lower()
    if key in _JSON_FORMATS:
        return Format.STRUCTURE_SDMX_JSON_2_0_0
    if key in _XML_FORMATS:
        try:
            return _SDMX_ML_BY_VERSION[sdmx_version]
        except KeyError:
            raise ValueError(
                f"Unsupported SDMX-ML version {sdmx_version!r}; "
                f"choose one of {sorted(_SDMX_ML_BY_VERSION)}"
            ) from None
    raise ValueError(
        f"Unknown output format {name!r}; choose one of "
        f"{sorted(_XML_FORMATS | _JSON_FORMATS)}"
    )


def serialize(
    sdmx_objects: Any,
    fmt: str,
    output_path: str = "",
    *,
    sdmx_version: str = DEFAULT_SDMX_VERSION,
) -> Optional[str]:
    """Write ``sdmx_objects`` (one object or a list) in ``fmt``.

    ``sdmx_version`` selects the SDMX-ML dialect ("3.0" default, "3.1" opt-in);
    it is ignored for JSON output. Returns the serialised string when
    ``output_path`` is empty, else writes to the path and returns None.
    """
    return write_sdmx(
        sdmx_objects, resolve_format(fmt, sdmx_version), output_path=output_path
    )
