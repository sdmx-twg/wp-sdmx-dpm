"""Write a new DPM SQLite database in dpmcore's ORM schema.

Phase 3 deliverable. The mechanism (verified during planning): dpmcore's ORM is
a standard SQLAlchemy declarative base, so a fresh DB is created with
``Base.metadata.create_all(engine)`` and populated by inserting ORM rows --
the same pattern ``dpmcore.loaders.migration.MigrationService`` uses. A valid
DPM DB needs the full mandatory row graph (Release, Organisation, version-range
columns, CompoundKey); ``connect(...).validate_schema()`` gates correctness.
"""

from __future__ import annotations

from typing import Any, Dict


class DpmWriter:
    """Materialise DPM artefacts into a new SQLite DB. (Phase 3.)"""

    def __init__(self, out_db_path: str):
        self.out_db_path = out_db_path

    def create_schema(self) -> None:
        raise NotImplementedError("DpmWriter.create_schema is implemented in Phase 3")

    def write_table(self, dpm_table: Dict[str, Any]) -> None:
        raise NotImplementedError("DpmWriter.write_table is implemented in Phase 3")
