"""
Storage backend adapter for EzDB RDBMS.
Provides unified interface for different storage backends (JSON, SQLite, PostgreSQL).
"""

from typing import Any, Dict, List, Optional
from .schema import TableSchema
from .storage import TableStore as JSONTableStore


class StorageBackend:
    """Base class for storage backends"""

    def create_table(self, table_name: str, schema: TableSchema):
        """Create a new table"""
        raise NotImplementedError

    def drop_table(self, table_name: str):
        """Drop a table"""
        raise NotImplementedError

    def insert(self, table_name: str, row_data: Dict[str, Any]) -> int:
        """Insert a row and return row ID"""
        raise NotImplementedError

    def insert_batch(self, table_name: str, rows: List[Dict[str, Any]]) -> List[int]:
        """Insert multiple rows"""
        raise NotImplementedError

    def get(self, table_name: str, row_id: int) -> Optional[Dict[str, Any]]:
        """Get a row by ID"""
        raise NotImplementedError

    def update(self, table_name: str, row_id: int, updates: Dict[str, Any]) -> bool:
        """Update a row"""
        raise NotImplementedError

    def delete(self, table_name: str, row_id: int) -> bool:
        """Delete a row"""
        raise NotImplementedError

    def scan(self, table_name: str, where: Optional[callable] = None,
             limit: Optional[int] = None, offset: int = 0) -> List[tuple]:
        """Scan table with optional filter"""
        raise NotImplementedError

    def count(self, table_name: str, where: Optional[callable] = None) -> int:
        """Count rows"""
        raise NotImplementedError

    def size(self, table_name: str) -> int:
        """Get total number of rows"""
        raise NotImplementedError

    def get_table(self, table_name: str):
        """Get table reference"""
        raise NotImplementedError

    def list_tables(self) -> List[str]:
        """List all table names"""
        raise NotImplementedError

    def close(self):
        """Close connections"""
        pass


class JSONStorageBackend(StorageBackend):
    """
    JSON-based in-memory storage backend.
    Current implementation - works for < 10K records.
    """

    def __init__(self):
        self.tables: Dict[str, JSONTableStore] = {}

    def create_table(self, table_name: str, schema: TableSchema):
        table_store = JSONTableStore(schema)
        self.tables[table_name] = table_store
        return table_store

    def drop_table(self, table_name: str):
        if table_name in self.tables:
            del self.tables[table_name]

    def insert(self, table_name: str, row_data: Dict[str, Any]) -> int:
        table = self.tables.get(table_name)
        if not table:
            raise ValueError(f"Table '{table_name}' does not exist")
        return table.insert(row_data)

    def insert_batch(self, table_name: str, rows: List[Dict[str, Any]]) -> List[int]:
        table = self.tables.get(table_name)
        if not table:
            raise ValueError(f"Table '{table_name}' does not exist")
        return table.insert_batch(rows)

    def get(self, table_name: str, row_id: int) -> Optional[Dict[str, Any]]:
        table = self.tables.get(table_name)
        if not table:
            return None
        return table.get(row_id)

    def update(self, table_name: str, row_id: int, updates: Dict[str, Any]) -> bool:
        table = self.tables.get(table_name)
        if not table:
            return False
        return table.update(row_id, updates)

    def delete(self, table_name: str, row_id: int) -> bool:
        table = self.tables.get(table_name)
        if not table:
            return False
        return table.delete(row_id)

    def scan(self, table_name: str, where: Optional[callable] = None,
             limit: Optional[int] = None, offset: int = 0) -> List[tuple]:
        table = self.tables.get(table_name)
        if not table:
            return []
        return table.scan(where, limit, offset)

    def count(self, table_name: str, where: Optional[callable] = None) -> int:
        table = self.tables.get(table_name)
        if not table:
            return 0
        return table.count(where)

    def size(self, table_name: str) -> int:
        table = self.tables.get(table_name)
        if not table:
            return 0
        return table.size()

    def get_table(self, table_name: str):
        return self.tables.get(table_name)

    def list_tables(self) -> List[str]:
        return list(self.tables.keys())


