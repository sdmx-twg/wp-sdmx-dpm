"""Read DPM artefacts from the input SQLite database via dpmcore.

Thin wrapper over ``dpmcore.connect()`` and its read-only ``StructureService``,
whose ``query_*`` methods return SDMX-style JSON-like dicts -- exactly the input
the SDMX builder consumes. The dicts are documented by example in the project
notes; key shapes (verified against dpm_4.2.1):

* module: ``id, code, name, owner, release, framework, tables[...]``
* table:  ``code, name, owner, isFlat, headers[...], cells[...],
            keyVariables[...], factVariables[...]``
* variable: ``code, property{id,name}, isEnumerated, enumeration{items[...]}``
* header: ``code, label, isKey, isAttribute, direction, property, context,
            keyVariableVersionId``
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dpmcore import connect
from dpmcore.server.params import ReleaseKeyword, StructureParams
from sqlalchemy import text


def _sqlite_url(db_path: str) -> str:
    """Build a SQLAlchemy SQLite URL from a filesystem path (absolute)."""
    if db_path.startswith("sqlite://"):
        return db_path
    return "sqlite:///" + str(Path(db_path).resolve())


class DpmReader:
    """Open a DPM SQLite DB and expose module/glossary reads.

    Use as a context manager so the underlying dpmcore session is closed::

        with DpmReader("input/dpm_4.2.1_20260606.db") as reader:
            module = reader.read_module("COREP_LE")
    """

    def __init__(self, db_path: str):
        self._db = connect(_sqlite_url(db_path))

    # -- lifecycle ---------------------------------------------------------
    def __enter__(self) -> "DpmReader":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def close(self) -> None:
        self._db.close()

    # -- release handling --------------------------------------------------
    @staticmethod
    def _params(
        ids: List[str],
        *,
        owners: Optional[List[str]] = None,
        release_code: Optional[str] = None,
    ) -> StructureParams:
        """Build a StructureParams. Defaults to the latest release."""
        release = None if release_code else ReleaseKeyword.LATEST
        return StructureParams(
            owners=owners or ["*"],
            ids=ids,
            release=release,
            release_code=release_code,
        )

    # -- reads -------------------------------------------------------------
    def read_module(
        self,
        code: str,
        *,
        owner: Optional[str] = None,
        release_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return one fully-populated module dict (with its ``tables`` array).

        Raises ``KeyError`` if the module/release is not found.
        """
        params = self._params(
            [code],
            owners=[owner] if owner else None,
            release_code=release_code,
        )
        rows, _total = self._db.services.structure.query_modules(
            params=params, detail="full", references="children", limit=1
        )
        if not rows:
            raise KeyError(
                f"Module {code!r} not found (owner={owner}, release={release_code})"
            )
        return rows[0]

    def list_modules(self, *, release_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return all modules (no table expansion) for discovery/CLI listing."""
        params = self._params(["*"], release_code=release_code)
        rows, _ = self._db.services.structure.query_modules(
            params=params, detail="full", references="none", limit=10_000
        )
        return rows

    def read_category(
        self, code: str, *, release_code: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Return one enumerated Category (codelist) dict, or None."""
        params = self._params([code], release_code=release_code)
        rows, _ = self._db.services.structure.query_categories(
            params=params, detail="full", limit=1
        )
        return rows[0] if rows else None

    def read_categories(
        self, codes: List[str], *, release_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Return full Category dicts (with items) for the given codes."""
        if not codes:
            return []
        params = self._params(sorted(set(codes)), release_code=release_code)
        rows, _ = self._db.services.structure.query_categories(
            params=params, detail="full", limit=len(codes) + 1
        )
        return rows

    def properties_by_id(
        self, *, release_code: Optional[str] = None
    ) -> Dict[int, Dict[str, Any]]:
        """Index every Property dict by its numeric ``id``.

        DPM variables reference a Property by id only (no code), so resolving a
        module's Concepts requires this lookup. ~3k rows; cheap to load whole.
        """
        params = self._params(["*"], release_code=release_code)
        rows, _ = self._db.services.structure.query_properties(
            params=params, detail="full", limit=1_000_000
        )
        return {r["id"]: r for r in rows}

    # -- data-definition support ------------------------------------------
    _DIMENSION_PIDS_SQL = text(
        """
        SELECT DISTINCT cc.PropertyID
        FROM TableVersionCell tvc
        JOIN VariableVersion vv ON tvc.VariableVID = vv.VariableVID
        JOIN ContextComposition cc ON vv.ContextID = cc.ContextID
        WHERE tvc.TableVID = :tvid
        """
    )
    _METRIC_PIDS_SQL = text(
        """
        SELECT DISTINCT vv.PropertyID
        FROM TableVersionCell tvc
        JOIN VariableVersion vv ON tvc.VariableVID = vv.VariableVID
        WHERE tvc.TableVID = :tvid AND vv.PropertyID IS NOT NULL
        """
    )

    def read_table_components(self, table_version_id: int) -> Tuple[List[int], List[int]]:
        """Return (dimension property ids, metric property ids) for a Table.

        Dimensions come from the union of the table's FactVariable Contexts
        (the (Property, Item) pairs that position each data point); metrics are
        the FactVariables' main Properties. Spec section 3.2.7.
        """
        session = self._db.session
        dim = [r[0] for r in session.execute(
            self._DIMENSION_PIDS_SQL, {"tvid": table_version_id}).fetchall()]
        metric = [r[0] for r in session.execute(
            self._METRIC_PIDS_SQL, {"tvid": table_version_id}).fetchall()]
        # A property used as a context dimension is not also a measure.
        dim_set = set(dim)
        metric = [p for p in metric if p not in dim_set]
        return dim, metric
