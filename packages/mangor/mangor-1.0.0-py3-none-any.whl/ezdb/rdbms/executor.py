"""
Query executor for EzDB RDBMS
Executes parsed SQL queries using query operators
"""

import json
import os
import re
from typing import Any, Dict, List, Optional
from .parser import (
    ParsedQuery, CreateTableQuery, DropTableQuery, InsertQuery,
    SelectQuery, UpdateQuery, DeleteQuery, DescribeQuery,
    CreateViewQuery, DropViewQuery, CreateSequenceQuery,
    DropSequenceQuery, AlterSequenceQuery, CreateTriggerQuery,
    DropTriggerQuery, RDBMSParser
)
from .schema import TableSchema, DataType, Column
from .storage import TableStore
from .operators import (
    ScanOperator, FilterOperator, ProjectOperator, SortOperator,
    LimitOperator, NestedLoopJoinOperator, HashJoinOperator,
    AggregateOperator, build_predicate_from_where
)
from .system_catalog import SystemCatalog
from .auto_vectorization import AutoVectorizer
from .sequence_manager import SequenceManager


class RDBMSEngine:
    """Main RDBMS engine managing tables and executing queries"""

    def __init__(self, db_file: Optional[str] = None, auto_vectorization: bool = True,
                 backend: str = 'auto'):
        """
        Initialize RDBMS engine.

        Args:
            db_file: Optional path to database file for persistence
            auto_vectorization: Enable automatic vector indexing (default: True)
            backend: Storage backend ('auto', 'json', 'sqlite').
                    'auto' selects based on file extension:
                    - .json → JSON backend
                    - .db or .sqlite → SQLite backend
                    - default → JSON backend
        """
        self.views: Dict[str, str] = {}  # Store view definitions (view_name -> select_query)
        self.sequences = SequenceManager()  # Sequence manager
        self.parser = RDBMSParser()
        self.catalog = SystemCatalog()  # System catalog for ALL_OBJECTS, etc.
        self.default_owner = 'PUBLIC'  # Default schema owner
        self.db_file = db_file

        # Determine backend
        if backend == 'auto':
            if db_file:
                if db_file.endswith('.db') or db_file.endswith('.sqlite'):
                    backend = 'sqlite'
                else:
                    backend = 'json'
            else:
                backend = 'json'

        self.backend_type = backend

        # Initialize storage backend
        from .storage_adapter import JSONStorageBackend, SQLiteStorageBackend

        if backend == 'sqlite':
            # Use SQLite backend
            sqlite_path = db_file if db_file else ':memory:'
            if db_file and db_file.endswith('.json'):
                # Replace .json with .db
                sqlite_path = db_file.replace('.json', '.db')
            self.storage = SQLiteStorageBackend(sqlite_path)
            print(f"Using SQLite backend: {sqlite_path}")
        else:
            # Use JSON backend (default)
            self.storage = JSONStorageBackend()
            if backend == 'json':
                print(f"Using JSON backend")

        # Keep tables reference for backward compatibility
        # For JSON backend, this points to storage.tables
        # For SQLite backend, this is managed through the adapter
        if backend == 'json':
            self.tables = self.storage.tables
        else:
            # For SQLite, create a property that maps to storage
            self._storage_backend = self.storage

        # Initialize auto-vectorization
        self.auto_vectorizer = None
        if auto_vectorization:
            self.auto_vectorizer = AutoVectorizer(
                ezdb_instance=None,  # TODO: Pass actual EzDB instance for vector storage
                embedding_model='sentence-transformers/all-MiniLM-L6-v2',
                dimension=384
            )

        # Load from file if it exists
        if db_file and os.path.exists(db_file):
            self.load_from_file(db_file)

    @property
    def tables(self):
        """Property to provide backward compatibility for table access"""
        if self.backend_type == 'json':
            return self.storage.tables
        else:
            # For SQLite, create a dict-like wrapper
            class TableDict:
                def __init__(self, storage):
                    self.storage = storage

                def __getitem__(self, key):
                    return self.storage.get_table(key)

                def __contains__(self, key):
                    return key in self.storage.list_tables()

                def __setitem__(self, key, value):
                    # This is handled by create_table
                    pass

                def __delitem__(self, key):
                    self.storage.drop_table(key)

                def get(self, key, default=None):
                    try:
                        return self.storage.get_table(key)
                    except:
                        return default

                def keys(self):
                    return self.storage.list_tables()

                def items(self):
                    return [(name, self.storage.get_table(name))
                            for name in self.storage.list_tables()]

            return TableDict(self.storage)

    @tables.setter
    def tables(self, value):
        """Setter for backward compatibility"""
        if self.backend_type == 'json':
            self.storage.tables = value

    def execute(self, sql: str) -> Dict[str, Any]:
        """
        Execute a SQL statement or PL/SQL block.

        Args:
            sql: SQL statement string or PL/SQL block

        Returns:
            Result dictionary with query results or status

        Raises:
            ValueError: If SQL is invalid
        """
        # Check if this is a PL/SQL block or procedure/function definition
        sql_stripped = sql.strip()
        sql_upper = sql_stripped.upper()

        # Check for PL/SQL statements
        is_plsql = (sql_upper.startswith('DECLARE') or
                   sql_upper.startswith('BEGIN') or
                   sql_upper.startswith('CREATE PROCEDURE') or
                   sql_upper.startswith('CREATE FUNCTION') or
                   sql_upper.startswith('CREATE PACKAGE') or
                   sql_upper.startswith('CREATE OR REPLACE PROCEDURE') or
                   sql_upper.startswith('CREATE OR REPLACE FUNCTION') or
                   sql_upper.startswith('CREATE OR REPLACE PACKAGE'))

        if is_plsql:
            # This is a PL/SQL block, use PL/SQL engine
            try:
                from ..plsql.engine import PLSQLEngine

                # Create PL/SQL engine if not already created
                if not hasattr(self, '_plsql_engine'):
                    self._plsql_engine = PLSQLEngine(self)

                # Execute PL/SQL
                result = self._plsql_engine.execute(sql)

                # Format output for display
                if result['status'] == 'success' and result.get('output'):
                    return {
                        'status': 'success',
                        'message': '\n'.join(result['output']),
                        'output': result['output']
                    }
                return result
            except Exception as e:
                return {
                    'status': 'error',
                    'error': str(e),
                    'error_type': type(e).__name__
                }

        # Parse SQL
        query = self.parser.parse(sql)

        # Route to appropriate handler
        if isinstance(query, CreateTableQuery):
            return self._execute_create_table(query)
        elif isinstance(query, DropTableQuery):
            return self._execute_drop_table(query)
        elif isinstance(query, CreateViewQuery):
            return self._execute_create_view(query)
        elif isinstance(query, DropViewQuery):
            return self._execute_drop_view(query)
        elif isinstance(query, CreateTriggerQuery):
            return self._execute_create_trigger(query)
        elif isinstance(query, DropTriggerQuery):
            return self._execute_drop_trigger(query)
        elif isinstance(query, CreateSequenceQuery):
            return self._execute_create_sequence(query)
        elif isinstance(query, DropSequenceQuery):
            return self._execute_drop_sequence(query)
        elif isinstance(query, AlterSequenceQuery):
            return self._execute_alter_sequence(query)
        elif isinstance(query, InsertQuery):
            return self._execute_insert(query)
        elif isinstance(query, SelectQuery):
            return self._execute_select(query)
        elif isinstance(query, UpdateQuery):
            return self._execute_update(query)
        elif isinstance(query, DeleteQuery):
            return self._execute_delete(query)
        elif isinstance(query, DescribeQuery):
            return self._execute_describe(query)
        else:
            raise ValueError(f"Unsupported query type: {query.query_type}")

    def _execute_create_table(self, query: CreateTableQuery) -> Dict[str, Any]:
        """Execute CREATE TABLE"""
        if query.table_name in self.tables:
            if query.if_not_exists:
                return {
                    'status': 'success',
                    'message': f"Table '{query.table_name}' already exists (IF NOT EXISTS)"
                }
            else:
                raise ValueError(f"Table '{query.table_name}' already exists")

        # Create schema
        schema = TableSchema(query.table_name, query.columns)

        # Create table using storage backend
        self.storage.create_table(query.table_name, schema)

        # Add to system catalog
        self.catalog.add_object(
            owner=self.default_owner,
            object_name=query.table_name,
            object_type='TABLE',
            status='VALID'
        )

        # Auto-create vector collection for text columns
        collection_name = None
        if self.auto_vectorizer:
            collection_name = self.auto_vectorizer.create_vector_collection(
                query.table_name,
                query.columns
            )

        # Auto-save
        self._auto_save()

        result = {
            'status': 'success',
            'message': f"Table '{query.table_name}' created",
            'table': query.table_name,
            'columns': len(query.columns)
        }

        if collection_name:
            result['vector_collection'] = collection_name

        return result

    def _execute_drop_table(self, query: DropTableQuery) -> Dict[str, Any]:
        """Execute DROP TABLE"""
        if query.table_name not in self.tables:
            if query.if_exists:
                return {
                    'status': 'success',
                    'message': f"Table '{query.table_name}' does not exist (IF EXISTS)"
                }
            else:
                raise ValueError(f"Table '{query.table_name}' does not exist")

        del self.tables[query.table_name]

        # Remove from system catalog
        self.catalog.remove_object(query.table_name, 'TABLE')

        # Auto-save
        self._auto_save()

        return {
            'status': 'success',
            'message': f"Table '{query.table_name}' dropped",
            'table': query.table_name
        }

    def _execute_create_view(self, query: CreateViewQuery) -> Dict[str, Any]:
        """Execute CREATE VIEW"""
        if query.view_name in self.views:
            if query.or_replace:
                # Replace existing view
                self.views[query.view_name] = query.select_query
                self.catalog.update_object_ddl_time(query.view_name, 'VIEW')
                return {
                    'status': 'success',
                    'message': f"View '{query.view_name}' replaced",
                    'view': query.view_name
                }
            else:
                raise ValueError(f"View '{query.view_name}' already exists")

        # Check if view name conflicts with table name
        if query.view_name in self.tables:
            raise ValueError(f"Table '{query.view_name}' already exists with that name")

        # Store view definition
        self.views[query.view_name] = query.select_query

        # Add to system catalog
        self.catalog.add_object(
            owner=self.default_owner,
            object_name=query.view_name,
            object_type='VIEW',
            status='VALID'
        )

        return {
            'status': 'success',
            'message': f"View '{query.view_name}' created",
            'view': query.view_name
        }

    def _execute_drop_view(self, query: DropViewQuery) -> Dict[str, Any]:
        """Execute DROP VIEW"""
        if query.view_name not in self.views:
            if query.if_exists:
                return {
                    'status': 'success',
                    'message': f"View '{query.view_name}' does not exist (IF EXISTS)"
                }
            else:
                raise ValueError(f"View '{query.view_name}' does not exist")

        del self.views[query.view_name]

        # Remove from system catalog
        self.catalog.remove_object(query.view_name, 'VIEW')

        return {
            'status': 'success',
            'message': f"View '{query.view_name}' dropped",
            'view': query.view_name
        }

    def _execute_insert(self, query: InsertQuery) -> Dict[str, Any]:
        """Execute INSERT"""
        if query.table_name not in self.tables:
            raise ValueError(f"Table '{query.table_name}' does not exist")

        table = self.tables[query.table_name]

        # Convert value lists to row dictionaries
        rows_to_insert = []
        for value_list in query.values:
            # Replace sequence NEXTVAL/CURRVAL calls with actual values
            value_list = [self._replace_sequence_calls(v) for v in value_list]

            if query.columns:
                # Columns specified
                if len(value_list) != len(query.columns):
                    raise ValueError(f"Column count ({len(query.columns)}) doesn't match value count ({len(value_list)})")
                row = dict(zip(query.columns, value_list))
            else:
                # No columns specified, use schema order
                schema_columns = [col.name for col in table.schema.columns if not col.auto_increment]
                if len(value_list) != len(schema_columns):
                    raise ValueError(f"Value count ({len(value_list)}) doesn't match table column count ({len(schema_columns)})")
                row = dict(zip(schema_columns, value_list))

            rows_to_insert.append(row)

        # Fire BEFORE INSERT triggers
        for row in rows_to_insert:
            self._fire_triggers(query.table_name, 'INSERT', 'BEFORE', new_row=row)

        # Insert rows
        inserted_ids = table.insert_batch(rows_to_insert)

        # Fire AFTER INSERT triggers
        for row in rows_to_insert:
            self._fire_triggers(query.table_name, 'INSERT', 'AFTER', new_row=row)

        # Auto-embed inserted rows (use batch embedding for better performance)
        if self.auto_vectorizer:
            if len(inserted_ids) > 1:
                # Use batch embedding for multiple rows
                self.auto_vectorizer.on_insert_batch(query.table_name, inserted_ids, rows_to_insert)
            elif len(inserted_ids) == 1:
                # Use single insert for one row
                self.auto_vectorizer.on_insert(query.table_name, inserted_ids[0], rows_to_insert[0])

        # Auto-save
        self._auto_save()

        return {
            'status': 'success',
            'message': f"Inserted {len(inserted_ids)} row(s)",
            'table': query.table_name,
            'inserted': len(inserted_ids)
        }

    def _execute_select(self, query: SelectQuery) -> Dict[str, Any]:
        """Execute SELECT with derived table support"""
        # Phase 4: Handle derived table (subquery in FROM clause)
        if query.from_derived_table:
            return self._execute_select_from_derived_table(query)

        # Check if querying system tables
        if query.from_table.upper() == 'ALL_OBJECTS':
            return self._query_all_objects(query)
        elif query.from_table.upper() == 'ALL_TABLES':
            return self._query_all_tables(query)
        elif query.from_table.upper() == 'DUAL':
            return self._query_dual(query)

        # Check if querying a view
        if query.from_table in self.views:
            # Execute the view's underlying query
            view_query = self.views[query.from_table]
            return self.execute(view_query)

        if query.from_table not in self.tables:
            raise ValueError(f"Table or view '{query.from_table}' does not exist")

        table = self.tables[query.from_table]

        # Check for aggregate functions (COUNT, SUM, AVG, etc.)
        import re
        has_aggregate = any(re.match(r'(COUNT|SUM|AVG|MIN|MAX)\s*\(', col, re.IGNORECASE)
                           for col in query.columns)

        if has_aggregate:
            # Handle aggregate queries
            return self._execute_aggregate_select(query, table)

        # Handle JOINs if present
        if query.joins:
            return self._execute_select_with_joins(query)

        # Build query plan using operators
        # Start with table scan
        plan = ScanOperator(table)

        # Apply WHERE filter
        if query.where:
            # Evaluate any subqueries in WHERE clause first
            evaluated_where = self._evaluate_subqueries_in_where(query.where)
            predicate = build_predicate_from_where(evaluated_where)
            plan = FilterOperator(plan, predicate)

        # Apply GROUP BY and aggregates
        if query.group_by or any('(' in col for col in query.columns):
            # TODO: Parse aggregate functions from columns
            # For now, skip aggregation in basic implementation
            pass

        # Apply ORDER BY
        if query.order_by:
            plan = SortOperator(plan, query.order_by)

        # Apply LIMIT/OFFSET
        if query.limit or query.offset:
            plan = LimitOperator(plan, query.limit, query.offset)

        # Apply projection (SELECT columns)
        plan = ProjectOperator(plan, query.columns)

        # Execute plan and collect results
        rows = list(plan.execute())

        # Convert numpy arrays to lists for JSON serialization
        serialized_rows = []
        for row in rows:
            serialized_row = {}
            for key, value in row.items():
                # Convert numpy arrays to lists
                if hasattr(value, 'tolist'):  # numpy array
                    serialized_row[key] = value.tolist()
                else:
                    serialized_row[key] = value
            serialized_rows.append(serialized_row)

        # Determine columns
        if serialized_rows:
            columns = list(serialized_rows[0].keys())
        else:
            columns = query.columns if query.columns != ['*'] else []

        return {
            'status': 'success',
            'columns': columns,
            'rows': serialized_rows,
            'count': len(serialized_rows)
        }

    def _execute_select_from_derived_table(self, query: SelectQuery) -> Dict[str, Any]:
        """Execute SELECT from derived table (subquery in FROM clause)

        This handles queries like:
        SELECT COUNT(*) FROM (SELECT * FROM employees WHERE salary > 70000)
        """
        # Execute the inner subquery first
        derived_result = self._execute_select(query.from_derived_table)

        if derived_result['status'] != 'success':
            return derived_result

        # Create a temporary in-memory table from the result
        temp_table = self._create_temp_table_from_result(
            query.derived_table_alias,
            derived_result
        )

        # Create a new query that references the temp table instead of the derived table
        from .parser import SelectQuery as SelectQueryClass
        outer_query = SelectQueryClass(
            columns=query.columns,
            from_table=query.derived_table_alias,
            where=query.where,
            joins=query.joins,
            group_by=query.group_by,
            having=query.having,
            order_by=query.order_by,
            limit=query.limit,
            offset=query.offset,
            from_derived_table=None,  # No longer a derived table
            derived_table_alias=None
        )

        try:
            # Execute the outer query against the temp table
            result = self._execute_select(outer_query)
            return result
        finally:
            # Clean up the temp table
            self._drop_temp_table(query.derived_table_alias)

    def _sanitize_column_name(self, col_expr: str) -> str:
        """
        Extract a valid column name from a column expression.
        Handles aliases (e.g., 'MAX(salary) as max_sal' -> 'max_sal')
        and makes invalid names SQLite-safe.
        """
        # Check for alias (AS keyword)
        if ' as ' in col_expr.lower():
            # Extract alias part
            parts = col_expr.lower().split(' as ')
            if len(parts) == 2:
                alias = parts[1].strip()
                # Return the alias
                return alias

        # No alias - sanitize the expression
        # Remove parentheses, replace special chars with underscore
        sanitized = col_expr.replace('(', '_').replace(')', '_').replace('*', 'all')
        sanitized = sanitized.replace(' ', '_').replace('-', '_')

        # Remove multiple consecutive underscores
        while '__' in sanitized:
            sanitized = sanitized.replace('__', '_')

        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')

        return sanitized if sanitized else 'col_0'

    def _create_temp_table_from_result(self, table_name: str, result: Dict[str, Any]):
        """Create a temporary in-memory table from query result"""
        from .schema import TableSchema, Column, DataType

        if not result['rows']:
            # Empty result - create table with minimal structure
            # Sanitize column names for temp table creation
            columns = [Column(name=self._sanitize_column_name(col), data_type=DataType.TEXT)
                      for col in result['columns']]
        else:
            # Infer column types from first row
            first_row = result['rows'][0]
            columns = []

            for col_name in result['columns']:
                value = first_row.get(col_name)

                # Sanitize the column name for temp table
                sanitized_name = self._sanitize_column_name(col_name)

                # Infer data type from value
                if value is None:
                    data_type = DataType.TEXT
                elif isinstance(value, bool):
                    data_type = DataType.BOOLEAN
                elif isinstance(value, int):
                    data_type = DataType.INTEGER
                elif isinstance(value, float):
                    data_type = DataType.REAL
                else:
                    data_type = DataType.TEXT

                columns.append(Column(name=sanitized_name, data_type=data_type))

        # Create table schema
        schema = TableSchema(table_name, columns)

        # Create table using storage backend
        self.storage.create_table(table_name, schema)

        # Build mapping from original column names to sanitized names
        col_name_mapping = {orig: self._sanitize_column_name(orig) for orig in result['columns']}

        # Insert all rows with proper type casting
        table = self.tables[table_name]
        for row in result['rows']:
            # Cast row values to proper types according to schema
            # Use sanitized column names for the temp table
            casted_row = {}
            for orig_name, sanitized_name in col_name_mapping.items():
                if orig_name in row:
                    # Find the column definition by sanitized name
                    col = next((c for c in columns if c.name == sanitized_name), None)
                    if col:
                        casted_row[sanitized_name] = col.cast_value(row[orig_name])
                else:
                    casted_row[sanitized_name] = None

            table.insert(casted_row)

        return table

    def _drop_temp_table(self, table_name: str):
        """Drop a temporary table"""
        if table_name in self.tables:
            del self.tables[table_name]

    def _execute_select_with_joins(self, query: SelectQuery) -> Dict[str, Any]:
        """Execute SELECT with JOIN operations"""
        # Get the main table
        left_table = self.tables[query.from_table]

        # Start with main table scan
        left_rows = [row for row in left_table.rows if row is not None]

        # Process each join
        for join_info in query.joins:
            right_table_name = join_info['table']
            if right_table_name not in self.tables:
                raise ValueError(f"Table '{right_table_name}' does not exist")

            right_table = self.tables[right_table_name]
            right_rows = [row for row in right_table.rows if row is not None]

            # Parse join condition (e.g., "e.topic_id = t.id")
            left_col = join_info['on_left']
            right_col = join_info['on_right']

            # Extract actual column names (remove alias prefix)
            left_col_name = left_col.split('.')[-1] if '.' in left_col else left_col
            right_col_name = right_col.split('.')[-1] if '.' in right_col else right_col

            # Perform join
            joined_rows = []
            for left_row in left_rows:
                matched = False
                for right_row in right_rows:
                    # Check join condition
                    if left_row.get(left_col_name) == right_row.get(right_col_name):
                        # Merge rows with prefixed column names
                        merged = {}
                        for k, v in left_row.items():
                            merged[k] = v
                        for k, v in right_row.items():
                            # Avoid overwriting columns with same name
                            if k in merged:
                                merged[f"{right_table_name}.{k}"] = v
                            else:
                                merged[k] = v
                        joined_rows.append(merged)
                        matched = True

                # For LEFT JOIN, include unmatched rows from left table
                if not matched and join_info['type'] == 'LEFT':
                    # Add left row with NULL values for right table columns
                    merged = dict(left_row)
                    for col in right_table.schema.columns:
                        if col.name not in merged:
                            merged[col.name] = None
                    joined_rows.append(merged)

            # Update left_rows for next iteration
            left_rows = joined_rows

        # Apply WHERE filter
        if query.where:
            # Evaluate any subqueries in WHERE clause first
            evaluated_where = self._evaluate_subqueries_in_where(query.where)
            predicate = build_predicate_from_where(evaluated_where)
            left_rows = [row for row in left_rows if predicate(row)]

        # Apply ORDER BY
        if query.order_by:
            for order_col, order_dir in reversed(query.order_by):
                # Handle aliased columns (e.g., "e.created_at")
                col_name = order_col.split('.')[-1] if '.' in order_col else order_col
                reverse = (order_dir.upper() == 'DESC')
                left_rows.sort(key=lambda x: x.get(col_name, ''), reverse=reverse)

        # Apply projection
        if query.columns != ['*']:
            projected_rows = []
            for row in left_rows:
                projected = {}
                for col_expr in query.columns:
                    # Handle aliased columns (e.g., "e.id", "t.topic_name")
                    if '.' in col_expr:
                        # Extract the actual column name
                        col_name = col_expr.split('.')[-1]
                        if col_name in row:
                            projected[col_expr] = row[col_name]
                        else:
                            projected[col_expr] = None
                    else:
                        projected[col_expr] = row.get(col_expr)
                projected_rows.append(projected)
            left_rows = projected_rows

        # Apply LIMIT/OFFSET
        if query.offset:
            left_rows = left_rows[query.offset:]
        if query.limit:
            left_rows = left_rows[:query.limit]

        # Determine columns
        if left_rows:
            columns = list(left_rows[0].keys())
        else:
            columns = query.columns if query.columns != ['*'] else []

        return {
            'status': 'success',
            'columns': columns,
            'rows': left_rows,
            'count': len(left_rows)
        }

    def _evaluate_subqueries_in_where(self, where_clause: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate any subqueries in WHERE clause values

        Replaces subquery strings like '(SELECT AVG(salary) FROM employees)'
        with their actual evaluated numeric results
        """
        import re

        evaluated_where = {}

        for column, condition in where_clause.items():
            if isinstance(condition, dict):
                # Check operator values for subqueries
                evaluated_condition = {}
                for op, op_value in condition.items():
                    # Check if this is a subquery (starts with '(' and contains 'SELECT')
                    if isinstance(op_value, str) and op_value.strip().startswith('(') and 'SELECT' in op_value.upper():
                        # This is a subquery - evaluate it
                        try:
                            from .expression_parser import ExpressionParser
                            from .expression_evaluator import ExpressionEvaluator, EvaluationContext

                            parser = ExpressionParser()
                            evaluator = ExpressionEvaluator()

                            ast = parser.parse(op_value)
                            context = EvaluationContext(row={}, engine=self)
                            result = evaluator.evaluate(ast, context)

                            evaluated_condition[op] = result
                        except Exception as e:
                            # If subquery evaluation fails, keep original
                            evaluated_condition[op] = op_value
                    else:
                        evaluated_condition[op] = op_value
                evaluated_where[column] = evaluated_condition
            else:
                evaluated_where[column] = condition

        return evaluated_where

    def _execute_aggregate_select(self, query: SelectQuery, table: TableStore) -> Dict[str, Any]:
        """Execute SELECT with aggregate functions like COUNT, SUM, AVG"""
        import re
        from collections import defaultdict

        # Get base rows (apply WHERE if specified)
        if query.where:
            # Evaluate any subqueries in WHERE clause first
            evaluated_where = self._evaluate_subqueries_in_where(query.where)
            predicate = build_predicate_from_where(evaluated_where)
            base_rows = [row for row in table.rows if row is not None and predicate(row)]
        else:
            base_rows = [row for row in table.rows if row is not None]

        # If GROUP BY is specified, group rows by those columns
        if query.group_by:
            # Group rows by the GROUP BY columns
            groups = defaultdict(list)
            for row in base_rows:
                # Create group key from GROUP BY columns
                group_key = tuple(row.get(col) for col in query.group_by)
                groups[group_key].append(row)

            # Process each group
            result_rows = []
            for group_key, group_rows in groups.items():
                result_row = {}

                # First, add the GROUP BY columns to the result
                for i, col_name in enumerate(query.group_by):
                    result_row[col_name] = group_key[i]

                # Then process aggregate columns
                for col_expr in query.columns:
                    # Skip if this is a GROUP BY column (already added)
                    if col_expr in query.group_by:
                        continue

                    # Extract alias if present (e.g., "MAX(salary) as max_sal" -> "max_sal")
                    output_name = self._extract_column_alias(col_expr)

                    # Process aggregate functions
                    result_row[output_name] = self._compute_aggregate(col_expr, group_rows)

                result_rows.append(result_row)

            return {
                'status': 'success',
                'columns': list(result_rows[0].keys()) if result_rows else [],
                'rows': result_rows,
                'count': len(result_rows)
            }
        else:
            # No GROUP BY - aggregate all rows together
            result_row = {}
            for col_expr in query.columns:
                # Extract alias if present
                output_name = self._extract_column_alias(col_expr)
                result_row[output_name] = self._compute_aggregate(col_expr, base_rows)

            return {
                'status': 'success',
                'columns': list(result_row.keys()),
                'rows': [result_row],
                'count': 1
            }

    def _extract_column_alias(self, col_expr: str) -> str:
        """
        Extract the output column name from a column expression.
        If there's an AS alias, use that. Otherwise, use the expression as-is.

        Examples:
            'MAX(salary) as max_sal' -> 'max_sal'
            'salary' -> 'salary'
            'MAX(salary)' -> 'MAX(salary)'
        """
        import re
        # Check for AS keyword (case insensitive)
        as_match = re.search(r'\s+as\s+(\w+)\s*$', col_expr, re.IGNORECASE)
        if as_match:
            return as_match.group(1)
        return col_expr

    def _compute_aggregate(self, col_expr: str, rows: list) -> Any:
        """Compute aggregate function value for a set of rows"""
        import re

        # Match aggregate function patterns
        count_match = re.match(r'COUNT\s*\(\s*\*?\s*\)', col_expr, re.IGNORECASE)
        if count_match:
            return len(rows)

        sum_match = re.match(r'SUM\s*\(\s*(\w+)\s*\)', col_expr, re.IGNORECASE)
        if sum_match:
            col_name = sum_match.group(1)
            values = []
            for row in rows:
                val = row.get(col_name)
                if val is not None:
                    try:
                        values.append(float(val))
                    except (ValueError, TypeError):
                        pass
            return sum(values) if values else 0

        avg_match = re.match(r'AVG\s*\(\s*(\w+)\s*\)', col_expr, re.IGNORECASE)
        if avg_match:
            col_name = avg_match.group(1)
            values = []
            for row in rows:
                val = row.get(col_name)
                if val is not None:
                    try:
                        values.append(float(val))
                    except (ValueError, TypeError):
                        pass
            return sum(values) / len(values) if values else 0

        min_match = re.match(r'MIN\s*\(\s*(\w+)\s*\)', col_expr, re.IGNORECASE)
        if min_match:
            col_name = min_match.group(1)
            values = []
            for row in rows:
                val = row.get(col_name)
                if val is not None:
                    try:
                        values.append(float(val))
                    except (ValueError, TypeError):
                        values.append(val)
            return min(values) if values else None

        max_match = re.match(r'MAX\s*\(\s*(\w+)\s*\)', col_expr, re.IGNORECASE)
        if max_match:
            col_name = max_match.group(1)
            values = []
            for row in rows:
                val = row.get(col_name)
                if val is not None:
                    try:
                        values.append(float(val))
                    except (ValueError, TypeError):
                        values.append(val)
            return max(values) if values else None

        # If not an aggregate, return None
        return None

    def _execute_update(self, query: UpdateQuery) -> Dict[str, Any]:
        """Execute UPDATE"""
        if query.table_name not in self.tables:
            raise ValueError(f"Table '{query.table_name}' does not exist")

        table = self.tables[query.table_name]

        # Find rows to update using scan() to get correct rowids
        if query.where:
            predicate = build_predicate_from_where(query.where)
            rows_to_update = table.scan(where=predicate)
        else:
            # Update all rows
            rows_to_update = table.scan()

        # Update each row
        updated_count = 0
        for row_id, old_row in rows_to_update:
            # Evaluate update expressions for this row
            evaluated_updates = {}
            for col_name, expr_value in query.updates.items():
                # Check if the value is an expression that references columns
                if isinstance(expr_value, str) and any(col in expr_value for col in old_row.keys()):
                    # This looks like an expression - evaluate it with row context
                    try:
                        # Replace column names with their values
                        eval_expr = expr_value
                        for row_col, row_val in old_row.items():
                            # Replace whole word matches only
                            import re
                            pattern = r'\b' + re.escape(row_col) + r'\b'
                            eval_expr = re.sub(pattern, str(row_val), eval_expr)
                        # Evaluate the expression
                        evaluated_updates[col_name] = eval(eval_expr)
                    except:
                        # If evaluation fails, use as literal value
                        evaluated_updates[col_name] = expr_value
                else:
                    # Not an expression, use as literal value
                    evaluated_updates[col_name] = expr_value

            # Create new row with updates applied
            new_row = dict(old_row)
            new_row.update(evaluated_updates)

            # Fire BEFORE UPDATE triggers
            self._fire_triggers(query.table_name, 'UPDATE', 'BEFORE', old_row=old_row, new_row=new_row)

            if table.update(row_id, evaluated_updates):
                # Fire AFTER UPDATE triggers
                self._fire_triggers(query.table_name, 'UPDATE', 'AFTER', old_row=old_row, new_row=new_row)

                # Auto re-embed if text columns changed
                if self.auto_vectorizer:
                    self.auto_vectorizer.on_update(
                        query.table_name,
                        row_id,
                        old_row,
                        query.updates
                    )
                updated_count += 1

        # Auto-save
        self._auto_save()

        return {
            'status': 'success',
            'message': f"Updated {updated_count} row(s)",
            'table': query.table_name,
            'updated': updated_count
        }

    def _execute_delete(self, query: DeleteQuery) -> Dict[str, Any]:
        """Execute DELETE"""
        if query.table_name not in self.tables:
            raise ValueError(f"Table '{query.table_name}' does not exist")

        table = self.tables[query.table_name]

        # Find rows to delete using scan() to get correct rowids
        if query.where:
            predicate = build_predicate_from_where(query.where)
            rows_to_delete = table.scan(where=predicate)
        else:
            # Delete all rows
            rows_to_delete = table.scan()

        # Delete each row
        deleted_count = 0
        for row_id, old_row in rows_to_delete:
            # Fire BEFORE DELETE triggers
            self._fire_triggers(query.table_name, 'DELETE', 'BEFORE', old_row=old_row)

            if table.delete(row_id):
                # Fire AFTER DELETE triggers
                self._fire_triggers(query.table_name, 'DELETE', 'AFTER', old_row=old_row)

                # Auto-remove corresponding vector
                if self.auto_vectorizer:
                    self.auto_vectorizer.on_delete(query.table_name, row_id)
                deleted_count += 1

        # Auto-save
        self._auto_save()

        return {
            'status': 'success',
            'message': f"Deleted {deleted_count} row(s)",
            'table': query.table_name,
            'deleted': deleted_count
        }

    def get_table(self, table_name: str) -> Optional[TableStore]:
        """Get a table by name"""
        return self.tables.get(table_name)

    def list_tables(self) -> List[str]:
        """Get list of all table names"""
        return list(self.tables.keys())

    def get_table_schema(self, table_name: str) -> Optional[TableSchema]:
        """Get schema for a table"""
        table = self.tables.get(table_name)
        return table.schema if table else None

    def table_stats(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a table"""
        table = self.tables.get(table_name)
        if not table:
            return None

        return {
            'name': table_name,
            'rows': table.size(),
            'columns': len(table.schema.columns),
            'schema': table.schema.to_dict()
        }

    def _query_all_objects(self, query: SelectQuery) -> Dict[str, Any]:
        """
        Query the ALL_OBJECTS system table.

        Args:
            query: SELECT query

        Returns:
            Result dictionary with object metadata
        """
        # For SQLite backend, query the actual all_objects table
        if self.backend_type == 'sqlite':
            import sqlite3
            conn = sqlite3.connect(self.db_file if self.db_file else 'EzDB_database.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Build SQL query
            columns_sql = ', '.join(query.columns) if query.columns != ['*'] else '*'
            sql = f"SELECT {columns_sql} FROM all_objects"

            # Add WHERE clause if specified
            if query.where:
                # Convert WHERE clause to SQL string
                where_sql = self._where_to_sql(query.where)
                sql += f" WHERE {where_sql}"

            # Add ORDER BY if specified
            if query.order_by:
                order_parts = [f"{col} {direction}" for col, direction in query.order_by]
                sql += f" ORDER BY {', '.join(order_parts)}"

            # Add LIMIT/OFFSET
            if query.limit:
                sql += f" LIMIT {query.limit}"
            if query.offset:
                sql += f" OFFSET {query.offset}"

            # Execute query
            cursor.execute(sql)
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()

            # Determine columns
            if rows:
                columns = list(rows[0].keys())
            else:
                columns = query.columns if query.columns != ['*'] else []

            return {
                'status': 'success',
                'columns': columns,
                'rows': rows,
                'count': len(rows)
            }

        # For JSON backend, use in-memory catalog
        # Get all objects from catalog
        objects = self.catalog.get_all_objects_data()

        # Convert to rows format
        rows = objects

        # Apply WHERE filter if specified
        if query.where:
            predicate = build_predicate_from_where(query.where)
            rows = [row for row in rows if predicate(row)]

        # Apply ORDER BY
        if query.order_by:
            for order_col, order_dir in reversed(query.order_by):
                reverse = (order_dir.upper() == 'DESC')
                rows.sort(key=lambda x: x.get(order_col, ''), reverse=reverse)

        # Apply LIMIT/OFFSET
        if query.offset:
            rows = rows[query.offset:]
        if query.limit:
            rows = rows[:query.limit]

        # Apply projection
        if query.columns != ['*']:
            projected_rows = []
            for row in rows:
                projected_row = {col: row.get(col) for col in query.columns if col in row}
                projected_rows.append(projected_row)
            rows = projected_rows

        # Determine columns
        if rows:
            columns = list(rows[0].keys())
        else:
            columns = query.columns if query.columns != ['*'] else []

        return {
            'status': 'success',
            'columns': columns,
            'rows': rows,
            'count': len(rows)
        }

    def _execute_describe(self, query: DescribeQuery) -> Dict[str, Any]:
        """
        Execute DESCRIBE command (Oracle-style table description).

        Args:
            query: DESCRIBE query

        Returns:
            Result dictionary with table schema information
        """
        # Check if table exists
        if query.table_name not in self.tables:
            # Check if it's a system table
            if query.table_name.upper() in ['ALL_OBJECTS', 'ALL_TABLES']:
                # For system tables, return their schema
                if query.table_name.upper() == 'ALL_OBJECTS':
                    rows = [
                        {'Name': 'OWNER', 'Null?': '', 'Type': 'VARCHAR2(128)'},
                        {'Name': 'OBJECT_NAME', 'Null?': '', 'Type': 'VARCHAR2(128)'},
                        {'Name': 'SUBOBJECT_NAME', 'Null?': '', 'Type': 'VARCHAR2(128)'},
                        {'Name': 'OBJECT_ID', 'Null?': '', 'Type': 'NUMBER'},
                        {'Name': 'DATA_OBJECT_ID', 'Null?': '', 'Type': 'NUMBER'},
                        {'Name': 'OBJECT_TYPE', 'Null?': '', 'Type': 'VARCHAR2(23)'},
                        {'Name': 'CREATED', 'Null?': '', 'Type': 'DATE'},
                        {'Name': 'LAST_DDL_TIME', 'Null?': '', 'Type': 'DATE'},
                        {'Name': 'TIMESTAMP', 'Null?': '', 'Type': 'VARCHAR2(19)'},
                        {'Name': 'STATUS', 'Null?': '', 'Type': 'VARCHAR2(7)'},
                        {'Name': 'TEMPORARY', 'Null?': '', 'Type': 'VARCHAR2(1)'},
                        {'Name': 'GENERATED', 'Null?': '', 'Type': 'VARCHAR2(1)'},
                        {'Name': 'SECONDARY', 'Null?': '', 'Type': 'VARCHAR2(1)'},
                        {'Name': 'NAMESPACE', 'Null?': '', 'Type': 'NUMBER'},
                        {'Name': 'EDITION_NAME', 'Null?': '', 'Type': 'VARCHAR2(128)'},
                        {'Name': 'SHARING', 'Null?': '', 'Type': 'VARCHAR2(18)'},
                        {'Name': 'EDITIONABLE', 'Null?': '', 'Type': 'VARCHAR2(1)'},
                        {'Name': 'ORACLE_MAINTAINED', 'Null?': '', 'Type': 'VARCHAR2(1)'},
                        {'Name': 'APPLICATION', 'Null?': '', 'Type': 'VARCHAR2(1)'},
                        {'Name': 'DEFAULT_COLLATION', 'Null?': '', 'Type': 'VARCHAR2(100)'},
                        {'Name': 'DUPLICATED', 'Null?': '', 'Type': 'VARCHAR2(1)'},
                        {'Name': 'SHARDED', 'Null?': '', 'Type': 'VARCHAR2(1)'},
                        {'Name': 'IMPORTED_OBJECT', 'Null?': '', 'Type': 'VARCHAR2(1)'},
                        {'Name': 'SYNCHRONOUS_DUPLICATED', 'Null?': '', 'Type': 'VARCHAR2(1)'},
                        {'Name': 'CREATED_APPID', 'Null?': '', 'Type': 'NUMBER'},
                        {'Name': 'CREATED_VSNID', 'Null?': '', 'Type': 'NUMBER'},
                        {'Name': 'MODIFIED_APPID', 'Null?': '', 'Type': 'NUMBER'},
                        {'Name': 'MODIFIED_VSNID', 'Null?': '', 'Type': 'NUMBER'}
                    ]
                else:  # ALL_TABLES
                    rows = [
                        {'Name': 'OWNER', 'Null?': '', 'Type': 'VARCHAR2(128)'},
                        {'Name': 'TABLE_NAME', 'Null?': '', 'Type': 'VARCHAR2(128)'},
                        {'Name': 'TABLESPACE_NAME', 'Null?': '', 'Type': 'VARCHAR2(30)'},
                        {'Name': 'NUM_ROWS', 'Null?': '', 'Type': 'NUMBER'},
                        {'Name': 'BLOCKS', 'Null?': '', 'Type': 'NUMBER'},
                        {'Name': 'STATUS', 'Null?': '', 'Type': 'VARCHAR2(8)'}
                    ]

                return {
                    'status': 'success',
                    'columns': ['Name', 'Null?', 'Type'],
                    'rows': rows,
                    'count': len(rows),
                    'is_describe': True
                }
            else:
                raise ValueError(f"Table '{query.table_name}' does not exist")

        # Get table schema
        table = self.tables[query.table_name]
        schema = table.schema

        # Format like Oracle DESCRIBE output
        rows = []
        for column in schema.columns:
            # Determine nullable status
            null_status = '' if not column.nullable else 'NULL'
            if not column.nullable:
                null_status = 'NOT NULL'

            # Determine type string
            type_str = column.data_type.name
            if column.data_type.name == 'VECTOR' and column.vector_dimension:
                type_str = f'VECTOR({column.vector_dimension})'
            elif column.data_type.name == 'INTEGER':
                type_str = 'NUMBER'
            elif column.data_type.name == 'REAL':
                type_str = 'NUMBER'
            elif column.data_type.name == 'TEXT':
                type_str = 'VARCHAR2(4000)'
            elif column.data_type.name == 'BLOB':
                type_str = 'BLOB'

            rows.append({
                'Name': column.name,
                'Null?': null_status,
                'Type': type_str
            })

        return {
            'status': 'success',
            'columns': ['Name', 'Null?', 'Type'],
            'rows': rows,
            'count': len(rows),
            'is_describe': True
        }

    def _query_all_tables(self, query: SelectQuery) -> Dict[str, Any]:
        """
        Query the ALL_TABLES system table.

        Args:
            query: SELECT query

        Returns:
            Result dictionary with table metadata
        """
        # Get all tables from catalog with extended metadata
        tables = self.catalog.get_all_tables_data()

        # Add row count information from actual tables
        for table_info in tables:
            table_name = table_info['OBJECT_NAME']
            if table_name in self.tables:
                table_store = self.tables[table_name]
                table_info['NUM_ROWS'] = table_store.size()

        rows = tables

        # Apply WHERE filter if specified
        if query.where:
            predicate = build_predicate_from_where(query.where)
            rows = [row for row in rows if predicate(row)]

        # Apply ORDER BY
        if query.order_by:
            for order_col, order_dir in reversed(query.order_by):
                reverse = (order_dir.upper() == 'DESC')
                rows.sort(key=lambda x: x.get(order_col, ''), reverse=reverse)

        # Apply LIMIT/OFFSET
        if query.offset:
            rows = rows[query.offset:]
        if query.limit:
            rows = rows[:query.limit]

        # Apply projection
        if query.columns != ['*']:
            projected_rows = []
            for row in rows:
                projected_row = {col: row.get(col) for col in query.columns if col in row}
                projected_rows.append(projected_row)
            rows = projected_rows

        # Determine columns
        if rows:
            columns = list(rows[0].keys())
        else:
            columns = query.columns if query.columns != ['*'] else []

        return {
            'status': 'success',
            'columns': columns,
            'rows': rows,
            'count': len(rows)
        }

    def _query_dual(self, query: SelectQuery) -> Dict[str, Any]:
        """
        Query the DUAL table (Oracle-style single-row dummy table).
        Used to execute functions and expressions without referencing a real table.

        Args:
            query: SELECT query

        Returns:
            Result dictionary with evaluated expressions/functions
        """
        import re

        # Import Oracle functions library
        try:
            import oracle_functions_library as oracle_funcs
        except ImportError:
            oracle_funcs = None

        # Import advanced functions library
        try:
            import advanced_functions_library as adv_funcs
        except ImportError:
            adv_funcs = None

        # Evaluate each column expression
        result_row = {}

        for col_expr in query.columns:
            # Remove any whitespace
            col_expr_clean = col_expr.strip()

            # Check if it's just the DUMMY column
            if col_expr_clean.upper() == 'DUMMY' or col_expr_clean == '*':
                result_row['DUMMY'] = 'X'
                continue

            # Try to match function calls (e.g., UPPER('hello'), ROUND(3.14, 2))
            func_match = re.match(r'(\w+)\s*\((.*)\)', col_expr_clean, re.IGNORECASE)

            if func_match:
                func_name = func_match.group(1).upper()
                func_args_str = func_match.group(2)

                # Try to execute function from Oracle library first, then advanced library
                func = None
                if oracle_funcs and hasattr(oracle_funcs, func_name):
                    func = getattr(oracle_funcs, func_name)
                elif adv_funcs and hasattr(adv_funcs, func_name):
                    func = getattr(adv_funcs, func_name)

                if func:
                    try:
                        # Parse arguments
                        args = []
                        if func_args_str.strip():
                            # Simple argument parsing (handles strings, numbers, etc.)
                            arg_list = self._parse_function_args(func_args_str)
                            args = arg_list

                        # Execute function
                        result = func(*args)
                        result_row[col_expr] = result
                        continue
                    except Exception as e:
                        # If function execution fails, return error
                        result_row[col_expr] = f"ERROR: {str(e)}"
                        continue

            # Try to evaluate as literal expression
            try:
                # Handle simple literals (numbers, strings)
                if col_expr_clean.startswith("'") and col_expr_clean.endswith("'"):
                    # String literal
                    result_row[col_expr] = col_expr_clean[1:-1]
                elif col_expr_clean.replace('.', '').replace('-', '').isdigit():
                    # Numeric literal
                    if '.' in col_expr_clean:
                        result_row[col_expr] = float(col_expr_clean)
                    else:
                        result_row[col_expr] = int(col_expr_clean)
                else:
                    # Try to evaluate as Python expression
                    result_row[col_expr] = eval(col_expr_clean)
            except:
                # If all else fails, return as string
                result_row[col_expr] = col_expr_clean

        return {
            'status': 'success',
            'columns': list(result_row.keys()),
            'rows': [result_row],
            'count': 1
        }

    def _parse_function_args(self, args_str: str) -> list:
        """
        Parse function arguments from string.
        Handles strings, numbers, and nested function calls.

        Args:
            args_str: Comma-separated argument string

        Returns:
            List of parsed arguments
        """
        args = []
        current_arg = ''
        in_string = False
        paren_depth = 0

        for char in args_str:
            if char == "'" and not in_string:
                in_string = True
                current_arg += char
            elif char == "'" and in_string:
                in_string = False
                current_arg += char
            elif char == '(' and not in_string:
                paren_depth += 1
                current_arg += char
            elif char == ')' and not in_string:
                paren_depth -= 1
                current_arg += char
            elif char == ',' and not in_string and paren_depth == 0:
                # End of argument
                args.append(self._parse_single_arg(current_arg.strip()))
                current_arg = ''
            else:
                current_arg += char

        # Add last argument
        if current_arg.strip():
            args.append(self._parse_single_arg(current_arg.strip()))

        return args

    def _parse_single_arg(self, arg_str: str):
        """
        Parse a single function argument.

        Args:
            arg_str: Single argument string

        Returns:
            Parsed argument value
        """
        arg_str = arg_str.strip()

        # String literal (could be JSON array/object)
        if arg_str.startswith("'") and arg_str.endswith("'"):
            content = arg_str[1:-1]

            # Try to parse as JSON (for arrays/objects)
            if content.startswith('[') or content.startswith('{'):
                try:
                    import json
                    return json.loads(content)
                except:
                    # Not valid JSON, return as string
                    return content

            return content

        # None/NULL
        if arg_str.upper() in ('NULL', 'NONE'):
            return None

        # Number
        if arg_str.replace('.', '').replace('-', '').isdigit():
            if '.' in arg_str:
                return float(arg_str)
            else:
                return int(arg_str)

        # Try to evaluate as expression (for nested functions)
        try:
            # Check if it's a function call
            if '(' in arg_str:
                import re
                func_match = re.match(r'(\w+)\s*\((.*)\)', arg_str, re.IGNORECASE)
                if func_match:
                    func_name = func_match.group(1).upper()
                    func_args_str = func_match.group(2)

                    # Import Oracle and advanced functions
                    import oracle_functions_library as oracle_funcs
                    import advanced_functions_library as adv_funcs

                    func = None
                    if hasattr(oracle_funcs, func_name):
                        func = getattr(oracle_funcs, func_name)
                    elif hasattr(adv_funcs, func_name):
                        func = getattr(adv_funcs, func_name)

                    if func:
                        args = self._parse_function_args(func_args_str)
                        return func(*args)

            return eval(arg_str)
        except:
            # Return as string if all else fails
            return arg_str

    def _where_to_sql(self, where_clause) -> str:
        """
        Convert WHERE clause object to SQL string.

        Args:
            where_clause: WHERE clause from parser

        Returns:
            SQL WHERE clause string
        """
        if isinstance(where_clause, dict):
            # The parser provides WHERE as a dict
            # Can be simple: {'column_name': 'value'}
            # Or with operators: {'column_name': {'$regex': '.*pattern.*'}}
            conditions = []

            for column, value in where_clause.items():
                # Check if value is a nested operator (like $regex for LIKE)
                if isinstance(value, dict):
                    # Handle operators
                    if '$regex' in value:
                        # Convert regex pattern to SQL LIKE pattern
                        regex_pattern = value['$regex']
                        # Convert .* to % for SQL LIKE
                        like_pattern = regex_pattern.replace('.*', '%')
                        conditions.append(f"{column} LIKE '{like_pattern}'")
                    else:
                        # Unknown operator - just convert to string
                        conditions.append(f"{column} = '{str(value)}'")
                elif isinstance(value, str):
                    # Simple string value
                    conditions.append(f"{column} = '{value}'")
                elif value is None:
                    # NULL value
                    conditions.append(f"{column} IS NULL")
                else:
                    # Numeric or other value
                    conditions.append(f"{column} = {value}")

            # Join multiple conditions with AND
            return ' AND '.join(conditions)

        # If it's already a string, return as-is
        return str(where_clause)

    def save_to_file(self, filepath: str):
        """
        Save database to JSON file, including vector collections.

        Args:
            filepath: Path to save database to
        """
        db_data = {
            'tables': {},
            'views': self.views,
            'sequences': self.sequences.to_dict(),
            'vector_collections': {}
        }

        # Serialize each table
        for table_name, table_store in self.tables.items():
            schema_dict = table_store.schema.to_dict()
            rows = [row for row in table_store.rows if row is not None]

            db_data['tables'][table_name] = {
                'schema': schema_dict,
                'rows': rows,
                'next_auto_increment': table_store._next_auto_increment
            }

        # Serialize vector collections if auto-vectorization is enabled
        if self.auto_vectorizer:
            db_data['vector_collections'] = {
                'enabled': True,
                'model': self.auto_vectorizer.embedding_model_name,
                'dimension': self.auto_vectorizer.dimension,
                'vectorized_tables': self.auto_vectorizer.vectorized_tables,
                'table_text_columns': self.auto_vectorizer.table_text_columns,
                'collections': {}
            }

            # Serialize each vector collection
            for collection_name, vector_db in self.auto_vectorizer.vector_collections.items():
                # Get all vectors, IDs, metadata, and documents from the collection
                all_ids = vector_db.store.get_all_ids()
                all_vectors = vector_db.store.get_all_vectors()
                all_metadata = vector_db.store.get_all_metadata()
                all_documents = vector_db.store.get_all_documents()

                # Get metric as string (handle both Enum and string)
                try:
                    metric_str = vector_db.metric.value  # For Enum
                except AttributeError:
                    metric_str = str(vector_db.metric)  # For string

                # Store collection data
                db_data['vector_collections']['collections'][collection_name] = {
                    'dimension': vector_db.dimension,
                    'metric': metric_str,
                    'vectors': [vec.tolist() for vec in all_vectors],
                    'ids': all_ids,
                    'metadata': all_metadata,
                    'documents': all_documents
                }

        # Write to file
        with open(filepath, 'w') as f:
            json.dump(db_data, f, indent=2, default=str)

    def load_from_file(self, filepath: str):
        """
        Load database from file (JSON or SQLite).

        Args:
            filepath: Path to load database from
        """
        # For SQLite backend, tables are automatically loaded from the database file
        if self.backend_type == 'sqlite':
            # SQLite backend loads tables on connection
            # Load metadata (views, sequences) from JSON file
            metadata_file = filepath.replace('.db', '_metadata.json')
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    self.views = metadata.get('views', {})
                    if 'sequences' in metadata:
                        self.sequences.from_dict(metadata['sequences'])

            # Load vector collections from SQLite
            if self.auto_vectorizer:
                from ..database import EzDB
                import numpy as np

                # Get list of vector collections from SQLite
                collections = self.storage.store.list_vector_collections()

                for collection_name in collections:
                    try:
                        # Load vectors from SQLite
                        vector_data = self.storage.store.load_vectors(collection_name)

                        if vector_data:
                            # Recreate the vector database
                            vector_db = EzDB(
                                dimension=vector_data['dimension'],
                                metric=vector_data['metric'],
                                index_type='hnsw'
                            )

                            # Restore vectors
                            if vector_data['vectors']:
                                vector_db.insert_batch(
                                    vectors=vector_data['vectors'],
                                    ids=vector_data['ids'],
                                    metadata_list=vector_data['metadata_list'],
                                    documents=vector_data['documents']
                                )

                                print(f"  ↳ Restored vector collection '{collection_name}' with {len(vector_data['vectors'])} vectors from SQLite")

                            # Store the restored collection
                            self.auto_vectorizer.vector_collections[collection_name] = vector_db

                            # Restore metadata about which tables are vectorized
                            table_name = collection_name.replace('_vectors', '')
                            if table_name not in self.auto_vectorizer.vectorized_tables:
                                self.auto_vectorizer.vectorized_tables[table_name] = collection_name

                    except Exception as e:
                        print(f"WARNING: Failed to restore vector collection '{collection_name}': {e}")
                        import traceback
                        traceback.print_exc()

            return

        # For JSON backend, load everything from JSON
        with open(filepath, 'r') as f:
            db_data = json.load(f)

        # Load views
        self.views = db_data.get('views', {})

        # Load sequences
        if 'sequences' in db_data:
            self.sequences.from_dict(db_data['sequences'])
            # Add to system catalog
            for seq_name in self.sequences.list_sequences():
                self.catalog.add_object(
                    owner=self.default_owner,
                    object_name=seq_name,
                    object_type='SEQUENCE',
                    status='VALID'
                )

        # Load tables
        for table_name, table_data in db_data.get('tables', {}).items():
            # Reconstruct schema
            schema_dict = table_data['schema']
            columns = []

            for col_dict in schema_dict['columns']:
                col = Column(
                    name=col_dict['name'],
                    data_type=DataType.from_string(col_dict.get('data_type') or col_dict.get('type')),
                    vector_dimension=col_dict.get('vector_dimension'),
                    nullable=col_dict.get('nullable', True),
                    primary_key=col_dict.get('primary_key', False),
                    unique=col_dict.get('unique', False),
                    default=col_dict.get('default'),
                    auto_increment=col_dict.get('auto_increment', False)
                )
                columns.append(col)

            schema = TableSchema(table_name, columns)
            table_store = TableStore(schema)

            # Restore auto-increment counter
            table_store._next_auto_increment = table_data.get('next_auto_increment', 1)

            # Load rows
            for row in table_data.get('rows', []):
                table_store.insert(row)

            self.tables[table_name] = table_store

            # Add to catalog
            self.catalog.add_object(
                owner=self.default_owner,
                object_name=table_name,
                object_type='TABLE',
                status='VALID'
            )

        # Load vector collections if auto-vectorization is enabled
        if self.auto_vectorizer and 'vector_collections' in db_data:
            vector_data = db_data['vector_collections']

            if vector_data.get('enabled'):
                # Restore vectorization metadata
                self.auto_vectorizer.vectorized_tables = vector_data.get('vectorized_tables', {})
                self.auto_vectorizer.table_text_columns = vector_data.get('table_text_columns', {})

                # Restore each vector collection
                for collection_name, coll_data in vector_data.get('collections', {}).items():
                    try:
                        from ..database import EzDB
                        import numpy as np

                        # Recreate the vector database
                        vector_db = EzDB(
                            dimension=coll_data['dimension'],
                            metric=coll_data['metric'],
                            index_type='hnsw'
                        )

                        # Restore vectors
                        vectors = coll_data.get('vectors', [])
                        ids = coll_data.get('ids', [])
                        metadata_list = coll_data.get('metadata', [])
                        documents = coll_data.get('documents', [])

                        if vectors:
                            # Convert lists back to numpy arrays
                            vectors_np = [np.array(vec, dtype=np.float32) for vec in vectors]

                            # Batch insert all vectors
                            vector_db.insert_batch(
                                vectors=vectors_np,
                                ids=ids,
                                metadata_list=metadata_list,
                                documents=documents
                            )

                            print(f"  ↳ Restored vector collection '{collection_name}' with {len(vectors)} vectors")

                        # Store the restored collection
                        self.auto_vectorizer.vector_collections[collection_name] = vector_db

                    except Exception as e:
                        print(f"WARNING: Failed to restore vector collection '{collection_name}': {e}")
                        import traceback
                        traceback.print_exc()

    def _execute_create_sequence(self, query: CreateSequenceQuery) -> Dict[str, Any]:
        """Execute CREATE SEQUENCE"""
        try:
            sequence = self.sequences.create_sequence(
                name=query.sequence_name,
                start_with=query.start_with,
                increment_by=query.increment_by,
                min_value=query.min_value,
                max_value=query.max_value,
                cycle=query.cycle,
                cache=query.cache,
                if_not_exists=query.if_not_exists
            )

            # Add to system catalog
            self.catalog.add_object(
                owner=self.default_owner,
                object_name=query.sequence_name.upper(),
                object_type='SEQUENCE',
                status='VALID'
            )

            # Auto-save
            self._auto_save()

            return {
                'status': 'success',
                'message': f"Sequence '{query.sequence_name}' created",
                'sequence': query.sequence_name,
                'start_with': query.start_with,
                'increment_by': query.increment_by
            }
        except ValueError as e:
            if query.if_not_exists and "already exists" in str(e):
                return {
                    'status': 'success',
                    'message': f"Sequence '{query.sequence_name}' already exists (IF NOT EXISTS)"
                }
            raise

    def _execute_drop_sequence(self, query: DropSequenceQuery) -> Dict[str, Any]:
        """Execute DROP SEQUENCE"""
        try:
            self.sequences.drop_sequence(query.sequence_name, query.if_exists)

            # Remove from system catalog
            self.catalog.remove_object(query.sequence_name.upper(), 'SEQUENCE')

            # Auto-save
            self._auto_save()

            return {
                'status': 'success',
                'message': f"Sequence '{query.sequence_name}' dropped",
                'sequence': query.sequence_name
            }
        except ValueError as e:
            if query.if_exists and "does not exist" in str(e):
                return {
                    'status': 'success',
                    'message': f"Sequence '{query.sequence_name}' does not exist (IF EXISTS)"
                }
            raise

    def _execute_alter_sequence(self, query: AlterSequenceQuery) -> Dict[str, Any]:
        """Execute ALTER SEQUENCE"""
        self.sequences.alter_sequence(
            name=query.sequence_name,
            increment_by=query.increment_by,
            min_value=query.min_value,
            max_value=query.max_value,
            cycle=query.cycle,
            cache=query.cache
        )

        # Update system catalog DDL time
        self.catalog.update_object_ddl_time(query.sequence_name.upper(), 'SEQUENCE')

        # Auto-save
        self._auto_save()

        return {
            'status': 'success',
            'message': f"Sequence '{query.sequence_name}' altered",
            'sequence': query.sequence_name
        }

    def _replace_sequence_calls(self, value: Any) -> Any:
        """
        Replace sequence NEXTVAL and CURRVAL calls with actual values.

        Args:
            value: Value that might contain sequence calls

        Returns:
            Value with sequence calls replaced
        """
        if not isinstance(value, str):
            return value

        # Check for NEXTVAL
        nextval_pattern = r'(\w+)\.NEXTVAL'
        match = re.match(nextval_pattern, value, re.IGNORECASE)
        if match:
            seq_name = match.group(1)
            return self.sequences.nextval(seq_name)

        # Check for CURRVAL
        currval_pattern = r'(\w+)\.CURRVAL'
        match = re.match(currval_pattern, value, re.IGNORECASE)
        if match:
            seq_name = match.group(1)
            return self.sequences.currval(seq_name)

        return value

    def _execute_create_trigger(self, query: CreateTriggerQuery) -> Dict[str, Any]:
        """Execute CREATE TRIGGER"""
        # Check if table exists
        if query.table_name not in self.tables:
            raise ValueError(f"Table '{query.table_name}' does not exist")

        # For SQLite backend, use storage trigger methods
        if self.backend_type == 'sqlite':
            self.storage.store.create_trigger(
                trigger_name=query.trigger_name,
                table_name=query.table_name,
                timing=query.timing,
                event=query.event,
                trigger_body=query.trigger_body,
                when_condition=query.when_condition,
                or_replace=query.or_replace
            )
        else:
            # For JSON backend, store in metadata
            if not hasattr(self, 'triggers'):
                self.triggers = {}

            if query.trigger_name in self.triggers and not query.or_replace:
                raise ValueError(f"Trigger '{query.trigger_name}' already exists")

            self.triggers[query.trigger_name] = {
                'trigger_name': query.trigger_name,
                'table_name': query.table_name,
                'timing': query.timing,
                'event': query.event,
                'trigger_body': query.trigger_body,
                'when_condition': query.when_condition
            }

        # Add to system catalog
        self.catalog.add_object(
            owner=self.default_owner,
            object_name=query.trigger_name,
            object_type='TRIGGER',
            status='VALID'
        )

        # Auto-save
        self._auto_save()

        return {
            'status': 'success',
            'message': f"Trigger '{query.trigger_name}' {'replaced' if query.or_replace else 'created'}",
            'trigger': query.trigger_name,
            'table': query.table_name,
            'timing': query.timing,
            'event': query.event
        }

    def _execute_drop_trigger(self, query: DropTriggerQuery) -> Dict[str, Any]:
        """Execute DROP TRIGGER"""
        # For SQLite backend, use storage trigger methods
        if self.backend_type == 'sqlite':
            try:
                self.storage.store.drop_trigger(query.trigger_name, query.if_exists)
            except ValueError as e:
                if not query.if_exists:
                    raise
                return {
                    'status': 'success',
                    'message': f"Trigger '{query.trigger_name}' does not exist (IF EXISTS)"
                }
        else:
            # For JSON backend
            if not hasattr(self, 'triggers'):
                self.triggers = {}

            if query.trigger_name not in self.triggers:
                if query.if_exists:
                    return {
                        'status': 'success',
                        'message': f"Trigger '{query.trigger_name}' does not exist (IF EXISTS)"
                    }
                else:
                    raise ValueError(f"Trigger '{query.trigger_name}' does not exist")

            del self.triggers[query.trigger_name]

        # Remove from system catalog
        self.catalog.remove_object(query.trigger_name, 'TRIGGER')

        # Auto-save
        self._auto_save()

        return {
            'status': 'success',
            'message': f"Trigger '{query.trigger_name}' dropped",
            'trigger': query.trigger_name
        }

    def _fire_triggers(self, table_name: str, event: str, timing: str,
                      old_row: Optional[Dict[str, Any]] = None,
                      new_row: Optional[Dict[str, Any]] = None):
        """
        Fire triggers for a given event.

        Args:
            table_name: Name of the table
            event: INSERT, UPDATE, or DELETE
            timing: BEFORE or AFTER
            old_row: Old row values (for UPDATE/DELETE)
            new_row: New row values (for INSERT/UPDATE)
        """
        # Get triggers for this table/event/timing
        if self.backend_type == 'sqlite':
            triggers = self.storage.store.get_triggers_for_event(table_name, event, timing)
        else:
            if not hasattr(self, 'triggers'):
                return
            triggers = [
                t for t in self.triggers.values()
                if t['table_name'] == table_name and t['event'] == event and t['timing'] == timing
            ]

        # Execute each trigger
        for trigger in triggers:
            # Check WHEN condition if specified
            if trigger.get('when_condition'):
                # Evaluate WHEN condition with OLD/NEW values
                # For simplicity, skip condition evaluation for now
                pass

            # Execute trigger body
            trigger_body = trigger['trigger_body']

            # Replace :NEW and :OLD references
            trigger_body = self._replace_trigger_references(trigger_body, old_row, new_row)

            # Execute each statement in the trigger body
            statements = [s.strip() for s in trigger_body.split(';') if s.strip()]
            for statement in statements:
                try:
                    self.execute(statement)
                except Exception as e:
                    # For BEFORE triggers, raise the error to prevent the main operation
                    if timing == 'BEFORE':
                        raise ValueError(f"Trigger '{trigger['trigger_name']}' failed: {str(e)}")
                    else:
                        # For AFTER triggers, log the error but continue
                        print(f"WARNING: Trigger '{trigger['trigger_name']}' failed: {str(e)}")

    def _replace_trigger_references(self, sql: str, old_row: Optional[Dict[str, Any]],
                                    new_row: Optional[Dict[str, Any]]) -> str:
        """
        Replace :OLD and :NEW references in trigger SQL.

        Args:
            sql: SQL statement with :OLD/:NEW references
            old_row: Old row values
            new_row: New row values

        Returns:
            SQL with references replaced by actual values
        """
        result = sql

        # Replace :NEW.column_name references
        if new_row:
            for col_name, col_value in new_row.items():
                pattern = f':NEW.{col_name}'
                if isinstance(col_value, str):
                    replacement = f"'{col_value}'"
                elif col_value is None:
                    replacement = 'NULL'
                else:
                    replacement = str(col_value)
                result = result.replace(pattern, replacement)

        # Replace :OLD.column_name references
        if old_row:
            for col_name, col_value in old_row.items():
                pattern = f':OLD.{col_name}'
                if isinstance(col_value, str):
                    replacement = f"'{col_value}'"
                elif col_value is None:
                    replacement = 'NULL'
                else:
                    replacement = str(col_value)
                result = result.replace(pattern, replacement)

        return result

    def _auto_save(self):
        """Auto-save database to file if db_file is set"""
        if self.db_file:
            if self.backend_type == 'sqlite':
                # For SQLite, RDBMS data is already persisted in the database
                # Save metadata (views, sequences) to separate file
                metadata_file = self.db_file.replace('.db', '_metadata.json')
                metadata = {
                    'views': self.views,
                    'sequences': self.sequences.to_dict()
                }
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)

                # Save vector collections to SQLite
                if self.auto_vectorizer:
                    for collection_name, vector_db in self.auto_vectorizer.vector_collections.items():
                        # Get all vectors from the collection
                        all_ids = vector_db.store.get_all_ids()
                        all_vectors = vector_db.store.get_all_vectors()
                        all_metadata = vector_db.store.get_all_metadata()
                        all_documents = vector_db.store.get_all_documents()

                        # Get metric as string (handle both Enum and string)
                        try:
                            metric_str = vector_db.metric.value  # For Enum
                        except AttributeError:
                            metric_str = str(vector_db.metric)  # For string

                        # Save to SQLite
                        self.storage.store.save_vectors(
                            collection_name=collection_name,
                            vectors=all_vectors,
                            ids=all_ids,
                            metadata_list=all_metadata,
                            documents=all_documents,
                            dimension=vector_db.dimension,
                            metric=metric_str
                        )
            else:
                # For JSON backend, save everything
                self.save_to_file(self.db_file)


class QueryExecutor:
    """
    Simplified executor interface for backward compatibility.
    Can be used standalone or integrated with existing EzDB.
    """

    def __init__(self, db_file: Optional[str] = None):
        """
        Initialize query executor.

        Args:
            db_file: Optional path to database file for persistence
        """
        self.engine = RDBMSEngine(db_file)

    def execute(self, sql: str) -> Dict[str, Any]:
        """Execute SQL and return results"""
        return self.engine.execute(sql)

    def execute_script(self, sql_script: str) -> List[Dict[str, Any]]:
        """
        Execute multiple SQL statements separated by semicolons.

        Args:
            sql_script: Multiple SQL statements separated by ;

        Returns:
            List of result dictionaries
        """
        results = []

        # Split by semicolon (simple approach)
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]

        for statement in statements:
            try:
                result = self.execute(statement)
                results.append(result)
            except Exception as e:
                results.append({
                    'status': 'error',
                    'error': str(e),
                    'statement': statement[:100]
                })

        return results
