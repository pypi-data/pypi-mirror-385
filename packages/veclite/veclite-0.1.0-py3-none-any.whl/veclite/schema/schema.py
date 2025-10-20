import json
import hashlib
from typing import Dict, Any, Type, List, Union

from .table import Table

TYPE_CHECKING = True
if TYPE_CHECKING:
    from .builder import TableBuilder


class Schema:
    """Central schema manager for tables - core table management only."""

    def __init__(self):
        self.tables: Dict[str, Type[Table]] = {}
        self.views: Dict[str, Type[Table]] = {}

        # SQLite keywords (case-insensitive)
        self._reserved_words = {
            'abort', 'action', 'add', 'after', 'all', 'alter', 'analyze', 'and', 'as', 'asc',
            'attach', 'autoincrement', 'before', 'begin', 'between', 'by', 'cascade', 'case',
            'cast', 'check', 'collate', 'column', 'commit', 'conflict', 'constraint', 'create',
            'cross', 'current_date', 'current_time', 'current_timestamp', 'database', 'default',
            'deferrable', 'deferred', 'delete', 'desc', 'detach', 'distinct', 'drop', 'each',
            'else', 'end', 'escape', 'except', 'exclusive', 'exists', 'explain', 'fail', 'for',
            'foreign', 'from', 'full', 'glob', 'group', 'having', 'if', 'ignore', 'immediate',
            'in', 'index', 'indexed', 'initially', 'inner', 'insert', 'instead', 'intersect',
            'into', 'is', 'isnull', 'join', 'key', 'left', 'like', 'limit', 'match', 'natural',
            'no', 'not', 'notnull', 'null', 'of', 'offset', 'on', 'or', 'order', 'outer', 'plan',
            'pragma', 'primary', 'query', 'raise', 'recursive', 'references', 'regexp', 'reindex',
            'release', 'rename', 'replace', 'restrict', 'right', 'rollback', 'row', 'savepoint',
            'select', 'set', 'table', 'temp', 'temporary', 'then', 'to', 'transaction', 'trigger',
            'union', 'unique', 'update', 'using', 'vacuum', 'values', 'view', 'virtual', 'when',
            'where', 'with', 'without'
        }

        # Engine-reserved names (case-insensitive): block user tables/views from colliding
        # Note: _sys_* prefix is also reserved for future engine tables
        self._reserved_names = {
            'vector_outbox',  # async embedding retry outbox
            # Add more engine tables here as needed, e.g.:
            # '_sys_migrations', '_sys_vectors_meta'
        }

    def add_table(self, table: Union[Type[Table], 'TableBuilder']) -> None:
        if hasattr(table, 'build'):
            from .builder import TableBuilder
            if isinstance(table, TableBuilder):
                table_cls = table.build()
            else:
                table_cls = table
        else:
            table_cls = table

        name = table_cls.__tablename__
        lname = name.lower()

        if name in self.tables:
            raise ValueError(f"Table '{name}' already added.")

        if self._is_reserved_word(lname):
            raise ValueError(
                f"Table name '{name}' is a SQLite reserved word. "
                f"Choose a different name."
            )

        if self._is_reserved_name(lname):
            raise ValueError(
                f"Table name '{name}' is reserved by the engine. "
                f"Choose a different name (avoid 'vector_outbox' and '_sys_*' prefix)."
            )

        self.tables[name] = table_cls

    def add_view(self, view: Type[Table]) -> None:
        name = view.__viewname__
        lname = name.lower()

        if name in self.views:
            raise ValueError(f"View '{name}' already added.")

        if self._is_reserved_word(lname):
            raise ValueError(
                f"View name '{name}' is a SQLite reserved word. "
                f"Choose a different name."
            )

        if self._is_reserved_name(lname):
            raise ValueError(
                f"View name '{name}' is reserved by the engine. "
                f"Choose a different name (avoid 'vector_outbox' and '_sys_*' prefix)."
            )

        self.views[name] = view

    def drop_view(self, view_name: str) -> None:
        """Remove a view from the schema.

        Args:
            view_name: Name of the view to remove

        Raises:
            ValueError: If view doesn't exist
        """
        if view_name not in self.views:
            raise ValueError(f"View '{view_name}' not found in schema.")

        del self.views[view_name]

    def _is_reserved_word(self, lname: str) -> bool:
        """Check if a name is a SQLite reserved word (expects lowercased input)."""
        return lname in self._reserved_words

    def _is_reserved_name(self, lname: str) -> bool:
        """Check if a name is reserved by the engine (expects lowercased input).

        Reserved names include:
        - Explicit names in _reserved_names set (e.g., 'vector_outbox')
        - Any name starting with '_sys_' prefix (reserved for future engine tables)
        """
        return lname in self._reserved_names or lname.startswith('_sys_')

    def reserve_names(self, names: set) -> None:
        """Allow extensions to register additional reserved names.

        Args:
            names: Set of lowercase table/view names to reserve
        """
        self._reserved_names.update(names)

    def get_table(self, name: str) -> Type[Table]:
        if name not in self.tables:
            raise ValueError(f"Table '{name}' not found in schema.")
        return self.tables[name]

    def update_table(self, table_cls: Type[Table]) -> None:
        """Update with modified table (e.g., after add_field)."""
        self.tables[table_cls.__tablename__] = table_cls

    def generate_all_sql(self) -> str:
        """Generate SQL for all tables; validate FKs.

        Also blocks engine-reserved names (helps catch legacy snapshots that
        accidentally included system tables like 'vector_outbox').
        """
        # Sanity check: block engine-reserved names if present
        for table_name in self.tables.keys():
            if self._is_reserved_name(table_name.lower()):
                raise ValueError(
                    f"Schema includes reserved table '{table_name}'. "
                    f"Remove or rename it (avoid 'vector_outbox' and '_sys_*' prefix)."
                )

        for view_name in self.views.keys():
            if self._is_reserved_name(view_name.lower()):
                raise ValueError(
                    f"Schema includes reserved view '{view_name}'. "
                    f"Remove or rename it (avoid 'vector_outbox' and '_sys_*' prefix)."
                )

        all_sql = []

        for table_cls in self.tables.values():
            for name, field in table_cls.get_fields().items():
                if field.foreign_key:
                    ref_table_name, ref_field = field.foreign_key.rsplit('.', 1) if '.' in field.foreign_key else (
                        field.foreign_key, 'id')
                    ref_table = self.tables.get(ref_table_name)

                    if not ref_table:
                        raise ValueError(f"FK target table '{ref_table_name}' not in schema.")
                    ref_fields = ref_table.get_fields()

                    if ref_field not in ref_fields:
                        raise ValueError(f"FK target field '{ref_field}' not in {ref_table_name}.")
                    ref = ref_fields[ref_field]

                    if not ref.primary_key:
                        raise ValueError(f"FK must reference PK/Serial: {ref_table_name}.{ref_field} is not PK.")

                    if ref.sql_type != field.sql_type:
                        raise ValueError(f"FK type mismatch: {field.sql_type} vs {ref.sql_type}.")

        for table_cls in self.tables.values():
            sql = table_cls.generate_create_sql()
            all_sql.append(sql)

        for view_cls in self.views.values():
            view_cls.__bound_schema__ = self
            sql = view_cls.generate_create_sql()
            all_sql.append(sql)

        return "\n".join(all_sql)

    def table(self, name: str, collection=None) -> Type[Table]:
        """Get table class for operations"""
        table_cls = self.get_table(name)
        table_instance = table_cls()
        table_instance._schema = self
        table_instance._collection = collection
        return table_instance

    def view(self, name: str) -> Type[Table]:
        """Get view class for operations"""
        if name not in self.views:
            raise ValueError(f"View '{name}' not found in schema.")
        view_cls = self.views[name]
        view_instance = view_cls()
        view_instance._schema = self
        return view_instance

    def to_dict(self) -> Dict[str, Any]:
        """Serialize entire schema to dictionary"""
        return {
            'tables': {
                name: table_cls.to_dict()
                for name, table_cls in self.tables.items()
            },
            'views': {
                name: view_cls.to_dict()
                for name, view_cls in self.views.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schema':
        """Recreate schema from dictionary"""
        from .view import View

        schema = cls()

        for table_name, table_data in data['tables'].items():
            table_cls = Table.from_dict(table_data)
            schema.add_table(table_cls)

        # Add views if present
        for view_name, view_data in data.get('views', {}).items():
            view_cls = View.from_dict(view_data)
            schema.add_view(view_cls)

        return schema

    def validate_insert_data(self, table_name: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Validate insert data against schema"""
        table_instance = self.table(table_name)

        if isinstance(data, list):
            return [table_instance.validate_insert_data(item) for item in data]
        else:
            return table_instance.validate_insert_data(data)

    def validate_update_data(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate update data against schema"""
        table_instance = self.table(table_name)
        return table_instance.validate_update_data(data)
    
    def get_schema_hash(self) -> str:
        """Generate hash of global schema in snapshot format for comparison"""
        # Convert schema to same format as namespace snapshots: {table_name: [pragma_table_info_rows]}
        snapshot_format = {}
        
        for table_name, table_cls in self.tables.items():
            table_info = []
            fields = table_cls.get_fields()
            
            # Convert each field to PRAGMA table_info format
            for field_name, field_desc in fields.items():
                table_info.append({
                    "name": field_name,
                    "type": field_desc.sql_type,
                    "notnull": 1 if not field_desc.nullable else 0,
                    "dflt_value": field_desc.default,
                    "pk": 1 if field_desc.primary_key else 0
                })
            
            snapshot_format[table_name] = table_info
        
        # Sort keys for deterministic hashing - must match namespace snapshot hashing
        serialized = json.dumps(snapshot_format, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()
