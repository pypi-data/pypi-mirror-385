from typing import Any, Dict, List, Tuple, Union, Type
from .fields import FieldDescriptor
from .table import Table

TableLike = Union[str, Type[Table]]


class ViewField(FieldDescriptor):
    def __init__(self, *, table: str, field: str):
        super().__init__(sql_type="TEXT")
        self._view_src_table = table
        self._view_src_field = field

    def to_dict(self) -> Dict:
        """Serialize ViewField to dictionary"""
        data = super().to_dict()
        data['view_src_table'] = self._view_src_table
        data['view_src_field'] = self._view_src_field
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'ViewField':
        """Deserialize ViewField from dictionary"""
        return cls(
            table=data['view_src_table'],
            field=data['view_src_field']
        )


Field = ViewField


class View(Table):
    __tablename__ = "__view__"  # Views don't create tables, but Table metaclass requires this
    __viewname__: str = ""
    __tables__: Tuple[TableLike, ...] = ()

    @classmethod
    def _table_name(cls, t: TableLike) -> str:
        return t if isinstance(t, str) else t.__tablename__

    @classmethod
    def _collect_view_columns(cls) -> List[Tuple[str, str]]:
        cols: List[Tuple[str, str]] = []
        for alias, desc in cls.get_fields().items():
            src_t = getattr(desc, "_view_src_table", None)
            src_c = getattr(desc, "_view_src_field", None)
            if not (src_t and src_c):
                raise ValueError(
                    f"View '{cls.__viewname__}': field '{alias}' must be defined as Field(table='...', field='...')"
                )
            cols.append((f"`{src_t}`.`{src_c}`", alias))
        if not cols:
            raise ValueError(f"View '{cls.__viewname__}' must expose at least one field.")
        return cols

    @classmethod
    def _resolve_join_chain(cls, schema) -> Tuple[str, List[str]]:
        if not cls.__tables__:
            raise ValueError(f"View '{cls.__viewname__}' must declare __tables__")

        wanted: List[str] = [cls._table_name(t) for t in cls.__tables__]

        def pk_field(table_name: str) -> str:
            for name, fd in schema.get_table(table_name).get_fields().items():
                if fd.primary_key:
                    return name
            raise ValueError(f"Table '{table_name}' has no primary key")

        edges = []
        for A in wanted:
            A_fields = schema.get_table(A).get_fields()
            for col, fd in A_fields.items():
                if fd.foreign_key:
                    tgt_table, tgt_col = (
                        fd.foreign_key.split(".", 1) if "." in fd.foreign_key else (fd.foreign_key, "id")
                    )
                    edges.append((A, col, tgt_table, tgt_col))
                    edges.append((tgt_table, tgt_col, A, col))

        joined = [wanted[0]]
        joins: List[str] = []
        while len(joined) < len(wanted):
            remaining = [t for t in wanted if t not in joined]
            progress = False
            for R in remaining:
                candidates = []
                for (L, Lc, Rt, Rc) in edges:
                    if Rt == R and L in joined:
                        candidates.append((L, Lc, Rt, Rc))
                if not candidates:
                    continue
                if len(candidates) > 1:
                    # Prefer FK from the most recently joined table (most direct path)
                    candidates.sort(key=lambda c: joined.index(c[0]), reverse=True)
                (L, Lc, Rt, Rc) = candidates[0]
                joins.append(f"LEFT JOIN `{Rt}` ON `{L}`.`{Lc}` = `{Rt}`.`{Rc}`")
                joined.append(R)
                progress = True
            if not progress:
                missing = [t for t in wanted if t not in joined]
                raise ValueError(
                    f"View '{cls.__viewname__}': cannot connect tables {missing} from base {joined[0]}. "
                    f"Ensure there is an FK path between them."
                )

        base = f"`{joined[0]}`"
        return base, joins

    @classmethod
    def type_map(cls, schema) -> Dict[str, FieldDescriptor]:
        """
        Map each alias to the underlying FieldDescriptor from the source table.

        Args:
            schema: Schema instance to resolve table references

        Returns:
            Dict mapping alias names to their underlying FieldDescriptors
        """
        mp = {}
        for alias, v in cls.get_fields().items():
            src_t = getattr(v, "_view_src_table", None)
            src_c = getattr(v, "_view_src_field", None)
            if not (src_t and src_c):
                raise ValueError(
                    f"View '{cls.__viewname__}': field '{alias}' must be Field(table=..., field=...)"
                )
            fd = schema.get_table(src_t).get_fields()[src_c]
            mp[alias] = fd
        return mp

    @classmethod
    def generate_create_sql(cls) -> str:
        if not cls.__viewname__:
            raise ValueError(f"View class '{cls.__name__}' must set __viewname__")
        if not hasattr(cls, "__bound_schema__") or cls.__bound_schema__ is None:
            raise RuntimeError(f"View '{cls.__viewname__}' is not bound to a Schema")

        cols = cls._collect_view_columns()
        base, joins = cls._resolve_join_chain(cls.__bound_schema__)

        # IMPORTANT: Views used with vector_search() must expose an 'id' field that maps
        # to the underlying table's primary key. This is required because:
        # 1. Vector stores are keyed by the underlying table's primary key
        # 2. Filtered vector search needs to map view row IDs to underlying table IDs
        # 3. The query builder assumes view IDs match the source table IDs for filtering
        #
        # Example: id = Field(table="filing_chunks", field="id")
        #
        # Verify that 'id' field exists and points to source table's primary key
        fields = cls.get_fields()
        if 'id' in fields:
            id_field = fields['id']
            src_table = getattr(id_field, '_view_src_table', None)
            src_field = getattr(id_field, '_view_src_field', None)
            if src_table and src_field:
                # Verify the source field is actually the primary key
                src_table_cls = cls.__bound_schema__.get_table(src_table)
                src_table_fields = src_table_cls.get_fields()
                if src_field in src_table_fields:
                    if not src_table_fields[src_field].primary_key:
                        raise ValueError(
                            f"View '{cls.__viewname__}': 'id' field maps to '{src_table}.{src_field}' "
                            f"which is not a primary key. Views must map 'id' to the underlying table's primary key "
                            f"for vector_search() compatibility."
                        )

        select_list = ", ".join([f"{expr} AS `{alias}`" for expr, alias in cols])
        join_sql = " ".join(joins)
        sql = (
            f"CREATE VIEW IF NOT EXISTS `{cls.__viewname__}` AS "
            f"SELECT {select_list} FROM {base} {join_sql};"
        )
        return sql

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Serialize view to dictionary"""
        # Serialize fields (ViewFields)
        fields_dict = {}
        for name, field in cls.get_fields().items():
            fields_dict[name] = field.to_dict()

        # Serialize table references (convert Table classes to strings)
        tables_list = []
        for t in cls.__tables__:
            if isinstance(t, str):
                tables_list.append(t)
            else:
                tables_list.append(t.__tablename__)

        return {
            'viewname': cls.__viewname__,
            'tables': tables_list,
            'fields': fields_dict,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Type['View']:
        """Deserialize view from dictionary"""
        viewname = data['viewname']
        tables = tuple(data['tables'])  # Keep as strings, will be resolved at runtime

        # Reconstruct ViewField instances
        fields_dict = {}
        for field_name, field_data in data['fields'].items():
            fields_dict[field_name] = ViewField.from_dict(field_data)

        # Dynamically create View class
        view_cls = type(
            viewname,
            (View,),
            {
                '__viewname__': viewname,
                '__tables__': tables,
                **fields_dict
            }
        )

        return view_cls
