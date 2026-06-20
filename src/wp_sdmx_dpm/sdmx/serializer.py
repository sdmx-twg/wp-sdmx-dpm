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
#   1. codelists   — agencies + codelists (the value domains everything points at);
#   2. hierarchies — Hierarchies (their HierarchicalCodes reference Codelist Codes);
#   3. concepts    — concept schemes (Concepts reference Codelists via their
#                    enumerated core representation);
#   4. structures  — everything else (DSDs, Dataflows, Constraints, CategorySchemes)
#                    which reference both codelists and concepts.
# Agencies lead tier 1 because every artefact's agencyID resolves against them.
# Each tier's references are persisted by the previous POST, so validation is
# deterministic regardless of intra-message ordering.
_STAGE_TYPES: Tuple[Tuple[str, Tuple[type, ...]], ...] = (
    ("codelists", (AgencyScheme, Codelist)),
    ("hierarchies", (Hierarchy, HierarchyAssociation)),
    ("concepts", (ConceptScheme,)),
)


def partition_stages(objects: Any) -> List[Tuple[str, List[Any]]]:
    """Split artefacts into ordered ``(label, objects)`` FMR submission tiers.

    Returns the tiers in dependency order: ``codelists`` (agencies + codelists),
    ``hierarchies`` (Hierarchies over those codelists), ``concepts`` (concept
    schemes), then ``structures`` (everything else). Order within each tier is
    preserved. Empty tiers are still returned; callers skip them.
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

    :class:`Hierarchy` artefacts are written by a small in-house SDMX-ML writer
    because pysdmx (1.16) has no Hierarchy serialiser; everything else goes
    through :func:`pysdmx.io.write_sdmx`. A list may not mix the two.
    """
    objs = sdmx_objects if isinstance(sdmx_objects, (list, tuple)) else [sdmx_objects]
    hierarchies = [o for o in objs if isinstance(o, Hierarchy)]
    if hierarchies:
        if len(hierarchies) != len(objs):
            raise ValueError(
                "Hierarchies must be serialised on their own (pysdmx cannot write "
                "them, so they cannot share a message with other artefacts)"
            )
        if fmt.lower() in _JSON_FORMATS:
            raise ValueError("Hierarchy serialisation is only implemented for SDMX-ML")
        xml = write_hierarchies_message(hierarchies, sdmx_version=sdmx_version)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as fh:
                fh.write(xml)
            return None
        return xml
    return write_sdmx(
        sdmx_objects, resolve_format(fmt, sdmx_version), output_path=output_path
    )


# --- In-house SDMX-ML Hierarchy writer --------------------------------------
# pysdmx 1.16 ships no Hierarchy serialiser (the 3.0/3.1 writers don't register
# the type), so we emit the Hierarchies message ourselves. The shape follows the
# SDMX 3.x schema (SDMXStructureHierarchicalCodelist.xsd): each HierarchicalCode
# carries a ``<str:Code>`` URN reference and nests its children; the required
# ``hasFormalLevels`` attribute is "false" (DPM hierarchies are value-based).
# Verified loadable by FMR 12 via the structure API.
_NS = {
    "3.0": "v3_0",
    "3.1": "v3_1",
}


def _esc(text: Optional[str]) -> str:
    if text is None:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _write_hier_annotations(annotations: Any, indent: str) -> str:
    if not annotations:
        return ""
    out = f"{indent}<com:Annotations>"
    for ann in annotations:
        out += f"{indent}  <com:Annotation>"
        if getattr(ann, "type", None):
            out += f"<com:AnnotationType>{_esc(ann.type)}</com:AnnotationType>"
        if getattr(ann, "text", None):
            out += (
                f'<com:AnnotationText xml:lang="en">{_esc(ann.text)}</com:AnnotationText>'
            )
        out += "</com:Annotation>"
    out += f"{indent}</com:Annotations>"
    return out


def _write_hier_code(hcode: Any, indent: str) -> str:
    out = f'{indent}<str:HierarchicalCode id="{_esc(hcode.id)}">'
    out += f"{indent}  <str:Code>{_esc(hcode.urn)}</str:Code>"
    for child in hcode.codes or []:
        out += _write_hier_code(child, indent + "  ")
    out += f"{indent}</str:HierarchicalCode>"
    return out


def _write_hierarchy(h: Any, indent: str) -> str:
    agency = h.agency.id if hasattr(h.agency, "id") else h.agency
    out = (
        f'{indent}<str:Hierarchy id="{_esc(h.id)}" agencyID="{_esc(str(agency))}" '
        f'version="{_esc(h.version)}" isExternalReference="false" hasFormalLevels="false">'
    )
    out += _write_hier_annotations(getattr(h, "annotations", None), indent + "  ")
    out += f'{indent}  <com:Name xml:lang="en">{_esc(h.name)}</com:Name>'
    if getattr(h, "description", None):
        out += (
            f'{indent}  <com:Description xml:lang="en">'
            f"{_esc(h.description)}</com:Description>"
        )
    for code in h.codes or []:
        out += _write_hier_code(code, indent + "  ")
    out += f"{indent}</str:Hierarchy>"
    return out


def write_hierarchies_message(
    hierarchies: List[Any], *, sdmx_version: str = DEFAULT_SDMX_VERSION
) -> str:
    """Serialise Hierarchy artefacts into a self-contained SDMX-ML structure message."""
    ns = _NS.get(sdmx_version)
    if ns is None:
        raise ValueError(
            f"Unsupported SDMX-ML version {sdmx_version!r}; choose one of {sorted(_NS)}"
        )
    base = "http://www.sdmx.org/resources/sdmxml/schemas"
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<mes:Structure xmlns:mes="{base}/{ns}/message" '
        f'xmlns:str="{base}/{ns}/structure" '
        f'xmlns:com="{base}/{ns}/common">',
        "  <mes:Header>",
        "    <mes:ID>DPM_HIERARCHIES</mes:ID>",
        "    <mes:Test>false</mes:Test>",
        "    <mes:Prepared>2021-01-01T00:00:00</mes:Prepared>",
        '    <mes:Sender id="DPM"/>',
        "  </mes:Header>",
        "  <mes:Structures>",
        "    <str:Hierarchies>",
    ]
    body = "".join(_write_hierarchy(h, "\n      ") for h in hierarchies)
    tail = [
        "",
        "    </str:Hierarchies>",
        "  </mes:Structures>",
        "</mes:Structure>",
    ]
    return "\n".join(lines) + body + "\n".join(tail)
