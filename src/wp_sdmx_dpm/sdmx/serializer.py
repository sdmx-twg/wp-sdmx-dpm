"""Serialise pysdmx structure objects to SDMX-ML or SDMX-JSON.

Wraps :func:`pysdmx.io.write_sdmx`. Defaults to SDMX-ML 3.1 (the version aligned
with the project's SDMX 3.1 mapping spec); SDMX-JSON 2.0 is offered as the
machine-friendly alternative.
"""

from __future__ import annotations

from typing import Any, Optional

from pysdmx.io import write_sdmx
from pysdmx.io.format import Format

_FORMATS = {
    "sdmx-ml": Format.STRUCTURE_SDMX_ML_3_1,
    "xml": Format.STRUCTURE_SDMX_ML_3_1,
    "json": Format.STRUCTURE_SDMX_JSON_2_0_0,
    "sdmx-json": Format.STRUCTURE_SDMX_JSON_2_0_0,
}


def resolve_format(name: str) -> Format:
    try:
        return _FORMATS[name.lower()]
    except KeyError:
        raise ValueError(
            f"Unknown output format {name!r}; choose one of {sorted(_FORMATS)}"
        ) from None


def serialize(sdmx_objects: Any, fmt: str, output_path: str = "") -> Optional[str]:
    """Write ``sdmx_objects`` (one object or a list) in ``fmt``.

    Returns the serialised string when ``output_path`` is empty, else writes to
    the path and returns None.
    """
    return write_sdmx(sdmx_objects, resolve_format(fmt), output_path=output_path)
