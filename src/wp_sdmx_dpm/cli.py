"""Command-line entry points: ``dpm-to-sdmx`` and ``sdmx-to-dpm``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .convert.dpm_to_sdmx import convert_module
from .convert.sdmx_to_dpm import convert_structure
from .sdmx.serializer import partition_messages, serialize

_LAYERS = ["glossary", "data-def", "constraints"]


def _layers_arg(value: str) -> List[str]:
    layers = [v.strip() for v in value.split(",") if v.strip()]
    bad = [l for l in layers if l not in _LAYERS]
    if bad:
        raise argparse.ArgumentTypeError(f"unknown layer(s): {bad}; choose from {_LAYERS}")
    return layers


def dpm_to_sdmx_main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="dpm-to-sdmx", description="Translate a DPM module into SDMX structures."
    )
    p.add_argument("--db", required=True, help="Path to the input DPM SQLite database")
    p.add_argument("--module", required=True, help="Module code, e.g. COREP_LE")
    p.add_argument("--release", default=None, help="DPM release code (default: latest)")
    p.add_argument("--out", required=True, help="Output directory")
    p.add_argument("--format", default="sdmx-ml", choices=["sdmx-ml", "json"])
    p.add_argument(
        "--sdmx-version",
        default="3.0",
        choices=["3.0", "3.1"],
        help="SDMX-ML dialect (default 3.0, loadable by FMR; 3.1 is spec-aligned)",
    )
    p.add_argument(
        "--no-agency",
        action="store_true",
        help="Do not bundle the SDMX:AGENCIES scheme in the output",
    )
    p.add_argument("--layers", type=_layers_arg, default=None, help="Comma-separated subset")
    args = p.parse_args(argv)

    result = convert_module(
        args.db,
        args.module,
        release_code=args.release,
        layers=args.layers,
        include_agency=not args.no_agency,
    )
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = "xml" if args.format == "sdmx-ml" else "json"

    # Emit two messages so they load into FMR in dependency order: vocabulary
    # (agencies/codelists/concepts/hierarchies) before structures (DSDs,
    # Dataflows, …). See out/fmr-structure-submission-race.md.
    vocabulary, structures = partition_messages(result.objects)
    written = []
    for label, objects in (("vocabulary", vocabulary), ("structures", structures)):
        if not objects:
            continue
        name = f"{args.module}.{label}.{ext}"
        serialize(objects, args.format, str(out_dir / name), sdmx_version=args.sdmx_version)
        written.append(name)

    (out_dir / f"{args.module}.review.json").write_text(result.report.to_json())
    print(f"Wrote {', '.join(written)} and review report to {out_dir}")
    return 1 if result.report.has_blocking else 0


def sdmx_to_dpm_main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="sdmx-to-dpm", description="Translate an SDMX structure into a DPM SQLite DB."
    )
    p.add_argument("--source", required=True, help="FMR endpoint URL or local SDMX file path")
    p.add_argument("--structure", required=True, help="Structure ref, e.g. ECB:CBD2(1.0)")
    p.add_argument("--out", required=True, help="Output DPM SQLite DB path")
    p.add_argument("--layers", type=_layers_arg, default=None, help="Comma-separated subset")
    args = p.parse_args(argv)

    result = convert_structure(args.source, args.structure, args.out, layers=args.layers)
    status = "valid" if result.is_valid else "INVALID"
    print(
        f"Wrote DPM database to {result.out_db_path} "
        f"({result.tables_written} table(s), schema {status})"
    )
    return 1 if result.report.has_blocking or not result.is_valid else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(dpm_to_sdmx_main())
