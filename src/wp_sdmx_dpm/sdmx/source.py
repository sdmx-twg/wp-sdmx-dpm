"""Load SDMX structures from a configurable source: FMR registry OR local file.

``--source`` is auto-detected: an ``http(s)://`` value is treated as an FMR REST
endpoint (read via :class:`pysdmx.api.fmr.RegistryClient`); anything else is a
path to a local SDMX-ML/JSON document (read via :func:`pysdmx.io.read_sdmx`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

from pysdmx.api.fmr import RegistryClient
from pysdmx.io import read_sdmx

# Structure reference: "AGENCY:ID(VERSION)", "AGENCY:ID", or "ID".
_REF = re.compile(r"^(?:(?P<agency>[^:]+):)?(?P<id>[^():]+)(?:\((?P<version>[^)]+)\))?$")


@dataclass
class StructureBundle:
    """Everything needed to map one Dataflow+DSD into a flat DPM table."""

    dataflow: Any
    dsd: Any
    codelists: List[Any] = field(default_factory=list)
    concept_schemes: List[Any] = field(default_factory=list)


def parse_structure_ref(ref: str) -> tuple:
    m = _REF.match(ref.strip())
    if not m:
        raise ValueError(f"Cannot parse structure reference {ref!r}")
    return m.group("agency"), m.group("id"), m.group("version")


def is_registry_endpoint(source: str) -> bool:
    return source.startswith("http://") or source.startswith("https://")


def open_source(source: str) -> "SdmxSource":
    return RegistrySource(source) if is_registry_endpoint(source) else FileSource(source)


class SdmxSource:
    """Common interface for fetching a Dataflow + its DSD (and glossary)."""

    def load_structure(self, structure_ref: str) -> StructureBundle:
        raise NotImplementedError


class RegistrySource(SdmxSource):
    """Read structures live from an FMR registry."""

    def __init__(self, endpoint: str, timeout: float = 30.0):
        self.client = RegistryClient(endpoint, timeout=timeout)

    def load_structure(self, structure_ref: str) -> StructureBundle:
        agency, id_, version = parse_structure_ref(structure_ref)
        dataflow = self.client.get_dataflows(agency, id_, version)
        dsd = self.client.get_data_structures(agency, id_, version)
        # Registry codelists/concepts are resolved lazily per component; callers
        # that need the full glossary should fetch via get_codes/get_concepts.
        return StructureBundle(dataflow=dataflow, dsd=dsd)


class FileSource(SdmxSource):
    """Read structures from a local SDMX-ML/JSON document."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.message = read_sdmx(self.path)

    def _dataflows(self) -> List[Any]:
        return list(self.message.get_dataflows() or [])

    def _dsds(self) -> List[Any]:
        return list(self.message.get_data_structure_definitions() or [])

    def load_structure(self, structure_ref: str) -> StructureBundle:
        _agency, id_, _version = parse_structure_ref(structure_ref)
        dataflow = next((d for d in self._dataflows() if d.id == id_), None)
        if dataflow is None:
            raise KeyError(f"Dataflow {id_!r} not found in {self.path}")
        # resolve the DSD the dataflow points at (short_urn like DataStructure=A:ID(v))
        dsd = self._resolve_dsd(dataflow)
        return StructureBundle(
            dataflow=dataflow,
            dsd=dsd,
            codelists=list(self.message.get_codelists() or []),
            concept_schemes=list(self.message.get_concept_schemes() or []),
        )

    def _resolve_dsd(self, dataflow: Any) -> Any:
        dsds = self._dsds()
        ref = dataflow.structure
        if ref is None:
            if len(dsds) == 1:
                return dsds[0]
            raise KeyError(f"Dataflow {dataflow.id!r} has no structure reference")
        # ref may be a short_urn string or a DSD object
        ref_id = getattr(ref, "id", None) or str(ref).split("=")[-1].split(":")[-1].split("(")[0]
        for dsd in dsds:
            if dsd.id == ref_id:
                return dsd
        if len(dsds) == 1:
            return dsds[0]
        raise KeyError(f"DSD {ref_id!r} for dataflow {dataflow.id!r} not found")
