"""Serialise pysdmx structure objects to SDMX-ML or SDMX-JSON.

Wraps :func:`pysdmx.io.write_sdmx`. SDMX-ML output defaults to **3.0**, the
highest SDMX-ML version the Fusion Metadata Registry (FMR 12) can ingest, so the
generated file loads directly into a registry. SDMX-ML 3.1 (aligned with the
project's mapping spec) is available via ``sdmx_version="3.1"`` for tooling that
supports it. SDMX-JSON 2.0 is the machine-friendly alternative.
"""

from __future__ import annotations

from typing import Any, List, Optional, Tuple

from pysdmx.io import write_sdmx
from pysdmx.io.format import Format
from pysdmx.model import (
    AgencyScheme,
    Codelist,
    ConceptScheme,
    Hierarchy,
    HierarchyAssociation,
)

# FMR resolves a DSD's references against the registry store and cannot reliably
# resolve a Codelist that arrives in the *same* submission (intermittent code-100
# "Could not resolve reference" — see out/fmr-structure-submission-race.md). So
# the converter emits two messages, loaded in this order:
#   1. vocabulary — the agencies/codelists/concepts/hierarchies things point at;
#   2. structures — everything else (DSDs, Dataflows, Constraints, CategorySchemes).
# Agencies lead the vocabulary message because every artefact's agencyID resolves
# against them.
_VOCABULARY_TYPES = (
    AgencyScheme,
    Codelist,
    ConceptScheme,
    Hierarchy,
    HierarchyAssociation,
)


def partition_messages(objects: Any) -> Tuple[List[Any], List[Any]]:
    """Split artefacts into ``(vocabulary, structures)`` for separate submission.

    Vocabulary = agencies, codelists, concept schemes, hierarchies. Structures =
    everything else (DSDs, Dataflows, Constraints, CategorySchemes, …). Order
    within each group is preserved.
    """
    vocabulary: List[Any] = []
    structures: List[Any] = []
    for obj in objects:
        (vocabulary if isinstance(obj, _VOCABULARY_TYPES) else structures).append(obj)
    return vocabulary, structures

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
