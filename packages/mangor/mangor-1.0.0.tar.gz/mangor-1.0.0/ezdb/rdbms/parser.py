"""
SQL Parser for EzDB RDBMS
Parses DDL (Data Definition Language) and DML (Data Manipulation Language)
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from .schema import DataType, Column


class ParsedQuery:
    """Base class for parsed queries"""
    def __init__(self, query_type: str):
        self.query_type = query_type


class CreateTableQuery(ParsedQuery):
    """Parsed CREATE TABLE statement"""
    def __init__(self, table_name: str, columns: List[Column], if_not_exists: bool = False):
        super().__init__("CREATE_TABLE")
        self.table_name = table_name
        self.columns = columns
        self.if_not_exists = if_not_exists


class DropTableQuery(ParsedQuery):
    """Parsed DROP TABLE statement"""
    def __init__(self, table_name: str, if_exists: bool = False):
        super().__init__("DROP_TABLE")
        self.table_name = table_name
        self.if_exists = if_exists


class InsertQuery(ParsedQuery):
    """Parsed INSERT statement"""
    def __init__(self, table_name: str, columns: Optional[List[str]], values: List[List[Any]]):
        super().__init__("INSERT")
        self.table_name = table_name
        self.columns = columns
        self.values = values


class SelectQuery(ParsedQuery):
    """Parsed SELECT statement with derived table support"""
    def __init__(self,
                 columns: List[str],
                 from_table: str = None,
                 where: Optional[Dict[str, Any]] = None,
                 joins: Optional[List[Dict]] = None,
                 group_by: Optional[List[str]] = None,
                 having: Optional[Dict[str, Any]] = None,
                 order_by: Optional[List[Tuple[str, str]]] = None,
                 limit: Optional[int] = None,
                 offset: int = 0,
                 from_derived_table: Optional['SelectQuery'] = None,
                 derived_table_alias: Optional[str] = None):
        super().__init__("SELECT")
        self.columns = columns
        self.from_table = from_table
        self.where = where
        self.joins = joins or []
        self.group_by = group_by
        self.having = having
        self.order_by = order_by
        self.limit = limit
        self.offset = offset
        # Derived table support (Phase 4)
        self.from_derived_table = from_derived_table
        self.derived_table_alias = derived_table_alias


class UpdateQuery(ParsedQuery):
    """Parsed UPDATE statement"""
    def __init__(self, table_name: str, updates: Dict[str, Any], where: Optional[Dict[str, Any]] = None):
        super().__init__("UPDATE")
        self.table_name = table_name
        self.updates = updates
        self.where = where


class DeleteQuery(ParsedQuery):
    """Parsed DELETE statement"""
    def __init__(self, table_name: str, where: Optional[Dict[str, Any]] = None):
        super().__init__("DELETE")
        self.table_name = table_name
        self.where = where


class DescribeQuery(ParsedQuery):
    """Parsed DESCRIBE/DESC statement"""
    def __init__(self, table_name: str):
        super().__init__("DESCRIBE")
        self.table_name = table_name


class CreateViewQuery(ParsedQuery):
    """Parsed CREATE VIEW statement"""
    def __init__(self, view_name: str, select_query: str, or_replace: bool = False):
        super().__init__("CREATE_VIEW")
        self.view_name = view_name
        self.select_query = select_query  # Store the SELECT query as string
        self.or_replace = or_replace


class DropViewQuery(ParsedQuery):
    """Parsed DROP VIEW statement"""
    def __init__(self, view_name: str, if_exists: bool = False):
        super().__init__("DROP_VIEW")
        self.view_name = view_name
        self.if_exists = if_exists


class CreateSequenceQuery(ParsedQuery):
    """Parsed CREATE SEQUENCE statement"""
    def __init__(self, sequence_name: str, start_with: int = 1, increment_by: int = 1,
                 min_value: Optional[int] = None, max_value: Optional[int] = None,
                 cycle: bool = False, cache: int = 1, if_not_exists: bool = False):
        super().__init__("CREATE_SEQUENCE")
        self.sequence_name = sequence_name
        self.start_with = start_with
        self.increment_by = increment_by
        self.min_value = min_value
        self.max_value = max_value
        self.cycle = cycle
        self.cache = cache
        self.if_not_exists = if_not_exists


class DropSequenceQuery(ParsedQuery):
    """Parsed DROP SEQUENCE statement"""
    def __init__(self, sequence_name: str, if_exists: bool = False):
        super().__init__("DROP_SEQUENCE")
        self.sequence_name = sequence_name
        self.if_exists = if_exists


class AlterSequenceQuery(ParsedQuery):
    """Parsed ALTER SEQUENCE statement"""
    def __init__(self, sequence_name: str, increment_by: Optional[int] = None,
                 min_value: Optional[int] = None, max_value: Optional[int] = None,
                 cycle: Optional[bool] = None, cache: Optional[int] = None):
        super().__init__("ALTER_SEQUENCE")
        self.sequence_name = sequence_name
        self.increment_by = increment_by
        self.min_value = min_value
        self.max_value = max_value
        self.cycle = cycle
        self.cache = cache


class CreateTriggerQuery(ParsedQuery):
    """Parsed CREATE TRIGGER statement"""
    def __init__(self, trigger_name: str, timing: str, event: str, table_name: str,
                 trigger_body: str, or_replace: bool = False, when_condition: Optional[str] = None):
        super().__init__("CREATE_TRIGGER")
        self.trigger_name = trigger_name
        self.timing = timing  # BEFORE or AFTER
        self.event = event  # INSERT, UPDATE, or DELETE
        self.table_name = table_name
        self.trigger_body = trigger_body
        self.or_replace = or_replace
        self.when_condition = when_condition


class DropTriggerQuery(ParsedQuery):
    """Parsed DROP TRIGGER statement"""
    def __init__(self, trigger_name: str, if_exists: bool = False):
        super().__init__("DROP_TRIGGER")
        self.trigger_name = trigger_name
        self.if_exists = if_exists


class RDBMSParser:
    """Parser for SQL statements"""

    def parse(self, sql: str) -> ParsedQuery:
        """
        Parse a SQL statement and return appropriate query object.

        Args:
            sql: SQL statement string

        Returns:
            ParsedQuery subclass instance

        Raises:
            ValueError: If SQL is invalid or unsupported
        """
        # Remove SQL comments (-- style)
        lines = sql.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove comment part
            comment_pos = line.find('--')
            if comment_pos >= 0:
                line = line[:comment_pos]
            if line.strip():
                cleaned_lines.append(line)

        sql = '\n'.join(cleaned_lines).strip()

        if not sql:
            raise ValueError("Empty SQL statement")

        # Determine query type
        sql_upper = sql.upper()

        if sql_upper.startswith("CREATE OR REPLACE TRIGGER") or sql_upper.startswith("CREATE TRIGGER"):
            return self._parse_create_trigger(sql)
        elif sql_upper.startswith("CREATE OR REPLACE VIEW") or sql_upper.startswith("CREATE VIEW"):
            return self._parse_create_view(sql)
        elif sql_upper.startswith("CREATE SEQUENCE"):
            return self._parse_create_sequence(sql)
        elif sql_upper.startswith("CREATE TABLE"):
            return self._parse_create_table(sql)
        elif sql_upper.startswith("DROP TRIGGER"):
            return self._parse_drop_trigger(sql)
        elif sql_upper.startswith("DROP SEQUENCE"):
            return self._parse_drop_sequence(sql)
        elif sql_upper.startswith("DROP VIEW"):
            return self._parse_drop_view(sql)
        elif sql_upper.startswith("DROP TABLE"):
            return self._parse_drop_table(sql)
        elif sql_upper.startswith("ALTER SEQUENCE"):
            return self._parse_alter_sequence(sql)
        elif sql_upper.startswith("INSERT"):
            return self._parse_insert(sql)
        elif sql_upper.startswith("SELECT"):
            return self._parse_select(sql)
        elif sql_upper.startswith("UPDATE"):
            return self._parse_update(sql)
        elif sql_upper.startswith("DELETE"):
            return self._parse_delete(sql)
        elif sql_upper.startswith("DESCRIBE") or sql_upper.startswith("DESC "):
            return self._parse_describe(sql)
        else:
            raise ValueError(f"Unsupported SQL statement: {sql[:50]}...")

    def _parse_create_table(self, sql: str) -> CreateTableQuery:
        """
        Parse CREATE TABLE statement.

        Syntax:
            CREATE TABLE [IF NOT EXISTS] table_name (
                column1 datatype [constraints],
                column2 datatype [constraints],
                ...
            )
        """
        # Check for IF NOT EXISTS
        if_not_exists = bool(re.search(r'IF\s+NOT\s+EXISTS', sql, re.IGNORECASE))

        # Extract table name
        if if_not_exists:
            match = re.search(r'CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+(\w+)', sql, re.IGNORECASE)
        else:
            match = re.search(r'CREATE\s+TABLE\s+(\w+)', sql, re.IGNORECASE)

        if not match:
            raise ValueError("Invalid CREATE TABLE syntax: missing table name")

        table_name = match.group(1)

        # Extract column definitions
        # Find content between parentheses
        paren_match = re.search(r'\((.*)\)', sql, re.DOTALL)
        if not paren_match:
            raise ValueError("Invalid CREATE TABLE syntax: missing column definitions")

        columns_str = paren_match.group(1)
        columns = self._parse_column_definitions(columns_str)

        return CreateTableQuery(table_name, columns, if_not_exists)

    def _parse_column_definitions(self, columns_str: str) -> List[Column]:
        """Parse column definitions from CREATE TABLE"""
        columns = []

        # Split by comma, but respect parentheses (for VECTOR(n))
        column_defs = self._split_columns(columns_str)

        for col_def in column_defs:
            col_def = col_def.strip()
            if not col_def:
                continue

            # Parse: column_name datatype [constraints]
            parts = col_def.split()
            if len(parts) < 2:
                raise ValueError(f"Invalid column definition: {col_def}")

            col_name = parts[0]
            col_type_str = parts[1]

            # Extract vector dimension if VECTOR type
            vector_dim = None
            if col_type_str.upper().startswith("VECTOR"):
                dim_match = re.search(r'VECTOR\((\d+)\)', col_type_str, re.IGNORECASE)
                if dim_match:
                    vector_dim = int(dim_match.group(1))
                else:
                    raise ValueError(f"VECTOR type must specify dimension: VECTOR(n)")

            col_type = DataType.from_string(col_type_str)

            # Parse constraints
            constraints_str = ' '.join(parts[2:]).upper()
            nullable = 'NOT NULL' not in constraints_str
            primary_key = 'PRIMARY KEY' in constraints_str
            unique = 'UNIQUE' in constraints_str
            auto_increment = 'AUTO_INCREMENT' in constraints_str or 'AUTOINCREMENT' in constraints_str

            # Parse default value
            default = None
            default_match = re.search(r'DEFAULT\s+([^\s,]+)', constraints_str, re.IGNORECASE)
            if default_match:
                default = self._parse_value(default_match.group(1))

            column = Column(
                name=col_name,
                data_type=col_type,
                vector_dimension=vector_dim,
                nullable=nullable,
                primary_key=primary_key,
                unique=unique,
                default=default,
                auto_increment=auto_increment
            )
            columns.append(column)

        return columns

    def _split_columns(self, columns_str: str) -> List[str]:
        """Split column definitions by comma, respecting parentheses"""
        columns = []
        current = []
        paren_depth = 0

        for char in columns_str:
            if char == '(':
                paren_depth += 1
                current.append(char)
            elif char == ')':
                paren_depth -= 1
                current.append(char)
            elif char == ',' and paren_depth == 0:
                columns.append(''.join(current))
                current = []
            else:
                current.append(char)

        if current:
            columns.append(''.join(current))

        return columns

    def _parse_drop_table(self, sql: str) -> DropTableQuery:
        """Parse DROP TABLE statement"""
        if_exists = bool(re.search(r'IF\s+EXISTS', sql, re.IGNORECASE))

        if if_exists:
            match = re.search(r'DROP\s+TABLE\s+IF\s+EXISTS\s+(\w+)', sql, re.IGNORECASE)
        else:
            match = re.search(r'DROP\s+TABLE\s+(\w+)', sql, re.IGNORECASE)

        if not match:
            raise ValueError("Invalid DROP TABLE syntax")

        table_name = match.group(1)
        return DropTableQuery(table_name, if_exists)

    def _parse_insert(self, sql: str) -> InsertQuery:
        """
        Parse INSERT statement.

        Syntax:
            INSERT INTO table_name [(column1, column2, ...)] VALUES (value1, value2, ...), (...)
        """
        # Extract table name
        table_match = re.search(r'INSERT\s+INTO\s+(\w+)', sql, re.IGNORECASE)
        if not table_match:
            raise ValueError("Invalid INSERT syntax: missing table name")

        table_name = table_match.group(1)

        # Extract columns (optional)
        # Use DOTALL to handle multi-line column lists
        columns = None
        columns_match = re.search(r'INSERT\s+INTO\s+\w+\s*\((.*?)\)\s+VALUES', sql, re.IGNORECASE | re.DOTALL)
        if columns_match:
            columns = [col.strip() for col in columns_match.group(1).split(',')]

        # Extract values
        values_match = re.search(r'VALUES\s+(.+)', sql, re.IGNORECASE | re.DOTALL)
        if not values_match:
            raise ValueError("Invalid INSERT syntax: missing VALUES clause")

        values_str = values_match.group(1).strip()
        values = self._parse_insert_values(values_str)

        return InsertQuery(table_name, columns, values)

    def _parse_insert_values(self, values_str: str) -> List[List[Any]]:
        """Parse VALUES clause"""
        values = []

        # Find all value tuples: (val1, val2, ...)
        # Need to handle nested parentheses in strings properly
        tuple_strings = self._extract_value_tuples(values_str)

        for tuple_str in tuple_strings:
            # Split by comma and parse each value
            value_list = []
            for val_str in self._split_values(tuple_str):
                value = self._parse_value(val_str.strip())
                value_list.append(value)
            values.append(value_list)

        if not values:
            raise ValueError("Invalid VALUES clause")

        return values

    def _extract_value_tuples(self, values_str: str) -> List[str]:
        """Extract value tuples from VALUES clause, respecting quotes and nested parens"""
        tuples = []
        current = []
        paren_depth = 0
        in_quotes = False
        quote_char = None

        i = 0
        while i < len(values_str):
            char = values_str[i]

            # Handle quotes
            if char in ('"', "'"):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    # Check if it's an escaped quote (two consecutive quotes)
                    if i + 1 < len(values_str) and values_str[i + 1] == quote_char:
                        current.append(char)
                        i += 1  # Skip next quote
                    else:
                        in_quotes = False
                        quote_char = None
                current.append(char)
            # Handle parentheses (only when not in quotes)
            elif char == '(' and not in_quotes:
                paren_depth += 1
                if paren_depth > 1:
                    current.append(char)
            elif char == ')' and not in_quotes:
                paren_depth -= 1
                if paren_depth == 0:
                    # End of tuple
                    tuples.append(''.join(current))
                    current = []
                else:
                    current.append(char)
            # Regular characters
            elif paren_depth > 0:
                current.append(char)

            i += 1

        return tuples

    def _split_values(self, values_str: str) -> List[str]:
        """Split values by comma, respecting quotes and brackets"""
        values = []
        current = []
        in_quotes = False
        quote_char = None
        in_brackets = 0

        for i, char in enumerate(values_str):
            if char in ('"', "'") and (i == 0 or values_str[i-1] != '\\'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                current.append(char)
            elif char == '[' and not in_quotes:
                in_brackets += 1
                current.append(char)
            elif char == ']' and not in_quotes:
                in_brackets -= 1
                current.append(char)
            elif char == ',' and not in_quotes and in_brackets == 0:
                values.append(''.join(current))
                current = []
            else:
                current.append(char)

        if current:
            values.append(''.join(current))

        return values

    def _parse_value(self, value_str: str) -> Any:
        """Parse a single value"""
        value_str = value_str.strip()

        # NULL
        if value_str.upper() == 'NULL':
            return None

        # Boolean
        if value_str.upper() in ('TRUE', 'FALSE'):
            return value_str.upper() == 'TRUE'

        # String (quoted)
        if (value_str.startswith("'") and value_str.endswith("'")) or \
           (value_str.startswith('"') and value_str.endswith('"')):
            return value_str[1:-1]

        # Array/Vector (for VECTOR type)
        if value_str.startswith('[') and value_str.endswith(']'):
            # Parse as JSON-like array
            import json
            try:
                return json.loads(value_str)
            except:
                raise ValueError(f"Invalid array value: {value_str}")

        # Number
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            # If all else fails, treat as unquoted string
            return value_str

    def _parse_select(self, sql: str) -> SelectQuery:
        """Parse SELECT statement with JOIN support"""
        # Extract SELECT columns
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
        if not select_match:
            raise ValueError("Invalid SELECT syntax: missing SELECT or FROM clause")

        columns_str = select_match.group(1).strip()
        # Use _split_columns to respect parentheses in function calls
        columns = [col.strip() for col in self._split_columns(columns_str)]

        # Extract FROM clause - could be table name or derived table (subquery)
        from_table = None
        from_derived_table = None
        derived_table_alias = None
        table_aliases = {}

        # Check if FROM clause contains a derived table (subquery in FROM)
        # Pattern: FROM (SELECT ...) [alias]
        # Use balanced parenthesis matching instead of regex to handle nested queries
        from_pos = sql.upper().find('FROM')
        paren_match = None
        if from_pos != -1:
            # Look for opening ( after FROM
            remainder = sql[from_pos:]
            paren_match = re.search(r'FROM\s+\(', remainder, re.IGNORECASE)

        if paren_match:
            # Found FROM ( - this is a derived table
            # Find the matching closing ) using balanced parenthesis counting
            paren_start = from_pos + paren_match.end() - 1  # Position of opening (
            depth = 0
            paren_end = None

            for i in range(paren_start, len(sql)):
                if sql[i] == '(':
                    depth += 1
                elif sql[i] == ')':
                    depth -= 1
                    if depth == 0:
                        paren_end = i
                        break

            if paren_end:
                # Extract subquery between balanced parentheses
                subquery_sql = sql[paren_start + 1:paren_end].strip()

                # Look for optional alias after the closing )
                after_paren = sql[paren_end + 1:].strip()
                alias_match = re.match(r'^(\w+)', after_paren)
                derived_table_alias = alias_match.group(1) if alias_match else "derived_1"

                # Recursively parse the subquery
                from_derived_table = self._parse_select(subquery_sql)

                # Store alias for the derived table
                table_aliases[derived_table_alias] = derived_table_alias

        else:
            # Regular table case
            # Pattern: FROM table_name [alias] [JOIN ...]
            from_match = re.search(r'FROM\s+(\w+)(?:\s+(\w+))?\s*(?:LEFT\s+JOIN|INNER\s+JOIN|JOIN|WHERE|ORDER|GROUP|LIMIT|;|$)',
                                  sql, re.IGNORECASE | re.DOTALL)
            if not from_match:
                raise ValueError("Invalid SELECT syntax: missing FROM clause")

            from_table = from_match.group(1)
            from_alias = from_match.group(2) if from_match.group(2) else None

            # Store table aliases for reference
            table_aliases = {from_table: from_table}
            if from_alias:
                table_aliases[from_alias] = from_table

        # Extract JOIN clauses
        joins = []
        join_pattern = r'(LEFT\s+JOIN|INNER\s+JOIN|JOIN)\s+(\w+)(?:\s+(\w+))?\s+ON\s+([\w.]+)\s*=\s*([\w.]+)'
        for join_match in re.finditer(join_pattern, sql, re.IGNORECASE):
            join_type = join_match.group(1).upper()
            join_table = join_match.group(2)
            join_alias = join_match.group(3) if join_match.group(3) else None
            left_col = join_match.group(4)
            right_col = join_match.group(5)

            # Store join table alias
            if join_alias:
                table_aliases[join_alias] = join_table

            joins.append({
                'type': 'LEFT' if 'LEFT' in join_type else 'INNER',
                'table': join_table,
                'alias': join_alias,
                'on_left': left_col,
                'on_right': right_col
            })

        # Extract WHERE clause
        # NOTE: If there's a derived table, we need to search for WHERE clause AFTER the derived table,
        # not inside it. Otherwise we'll incorrectly capture the inner query's WHERE clause.
        where = None
        if from_derived_table:
            # For derived table queries, look for WHERE clause after the closing )
            # Pattern: ) [alias] WHERE ...
            where_match = re.search(r'\)(?:\s+\w+)?\s+WHERE\s+(.*?)(?:\s+ORDER\s+BY|\s+GROUP\s+BY|\s+LIMIT|$)',
                                   sql, re.IGNORECASE | re.DOTALL)
            if where_match:
                where = self._parse_where_clause(where_match.group(1).strip())
        else:
            # For regular table queries, normal WHERE clause search
            where_match = re.search(r'WHERE\s+(.*?)(?:\s+ORDER\s+BY|\s+GROUP\s+BY|\s+LIMIT|$)',
                                   sql, re.IGNORECASE | re.DOTALL)
            if where_match:
                where = self._parse_where_clause(where_match.group(1).strip())

        # Extract ORDER BY clause
        # NOTE: Same as WHERE and GROUP BY - if there's a derived table, search after the derived table
        order_by = None
        if from_derived_table:
            # For derived table queries, look for ORDER BY after the closing )
            order_match = re.search(r'\)(?:\s+\w+)?\s+ORDER\s+BY\s+(.*?)(?:\s+LIMIT|$)',
                                   sql, re.IGNORECASE | re.DOTALL)
            if order_match:
                order_by = []
                order_str = order_match.group(1).strip()
                for order_item in order_str.split(','):
                    order_item = order_item.strip()
                    parts = order_item.split()
                    col = parts[0]
                    direction = parts[1].upper() if len(parts) > 1 else 'ASC'
                    order_by.append((col, direction))
        else:
            # For regular table queries, normal ORDER BY search
            order_match = re.search(r'ORDER\s+BY\s+(.*?)(?:\s+LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
            if order_match:
                order_by = []
                order_str = order_match.group(1).strip()
                for order_item in order_str.split(','):
                    order_item = order_item.strip()
                    parts = order_item.split()
                    col = parts[0]
                    direction = parts[1].upper() if len(parts) > 1 else 'ASC'
                    order_by.append((col, direction))

        # Extract LIMIT and OFFSET
        # NOTE: Same as WHERE, GROUP BY, ORDER BY - if there's a derived table, search after it
        limit = None
        offset = 0
        if from_derived_table:
            # For derived table queries, look for LIMIT after the closing )
            limit_match = re.search(r'\)(?:\s+\w+)?\s+LIMIT\s+(\d+)(?:\s+OFFSET\s+(\d+))?',
                                   sql, re.IGNORECASE)
            if limit_match:
                limit = int(limit_match.group(1))
                if limit_match.group(2):
                    offset = int(limit_match.group(2))
        else:
            # For regular table queries, normal LIMIT search
            limit_match = re.search(r'LIMIT\s+(\d+)(?:\s+OFFSET\s+(\d+))?', sql, re.IGNORECASE)
            if limit_match:
                limit = int(limit_match.group(1))
                if limit_match.group(2):
                    offset = int(limit_match.group(2))

        # Extract GROUP BY clause
        # NOTE: Same as WHERE clause - if there's a derived table, we need to search for GROUP BY
        # AFTER the derived table, not inside it.
        group_by = None
        if from_derived_table:
            # For derived table queries, look for GROUP BY after the closing )
            # Pattern: ) [alias] GROUP BY ...
            group_match = re.search(r'\)(?:\s+\w+)?\s+GROUP\s+BY\s+(.*?)(?:\s+HAVING|\s+ORDER\s+BY|\s+LIMIT|$)',
                                   sql, re.IGNORECASE | re.DOTALL)
            if group_match:
                group_by = [col.strip() for col in group_match.group(1).split(',')]
        else:
            # For regular table queries, normal GROUP BY search
            group_match = re.search(r'GROUP\s+BY\s+(.*?)(?:\s+HAVING|\s+ORDER\s+BY|\s+LIMIT|$)',
                                   sql, re.IGNORECASE | re.DOTALL)
            if group_match:
                group_by = [col.strip() for col in group_match.group(1).split(',')]

        return SelectQuery(
            columns=columns,
            from_table=from_table,
            where=where,
            joins=joins if joins else None,
            group_by=group_by,
            order_by=order_by,
            limit=limit,
            offset=offset,
            from_derived_table=from_derived_table,
            derived_table_alias=derived_table_alias
        )

    def _parse_update(self, sql: str) -> UpdateQuery:
        """Parse UPDATE statement"""
        # Extract table name
        table_match = re.search(r'UPDATE\s+(\w+)\s+SET', sql, re.IGNORECASE)
        if not table_match:
            raise ValueError("Invalid UPDATE syntax")

        table_name = table_match.group(1)

        # Extract SET clause
        set_match = re.search(r'SET\s+(.*?)(?:\s+WHERE|$)', sql, re.IGNORECASE | re.DOTALL)
        if not set_match:
            raise ValueError("Invalid UPDATE syntax: missing SET clause")

        updates = self._parse_set_clause(set_match.group(1))

        # Extract WHERE clause (optional)
        where = None
        where_match = re.search(r'WHERE\s+(.+)', sql, re.IGNORECASE | re.DOTALL)
        if where_match:
            where = self._parse_where_clause(where_match.group(1))

        return UpdateQuery(table_name, updates, where)

    def _parse_set_clause(self, set_str: str) -> Dict[str, Any]:
        """Parse SET clause from UPDATE"""
        updates = {}
        assignments = set_str.split(',')

        for assignment in assignments:
            parts = assignment.split('=', 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid SET clause: {assignment}")

            col_name = parts[0].strip()
            value = self._parse_value(parts[1].strip())
            updates[col_name] = value

        return updates

    def _parse_delete(self, sql: str) -> DeleteQuery:
        """Parse DELETE statement"""
        # Extract table name
        table_match = re.search(r'DELETE\s+FROM\s+(\w+)', sql, re.IGNORECASE)
        if not table_match:
            raise ValueError("Invalid DELETE syntax")

        table_name = table_match.group(1)

        # Extract WHERE clause (optional)
        where = None
        where_match = re.search(r'WHERE\s+(.+)', sql, re.IGNORECASE | re.DOTALL)
        if where_match:
            where = self._parse_where_clause(where_match.group(1))

        return DeleteQuery(table_name, where)

    def _parse_where_clause(self, where_str: str) -> Dict[str, Any]:
        """Parse WHERE clause (reuse existing parser logic)"""
        from ..sql_parser import SQLParser

        parser = SQLParser()
        # Use existing WHERE parser
        return parser._parse_where(where_str)

    def _parse_describe(self, sql: str) -> DescribeQuery:
        """
        Parse DESCRIBE/DESC statement.

        Syntax:
            DESCRIBE table_name
            DESC table_name
        """
        # Extract table name
        match = re.search(r'(?:DESCRIBE|DESC)\s+(\w+)', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DESCRIBE syntax: missing table name")

        table_name = match.group(1)
        return DescribeQuery(table_name)

    def _parse_create_view(self, sql: str) -> CreateViewQuery:
        """
        Parse CREATE VIEW statement.

        Syntax:
            CREATE [OR REPLACE] VIEW view_name AS select_statement
        """
        # Check for OR REPLACE
        or_replace = bool(re.search(r'CREATE\s+OR\s+REPLACE\s+VIEW', sql, re.IGNORECASE))

        # Extract view name
        if or_replace:
            match = re.search(r'CREATE\s+OR\s+REPLACE\s+VIEW\s+(\w+)\s+AS', sql, re.IGNORECASE)
        else:
            match = re.search(r'CREATE\s+VIEW\s+(\w+)\s+AS', sql, re.IGNORECASE)

        if not match:
            raise ValueError("Invalid CREATE VIEW syntax: missing view name or AS clause")

        view_name = match.group(1)

        # Extract SELECT query
        as_match = re.search(r'\bAS\s+(.+)', sql, re.IGNORECASE | re.DOTALL)
        if not as_match:
            raise ValueError("Invalid CREATE VIEW syntax: missing AS clause")

        select_query = as_match.group(1).strip()

        # Remove trailing semicolon if present
        select_query = select_query.rstrip(';').strip()

        return CreateViewQuery(view_name, select_query, or_replace)

    def _parse_drop_view(self, sql: str) -> DropViewQuery:
        """
        Parse DROP VIEW statement.

        Syntax:
            DROP VIEW [IF EXISTS] view_name
        """
        if_exists = bool(re.search(r'IF\s+EXISTS', sql, re.IGNORECASE))

        if if_exists:
            match = re.search(r'DROP\s+VIEW\s+IF\s+EXISTS\s+(\w+)', sql, re.IGNORECASE)
        else:
            match = re.search(r'DROP\s+VIEW\s+(\w+)', sql, re.IGNORECASE)

        if not match:
            raise ValueError("Invalid DROP VIEW syntax: missing view name")

        view_name = match.group(1)
        return DropViewQuery(view_name, if_exists)

    def _parse_create_sequence(self, sql: str) -> CreateSequenceQuery:
        """
        Parse CREATE SEQUENCE statement.

        Syntax:
            CREATE SEQUENCE [IF NOT EXISTS] sequence_name
                [START WITH n]
                [INCREMENT BY n]
                [MINVALUE n | NOMINVALUE]
                [MAXVALUE n | NOMAXVALUE]
                [CYCLE | NOCYCLE]
                [CACHE n]
        """
        # Check for IF NOT EXISTS
        if_not_exists = bool(re.search(r'IF\s+NOT\s+EXISTS', sql, re.IGNORECASE))

        # Extract sequence name
        if if_not_exists:
            match = re.search(r'CREATE\s+SEQUENCE\s+IF\s+NOT\s+EXISTS\s+(\w+)', sql, re.IGNORECASE)
        else:
            match = re.search(r'CREATE\s+SEQUENCE\s+(\w+)', sql, re.IGNORECASE)

        if not match:
            raise ValueError("Invalid CREATE SEQUENCE syntax: missing sequence name")

        sequence_name = match.group(1)

        # Extract optional parameters
        start_with = 1
        increment_by = 1
        min_value = None
        max_value = None
        cycle = False
        cache = 1

        # START WITH
        start_match = re.search(r'START\s+WITH\s+(-?\d+)', sql, re.IGNORECASE)
        if start_match:
            start_with = int(start_match.group(1))

        # INCREMENT BY
        incr_match = re.search(r'INCREMENT\s+BY\s+(-?\d+)', sql, re.IGNORECASE)
        if incr_match:
            increment_by = int(incr_match.group(1))

        # MINVALUE
        if re.search(r'NOMINVALUE', sql, re.IGNORECASE):
            min_value = None
        else:
            min_match = re.search(r'MINVALUE\s+(-?\d+)', sql, re.IGNORECASE)
            if min_match:
                min_value = int(min_match.group(1))

        # MAXVALUE
        if re.search(r'NOMAXVALUE', sql, re.IGNORECASE):
            max_value = None
        else:
            max_match = re.search(r'MAXVALUE\s+(-?\d+)', sql, re.IGNORECASE)
            if max_match:
                max_value = int(max_match.group(1))

        # CYCLE
        if re.search(r'\bCYCLE\b', sql, re.IGNORECASE) and not re.search(r'NOCYCLE', sql, re.IGNORECASE):
            cycle = True
        elif re.search(r'NOCYCLE', sql, re.IGNORECASE):
            cycle = False

        # CACHE
        cache_match = re.search(r'CACHE\s+(\d+)', sql, re.IGNORECASE)
        if cache_match:
            cache = int(cache_match.group(1))

        return CreateSequenceQuery(
            sequence_name=sequence_name,
            start_with=start_with,
            increment_by=increment_by,
            min_value=min_value,
            max_value=max_value,
            cycle=cycle,
            cache=cache,
            if_not_exists=if_not_exists
        )

    def _parse_drop_sequence(self, sql: str) -> DropSequenceQuery:
        """
        Parse DROP SEQUENCE statement.

        Syntax:
            DROP SEQUENCE [IF EXISTS] sequence_name
        """
        if_exists = bool(re.search(r'IF\s+EXISTS', sql, re.IGNORECASE))

        if if_exists:
            match = re.search(r'DROP\s+SEQUENCE\s+IF\s+EXISTS\s+(\w+)', sql, re.IGNORECASE)
        else:
            match = re.search(r'DROP\s+SEQUENCE\s+(\w+)', sql, re.IGNORECASE)

        if not match:
            raise ValueError("Invalid DROP SEQUENCE syntax: missing sequence name")

        sequence_name = match.group(1)
        return DropSequenceQuery(sequence_name, if_exists)

    def _parse_alter_sequence(self, sql: str) -> AlterSequenceQuery:
        """
        Parse ALTER SEQUENCE statement.

        Syntax:
            ALTER SEQUENCE sequence_name
                [INCREMENT BY n]
                [MINVALUE n | NOMINVALUE]
                [MAXVALUE n | NOMAXVALUE]
                [CYCLE | NOCYCLE]
                [CACHE n]
        """
        # Extract sequence name
        match = re.search(r'ALTER\s+SEQUENCE\s+(\w+)', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid ALTER SEQUENCE syntax: missing sequence name")

        sequence_name = match.group(1)

        # Extract optional parameters
        increment_by = None
        min_value = None
        max_value = None
        cycle = None
        cache = None

        # INCREMENT BY
        incr_match = re.search(r'INCREMENT\s+BY\s+(-?\d+)', sql, re.IGNORECASE)
        if incr_match:
            increment_by = int(incr_match.group(1))

        # MINVALUE
        if re.search(r'NOMINVALUE', sql, re.IGNORECASE):
            min_value = None  # Reset to default
        else:
            min_match = re.search(r'MINVALUE\s+(-?\d+)', sql, re.IGNORECASE)
            if min_match:
                min_value = int(min_match.group(1))

        # MAXVALUE
        if re.search(r'NOMAXVALUE', sql, re.IGNORECASE):
            max_value = None  # Reset to default
        else:
            max_match = re.search(r'MAXVALUE\s+(-?\d+)', sql, re.IGNORECASE)
            if max_match:
                max_value = int(max_match.group(1))

        # CYCLE
        if re.search(r'\bCYCLE\b', sql, re.IGNORECASE) and not re.search(r'NOCYCLE', sql, re.IGNORECASE):
            cycle = True
        elif re.search(r'NOCYCLE', sql, re.IGNORECASE):
            cycle = False

        # CACHE
        cache_match = re.search(r'CACHE\s+(\d+)', sql, re.IGNORECASE)
        if cache_match:
            cache = int(cache_match.group(1))

        return AlterSequenceQuery(
            sequence_name=sequence_name,
            increment_by=increment_by,
            min_value=min_value,
            max_value=max_value,
            cycle=cycle,
            cache=cache
        )

    def _parse_create_trigger(self, sql: str) -> CreateTriggerQuery:
        """
        Parse CREATE TRIGGER statement.

        Syntax:
            CREATE [OR REPLACE] TRIGGER trigger_name
                {BEFORE | AFTER} {INSERT | UPDATE | DELETE}
                ON table_name
                [FOR EACH ROW]
                [WHEN (condition)]
            BEGIN
                -- trigger body statements
            END;
        """
        # Check for OR REPLACE
        or_replace = bool(re.search(r'CREATE\s+OR\s+REPLACE\s+TRIGGER', sql, re.IGNORECASE))

        # Extract trigger name
        if or_replace:
            match = re.search(r'CREATE\s+OR\s+REPLACE\s+TRIGGER\s+(\w+)', sql, re.IGNORECASE)
        else:
            match = re.search(r'CREATE\s+TRIGGER\s+(\w+)', sql, re.IGNORECASE)

        if not match:
            raise ValueError("Invalid CREATE TRIGGER syntax: missing trigger name")

        trigger_name = match.group(1)

        # Extract timing (BEFORE or AFTER)
        timing_match = re.search(r'\b(BEFORE|AFTER)\b', sql, re.IGNORECASE)
        if not timing_match:
            raise ValueError("Invalid CREATE TRIGGER syntax: missing BEFORE/AFTER timing")

        timing = timing_match.group(1).upper()

        # Extract event (INSERT, UPDATE, or DELETE)
        event_match = re.search(r'\b(INSERT|UPDATE|DELETE)\b', sql, re.IGNORECASE)
        if not event_match:
            raise ValueError("Invalid CREATE TRIGGER syntax: missing INSERT/UPDATE/DELETE event")

        event = event_match.group(1).upper()

        # Extract table name
        table_match = re.search(r'\bON\s+(\w+)', sql, re.IGNORECASE)
        if not table_match:
            raise ValueError("Invalid CREATE TRIGGER syntax: missing ON table_name")

        table_name = table_match.group(1)

        # Extract WHEN condition (optional)
        when_condition = None
        when_match = re.search(r'\bWHEN\s*\((.*?)\)\s*BEGIN', sql, re.IGNORECASE | re.DOTALL)
        if when_match:
            when_condition = when_match.group(1).strip()

        # Extract trigger body (between BEGIN and END)
        body_match = re.search(r'\bBEGIN\s+(.*?)\s+END', sql, re.IGNORECASE | re.DOTALL)
        if not body_match:
            raise ValueError("Invalid CREATE TRIGGER syntax: missing BEGIN...END block")

        trigger_body = body_match.group(1).strip()

        return CreateTriggerQuery(
            trigger_name=trigger_name,
            timing=timing,
            event=event,
            table_name=table_name,
            trigger_body=trigger_body,
            or_replace=or_replace,
            when_condition=when_condition
        )

    def _parse_drop_trigger(self, sql: str) -> DropTriggerQuery:
        """
        Parse DROP TRIGGER statement.

        Syntax:
            DROP TRIGGER [IF EXISTS] trigger_name
        """
        if_exists = bool(re.search(r'IF\s+EXISTS', sql, re.IGNORECASE))

        if if_exists:
            match = re.search(r'DROP\s+TRIGGER\s+IF\s+EXISTS\s+(\w+)', sql, re.IGNORECASE)
        else:
            match = re.search(r'DROP\s+TRIGGER\s+(\w+)', sql, re.IGNORECASE)

        if not match:
            raise ValueError("Invalid DROP TRIGGER syntax: missing trigger name")

        trigger_name = match.group(1)
        return DropTriggerQuery(trigger_name, if_exists)