class SQLiteStorageBackend(StorageBackend):
    """
    SQLite-based storage backend.
    Production-ready implementation for 10K-10M records.
    """

    def __init__(self, db_path: str):
        from .storage_sqlite import SQLiteTableStore
        self.db_path = db_path
        self.store = SQLiteTableStore(db_path)
        self.schemas: Dict[str, TableSchema] = {}  # Cache schemas

    def create_table(self, table_name: str, schema: TableSchema):
        # Convert schema to SQLite format
        schema_dict = schema.to_dict()
        self.store.create_table(table_name, schema_dict)
        self.schemas[table_name] = schema

    def drop_table(self, table_name: str):
        self.store.drop_table(table_name)
        if table_name in self.schemas:
            del self.schemas[table_name]

    def insert(self, table_name: str, row_data: Dict[str, Any]) -> int:
        return self.store.insert(table_name, row_data)

    def insert_batch(self, table_name: str, rows: List[Dict[str, Any]]) -> List[int]:
        return self.store.insert_batch(table_name, rows)

    def get(self, table_name: str, row_id: int) -> Optional[Dict[str, Any]]:
        results = self.store.select(table_name, where="rowid=?", params=[row_id], limit=1)
        return results[0] if results else None

    def update(self, table_name: str, row_id: int, updates: Dict[str, Any]) -> bool:
        return self.store.update(table_name, row_id, updates)

    def delete(self, table_name: str, row_id: int) -> bool:
        count = self.store.delete(table_name, where="rowid=?", params=[row_id])
        return count > 0

    def scan(self, table_name: str, where: Optional[callable] = None,
             limit: Optional[int] = None, offset: int = 0) -> List[tuple]:
        # SQLite doesn't support callable where clauses directly
        # Return all rows and filter in memory (for compatibility)
        rows = self.store.select(table_name, limit=limit, offset=offset)

        results = []
        for i, row in enumerate(rows):
            if where is None or where(row):
                # Return (row_id, row) tuple
                results.append((offset + i, row))

        return results

    def count(self, table_name: str, where: Optional[callable] = None) -> int:
        if where is None:
            return self.store.count(table_name)
        else:
            # Fallback to scanning for callable where
            rows = self.store.select(table_name)
            return sum(1 for row in rows if where(row))

    def size(self, table_name: str) -> int:
        return self.store.count(table_name)

    def get_table(self, table_name: str):
        # Return a wrapper object for compatibility with existing code
        # If schema not cached, try to get it from the database
        if table_name not in self.schemas and table_name in self.list_tables():
            schema_dict = self.store.get_table_schema(table_name)
            # Convert to TableSchema object
            from .schema import TableSchema, Column, DataType
            columns = []
            for col_name, col_info in schema_dict['columns'].items():
                col = Column(
                    name=col_name,
                    data_type=DataType.from_string(col_info['type']),
                    nullable=col_info.get('not_null', False) == False,
                    primary_key=col_info.get('primary_key', False)
                )
                columns.append(col)
            self.schemas[table_name] = TableSchema(table_name, columns)

        return SQLiteTableWrapper(table_name, self.store, self.schemas.get(table_name))

    def list_tables(self) -> List[str]:
        return self.store.get_all_tables()

    def close(self):
        self.store.close()


class SQLiteTableWrapper:
    """
    Wrapper to make SQLite storage compatible with existing JSONTableStore interface.
    """

    def __init__(self, table_name: str, store, schema: Optional[TableSchema]):
        self.table_name = table_name
        self.store = store
        self.schema = schema
        self._next_auto_increment = 1
        self._rows_cache = None  # Cache for rows property

    @property
    def rows(self):
        """Fetch rows from SQLite on demand"""
        # Always fetch fresh data from SQLite
        return self.get_all_rows()

    def insert(self, row_data: Dict[str, Any]) -> int:
        return self.store.insert(self.table_name, row_data)

    def insert_batch(self, rows: List[Dict[str, Any]]) -> List[int]:
        return self.store.insert_batch(self.table_name, rows)

    def _cast_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Cast row values to proper types based on schema"""
        if not self.schema or not hasattr(self.schema, 'columns'):
            return row

        casted_row = {}
        for col in self.schema.columns:
            if col.name in row:
                casted_row[col.name] = col.cast_value(row[col.name])
            else:
                casted_row[col.name] = None

        # Include any columns not in schema (shouldn't happen but be safe)
        for key in row:
            if key not in casted_row:
                casted_row[key] = row[key]

        return casted_row

    def get(self, row_id: int) -> Optional[Dict[str, Any]]:
        results = self.store.select(self.table_name, where="rowid=?", params=[row_id], limit=1)
        if results:
            return self._cast_row(results[0])
        return None

    def update(self, row_id: int, updates: Dict[str, Any]) -> bool:
        return self.store.update(self.table_name, row_id, updates)

    def delete(self, row_id: int) -> bool:
        count = self.store.delete(self.table_name, where="rowid=?", params=[row_id])
        return count > 0

    def scan(self, where: Optional[callable] = None,
             limit: Optional[int] = None, offset: int = 0) -> List[tuple]:
        # For SQLite, we need to fetch actual rowids
        # Use raw SQL to get rowid along with row data
        import sqlite3
        sql = f"SELECT rowid, * FROM {self.table_name}"
        if limit:
            sql += f" LIMIT {limit}"
        if offset:
            sql += f" OFFSET {offset}"

        cursor = self.store.conn.execute(sql)
        results = []
        for row in cursor.fetchall():
            # First column is rowid, rest is row data
            rowid = row[0]
            # Get column names (excluding rowid)
            col_names = [desc[0] for desc in cursor.description[1:]]
            row_dict = dict(zip(col_names, row[1:]))

            # Cast row values to proper types
            row_dict = self._cast_row(row_dict)

            if where is None or where(row_dict):
                results.append((rowid, row_dict))

        return results

    def count(self, where: Optional[callable] = None) -> int:
        if where is None:
            return self.store.count(self.table_name)
        else:
            rows = self.store.select(self.table_name)
            return sum(1 for row in rows if where(row))

    def size(self) -> int:
        return self.store.count(self.table_name)

    def get_all_rows(self) -> List[Dict[str, Any]]:
        rows = self.store.select(self.table_name)
        return [self._cast_row(row) for row in rows]
