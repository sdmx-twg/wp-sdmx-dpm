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

    def read_all_categories(
        self, *, release_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Return every Category dict (with items), independent of any module.

        Used by the module-independent glossary export so that importing a
        Codelist brings the *whole* value domain, not just the slice a module
        happens to reference. ~150 rows; cheap to load whole.
        """
        params = self._params(["*"], release_code=release_code)
        rows, _ = self._db.services.structure.query_categories(
            params=params, detail="full", limit=1_000_000
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

    # -- hierarchy support (SubCategory parent-child trees) ----------------
    # A SubCategory is a versioned subset of a Category's Items. When its Items
    # carry parent-child links (``SubCategoryItem.ParentItemID``), the SubCategory
    # is a *hierarchy* over the Category's Codelist and maps to an SDMX Hierarchy
    # (glossary detailed rules section 3.4.3). The current version of each
    # SubCategory is the one whose ``SubCategoryVersion`` is still open
    # (``EndReleaseID IS NULL``); item codes/names are resolved against the
    # parent Category's current ``ItemCategory`` rows.
    _HIERARCHIES_SQL = text(
        """
        SELECT c.Code        AS cat_code,
               sc.SubCategoryID AS sub_id,
               sc.Code        AS sub_code,
               sc.Name        AS sub_name,
               sc.Description AS sub_desc,
               sci.ItemID     AS item_id,
               sci.ParentItemID AS parent_item_id,
               sci."Order"    AS ord,
               sci.Label      AS label,
               ic.Code        AS item_code,
               i.Name         AS item_name
        FROM SubCategory sc
        JOIN Category c            ON c.CategoryID = sc.CategoryID
        JOIN SubCategoryVersion scv ON scv.SubCategoryID = sc.SubCategoryID
                                   AND scv.EndReleaseID IS NULL
        JOIN SubCategoryItem sci   ON sci.SubCategoryVID = scv.SubCategoryVID
        JOIN Item i                ON i.ItemID = sci.ItemID
        LEFT JOIN ItemCategory ic  ON ic.ItemID = sci.ItemID
                                  AND ic.CategoryID = sc.CategoryID
                                  AND ic.EndReleaseID IS NULL
        WHERE c.IsEnumerated = 1
        ORDER BY c.Code, sc.SubCategoryID, sci."Order"
        """
    )

    def read_hierarchies(
        self, category_codes: Optional[List[str]] = None, *, release_code: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Return hierarchical SubCategories grouped by their Category code.

        Only SubCategories whose Items carry at least one parent-child link are
        returned (flat subsets are not hierarchies). Each entry is a dict::

            {"code", "name", "description", "categoryCode",
             "items": [{"code", "parentCode", "name", "label", "order"}, ...]}

        ``category_codes`` restricts the result to those Categories (the
        module-driven path passes the codelists it emits); ``None`` returns the
        hierarchies of every enumerated Category (the whole-glossary path).

        Note: this reads the *current* (open) SubCategory version regardless of
        ``release_code`` -- per-release hierarchy history is not yet wired up.
        """
        wanted = set(category_codes) if category_codes is not None else None
        rows = self._db.session.execute(self._HIERARCHIES_SQL).fetchall()

        # Group rows by SubCategory, preserving DPM order.
        by_sub: Dict[int, Dict[str, Any]] = {}
        for r in rows:
            if wanted is not None and r.cat_code not in wanted:
                continue
            sub = by_sub.get(r.sub_id)
            if sub is None:
                sub = by_sub[r.sub_id] = {
                    "code": r.sub_code,
                    "name": r.sub_name,
                    "description": r.sub_desc,
                    "categoryCode": r.cat_code,
                    "_rows": [],
                }
            sub["_rows"].append(r)

        result: Dict[str, List[Dict[str, Any]]] = {}
        for sub in by_sub.values():
            subrows = sub.pop("_rows")
            # Resolve item ids -> codes within this SubCategory so parent links
            # (which point at ItemIDs) can be expressed as parent *codes*.
            code_by_item = {r.item_id: r.item_code for r in subrows if r.item_code}
            if not any(r.parent_item_id is not None for r in subrows):
                continue  # flat subset, not a hierarchy
            items = []
            for r in subrows:
                if not r.item_code:
                    continue  # item not in the current codelist; skip
                parent_code = code_by_item.get(r.parent_item_id) if r.parent_item_id else None
                items.append(
                    {
                        "code": r.item_code,
                        "parentCode": parent_code,
                        "name": r.item_name,
                        "label": r.label,
                        "order": r.ord,
                    }
                )
            if not items:
                continue
            sub["items"] = items
            result.setdefault(sub["categoryCode"], []).append(sub)
        return result

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
