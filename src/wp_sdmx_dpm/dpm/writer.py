"""Write a new DPM SQLite database in dpmcore's ORM schema.

Materialises the SDMX->DPM mapping output (glossary dicts + a flat-table spec)
into a fresh, traversable DPM database: ``Base.metadata.create_all`` builds the
schema, then ORM rows are inserted in dependency order and committed. The
result is gated by ``connect(...).validate_schema()`` and is queryable via
dpmcore's StructureService.

Surrogate PKs are not autoincrement in the schema, so they are allocated here
from a single counter. Only PK columns are NOT NULL, so ``row_guid`` /
``owner_id`` and other optional FKs are left unset where not needed.

Scope (Phase 3b): the deterministic flat-table path (spec 3.2.6). SubCategory
restrictions (constraints) are Phase 4.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from dpmcore.orm.base import Base
from dpmcore.orm.glossary import (
    Category,
    Item,
    ItemCategory,
    Property,
    PropertyCategory,
)
from dpmcore.orm.infrastructure import DataType, Organisation, Release
from dpmcore.orm.operations import Operator
from dpmcore.orm.packaging import (
    Framework,
    Module,
    ModuleVersion,
    ModuleVersionComposition,
)
from dpmcore.orm.rendering import (
    Cell,
    Header,
    HeaderVersion,
    Table,
    TableVersion,
    TableVersionCell,
    TableVersionHeader,
)
from dpmcore.orm.variables import CompoundKey, KeyComposition, Variable, VariableVersion

from ..config import Conventions, ReviewReport

# Standard DPM data types (code -> name); Properties reference these by id.
_DPM_DATATYPES = [
    ("m", "monetary"), ("r", "decimal"), ("i", "integer"), ("p", "percentage"),
    ("b", "boolean"), ("d", "date"), ("dt", "date time"), ("es", "string"),
    ("e", "enumeration"), ("u", "URI"), ("o", "ordinals"),
]
_PROPERTIES_CATEGORY_CODE = "_PR"  # defining category that gives Properties their codes


@dataclass
class DpmWriteResult:
    out_db_path: str
    is_valid: bool = False
    tables_written: int = 0
    report: ReviewReport = field(default_factory=ReviewReport)


class DpmWriter:
    """Materialise DPM artefacts into a new SQLite DB."""

    def __init__(self, out_db_path: str, conventions: Conventions, report: ReviewReport):
        self.out_db_path = out_db_path
        self.conventions = conventions
        self.report = report
        self._session: Optional[Session] = None
        self._engine = None
        self._id = 0
        # lookup maps populated during writing
        self._datatype_id: Dict[str, int] = {}
        self._category_id: Dict[str, int] = {}
        self._property_id: Dict[str, int] = {}
        self._org_id = 1
        self._release_id = 1
        self._tables_written = 0

    # -- lifecycle ---------------------------------------------------------
    def _next(self) -> int:
        self._id += 1
        return self._id

    def create_schema(self) -> None:
        path = Path(self.out_db_path)
        if path.exists():
            path.unlink()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._engine = create_engine(f"sqlite:///{path.resolve()}")
        Base.metadata.create_all(self._engine)
        self._session = Session(self._engine)
        self._seed()

    def close(self) -> None:
        if self._session is not None:
            self._session.close()
        if self._engine is not None:
            self._engine.dispose()

    # -- seed data ---------------------------------------------------------
    def _seed(self) -> None:
        s = self._session
        agency = self.conventions.default_agency
        s.add(Organisation(org_id=self._org_id, name=agency, acronym=agency, id_prefix=agency))
        s.add(Release(
            release_id=self._release_id, code="1.0", status="Final",
            is_current=True, description="Generated from SDMX", owner_id=self._org_id,
        ))
        for code, name in _DPM_DATATYPES:
            dt_id = self._next()
            self._datatype_id[code] = dt_id
            s.add(DataType(data_type_id=dt_id, code=code, name=name, is_active=True))
        # one Operator row (validate_schema requires this table non-empty)
        s.add(Operator(operator_id=self._next(), name="equals", symbol="=", type="comparison"))
        # defining category that carries Property codes (mirrors the real "_PR")
        pr_id = self._next()
        self._category_id[_PROPERTIES_CATEGORY_CODE] = pr_id
        s.add(Category(
            category_id=pr_id, code=_PROPERTIES_CATEGORY_CODE, name="Properties",
            is_enumerated=False, is_active=True, created_release_id=self._release_id,
            owner_id=self._org_id,
        ))
        s.flush()

    # -- glossary ----------------------------------------------------------
    def write_glossary(
        self, categories: List[Dict[str, Any]], properties: List[Dict[str, Any]]
    ) -> None:
        s = self._session
        for cat in categories:
            cat_id = self._next()
            self._category_id[cat["code"]] = cat_id
            s.add(Category(
                category_id=cat_id, code=cat["code"], name=cat.get("name"),
                description=cat.get("description"), is_enumerated=True, is_active=True,
                created_release_id=self._release_id, owner_id=self._org_id,
            ))
            for item in cat.get("items") or []:
                item_id = self._next()
                s.add(Item(
                    item_id=item_id, name=item.get("name"), description=item.get("description"),
                    is_property=False, is_active=True, owner_id=self._org_id,
                ))
                s.add(ItemCategory(
                    item_id=item_id, start_release_id=self._release_id, category_id=cat_id,
                    code=item["code"], is_default_item=bool(item.get("isDefaultItem")),
                    signature=item.get("signature"),
                ))
        s.flush()

        for prop in properties:
            pid = self._next()
            self._property_id[prop["code"]] = pid
            s.add(Item(
                item_id=pid, name=prop.get("label"), description=prop.get("description"),
                is_property=True, is_active=True, owner_id=self._org_id,
            ))
            s.add(Property(
                property_id=pid, is_metric=bool(prop.get("isMetric")), is_composite=False,
                data_type_id=self._datatype_id.get(prop.get("dataTypeCode", "es")),
                period_type=prop.get("periodType"), owner_id=self._org_id,
            ))
            # the property's own code lives in an ItemCategory row of the _PR category
            s.add(ItemCategory(
                item_id=pid, start_release_id=self._release_id,
                category_id=self._category_id[_PROPERTIES_CATEGORY_CODE],
                code=prop["code"], is_default_item=False, signature=prop.get("signature"),
            ))
            # enumerated properties link to their value Category
            cat_code = prop.get("categoryCode")
            if prop.get("isEnumerated") and cat_code in self._category_id:
                s.add(PropertyCategory(
                    property_id=pid, start_release_id=self._release_id,
                    category_id=self._category_id[cat_code],
                ))
        s.flush()

    # -- flat table --------------------------------------------------------
    def write_flat_table(self, table_spec: Dict[str, Any], module_spec: Dict[str, Any]) -> None:
        s = self._session
        tbl = table_spec["table"]
        table_id = self._next()
        key_id = self._next()
        table_vid = self._next()
        s.add(Table(
            table_id=table_id, is_flat=bool(tbl.get("is_flat", True)),
            has_open_rows=bool(tbl.get("has_open_rows", True)), is_abstract=False,
            has_open_columns=False, has_open_sheets=False, is_normalised=False,
            owner_id=self._org_id,
        ))
        s.add(CompoundKey(key_id=key_id, signature=tbl["code"], owner_id=self._org_id))
        s.add(TableVersion(
            table_vid=table_vid, code=tbl["code"], name=tbl.get("name"),
            description=tbl.get("description"), table_id=table_id, key_id=key_id,
            start_release_id=self._release_id,
        ))
        s.flush()

        for comp in table_spec["components"]:
            prop_id = self._property_id.get(comp["property_code"])
            var_id = self._next()
            var_vid = self._next()
            s.add(Variable(variable_id=var_id, type=comp["variable_type"], owner_id=self._org_id))
            s.add(VariableVersion(
                variable_vid=var_vid, variable_id=var_id, property_id=prop_id,
                code=comp["code"], name=comp.get("name"), is_multi_valued=False,
                key_id=(key_id if comp["variable_type"] == "fact" else None),
                start_release_id=self._release_id,
            ))
            if comp["is_key"]:
                s.add(KeyComposition(key_id=key_id, variable_vid=var_vid))

            header_id = self._next()
            header_vid = self._next()
            s.add(Header(
                header_id=header_id, table_id=table_id, direction="C",
                is_key=bool(comp["is_key"]), is_attribute=bool(comp["is_attribute"]),
                owner_id=self._org_id,
            ))
            s.add(HeaderVersion(
                header_vid=header_vid, header_id=header_id, code=comp["code"],
                label=comp.get("name"), property_id=prop_id,
                key_variable_vid=(var_vid if comp["is_key"] else None),
                start_release_id=self._release_id,
            ))
            s.add(TableVersionHeader(
                table_vid=table_vid, header_id=header_id, header_vid=header_vid,
                order=comp["order"], parent_first=True, is_abstract=False, is_unique=True,
            ))

            # non-key components render as Cells bound to their VariableVersion
            if not comp["is_key"]:
                cell_id = self._next()
                s.add(Cell(cell_id=cell_id, table_id=table_id, column_id=header_id,
                           owner_id=self._org_id))
                s.add(TableVersionCell(
                    table_vid=table_vid, cell_id=cell_id, cell_code=comp["code"],
                    is_nullable=bool(comp["is_nullable"]), is_excluded=False, is_void=False,
                    variable_vid=var_vid,
                ))
        s.flush()

        # mandatory Module/ModuleVersion (no DPM Table exists outside a Module)
        framework_id = self._next()
        module_id = self._next()
        module_vid = self._next()
        s.add(Framework(
            framework_id=framework_id, code=module_spec["framework_code"],
            name=module_spec.get("framework_name"), owner_id=self._org_id,
        ))
        s.add(Module(module_id=module_id, framework_id=framework_id, owner_id=self._org_id))
        s.add(ModuleVersion(
            module_vid=module_vid, module_id=module_id, code=module_spec["code"],
            name=module_spec.get("name"), version_number=module_spec.get("version_number"),
            start_release_id=self._release_id, is_reported=True,
        ))
        s.add(ModuleVersionComposition(
            module_vid=module_vid, table_id=table_id, table_vid=table_vid, order=10,
        ))
        s.flush()
        self._tables_written += 1

    # -- finalise ----------------------------------------------------------
    def finalise(self) -> DpmWriteResult:
        self._session.commit()
        from dpmcore import connect
        with connect(f"sqlite:///{Path(self.out_db_path).resolve()}") as db:
            is_valid = bool(db.validate_schema().is_valid)
        return DpmWriteResult(
            out_db_path=self.out_db_path, is_valid=is_valid,
            tables_written=self._tables_written, report=self.report,
        )
