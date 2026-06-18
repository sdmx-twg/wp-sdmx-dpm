"""Load SDMX structures from a configurable source: FMR registry OR local file.

``--source`` is auto-detected: an ``http(s)://`` value is treated as an FMR REST
endpoint (read via :class:`pysdmx.api.fmr.RegistryClient`); anything else is a
path to a local SDMX-ML/JSON document (read via :func:`pysdmx.io.read_sdmx`).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pysdmx.api.fmr import RegistryClient
from pysdmx.io import read_sdmx


def is_registry_endpoint(source: str) -> bool:
    return source.startswith("http://") or source.startswith("https://")


def open_source(source: str) -> "SdmxSource":
    return RegistrySource(source) if is_registry_endpoint(source) else FileSource(source)


class SdmxSource:
    """Common interface for fetching a DSD + Dataflow pair by reference."""

    def get_data_structure(self, agency: str, id_: str, version: str) -> Any:
        raise NotImplementedError

    def get_dataflow(self, agency: str, id_: str, version: str) -> Any:
        raise NotImplementedError


class RegistrySource(SdmxSource):
    """Read structures live from an FMR registry."""

    def __init__(self, endpoint: str, timeout: float = 30.0):
        self.client = RegistryClient(endpoint, timeout=timeout)

    def get_data_structure(self, agency: str, id_: str, version: str) -> Any:
        return self.client.get_data_structures(agency, id_, version)

    def get_dataflow(self, agency: str, id_: str, version: str) -> Any:
        # DataflowDetails control whether components/constraints are resolved;
        # the builder (Phase 3) will request the level of detail it needs.
        return self.client.get_dataflows(agency, id_, version)


class FileSource(SdmxSource):
    """Read structures from a local SDMX-ML/JSON document."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.message = read_sdmx(self.path)

    def get_data_structure(self, agency: str, id_: str, version: str) -> Any:
        # Phase 3: resolve from self.message by urn/short-urn.
        raise NotImplementedError("FileSource structure lookup is implemented in Phase 3")

    def get_dataflow(self, agency: str, id_: str, version: str) -> Any:
        raise NotImplementedError("FileSource dataflow lookup is implemented in Phase 3")
