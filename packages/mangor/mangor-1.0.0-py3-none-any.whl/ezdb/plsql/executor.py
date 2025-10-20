"""
PL/SQL Executor
Interprets and executes PL/SQL AST nodes
"""

import re
from typing import Any, Dict, List, Optional
from .parser import (
    PLSQLBlock, Declaration, Assignment, IfStatement, LoopStatement,
    ExitStatement, SQLStatement, OutputStatement, ExceptionHandler,
    CursorDeclaration, CursorStatement, CursorForLoop,
    ProcedureDefinition, FunctionDefinition, CallStatement, ReturnStatement, Parameter,
    PackageSpecification, PackageBody, ProcedureSignature, FunctionSignature,
    RecordTypeDeclaration, RecordField, RecordVariableDeclaration, RecordAccess, RecordAssignment,
    CollectionTypeDeclaration, CollectionVariableDeclaration, CollectionAccess, CollectionMethod,
    TypeAttributeDeclaration,
    ExecuteImmediateStatement, PragmaStatement, PipelineStatement, BulkCollectStatement, ForallStatement
)


class Cursor:
    """Represents a cursor state"""

    def __init__(self, query: str):
        self.query = query
        self.is_open = False
        self.rows = []
        self.current_row = 0
        self.row_count = 0

    def open(self, rdbms_engine):
        """Open cursor and execute query"""
        if self.is_open:
            raise RuntimeError("Cursor already open")

        result = rdbms_engine.execute(self.query)
        if result['status'] == 'success':
            self.rows = result.get('rows', [])
            self.row_count = len(self.rows)
            self.current_row = 0
            self.is_open = True
        else:
            raise RuntimeError(f"Cursor open failed: {result.get('error', 'Unknown error')}")

    def fetch(self) -> Optional[Dict[str, Any]]:
        """Fetch next row"""
        if not self.is_open:
            raise RuntimeError("Cursor not open")

        if self.current_row < self.row_count:
            row = self.rows[self.current_row]
            self.current_row += 1
            return row
        return None

    def close(self):
        """Close cursor"""
        if not self.is_open:
            raise RuntimeError("Cursor not open")
        self.is_open = False
        self.rows = []
        self.current_row = 0


class RecordType:
    """Represents a RECORD type definition"""

    def __init__(self, type_name: str, fields: Dict[str, str]):
        self.type_name = type_name
        self.fields = fields  # Dict[field_name, field_type]


class RecordInstance:
    """Represents an instance of a RECORD type"""

    def __init__(self, record_type: RecordType):
        self.record_type = record_type
        self.values = {}  # Dict[field_name, value]

        # Initialize all fields to None
        for field_name in record_type.fields:
            self.values[field_name] = None

    def get_field(self, field_name: str) -> Any:
        """Get field value"""
        field_name_upper = field_name.upper()
        if field_name_upper not in self.values:
            raise AttributeError(f"Record has no field '{field_name}'")
        return self.values[field_name_upper]

    def set_field(self, field_name: str, value: Any):
        """Set field value"""
        field_name_upper = field_name.upper()
        if field_name_upper not in self.values:
            raise AttributeError(f"Record has no field '{field_name}'")
        self.values[field_name_upper] = value


class AssociativeArray:
    """Represents an associative array (INDEX BY)"""

    def __init__(self, element_type: str, index_type: str):
        self.element_type = element_type
        self.index_type = index_type
        self.data = {}  # Sparse storage

    def get(self, index):
        """Get element at index"""
        return self.data.get(index)

    def set(self, index, value):
        """Set element at index"""
        self.data[index] = value

    def exists(self, index) -> bool:
        """Check if index exists"""
        return index in self.data

    def count(self) -> int:
        """Get number of elements"""
        return len(self.data)

    def first(self):
        """Get first index"""
        if not self.data:
            return None
        return min(self.data.keys())

    def last(self):
        """Get last index"""
        if not self.data:
            return None
        return max(self.data.keys())

    def next(self, index):
        """Get next index after given index"""
        keys = sorted([k for k in self.data.keys() if k > index])
        return keys[0] if keys else None

    def prior(self, index):
        """Get previous index before given index"""
        keys = sorted([k for k in self.data.keys() if k < index], reverse=True)
        return keys[0] if keys else None

    def delete(self, index=None, end_index=None):
        """Delete element(s)"""
        if index is None:
            # Delete all
            self.data.clear()
        elif end_index is None:
            # Delete single element
            if index in self.data:
                del self.data[index]
        else:
            # Delete range
            for i in list(self.data.keys()):
                if index <= i <= end_index:
                    del self.data[i]


class NestedTable:
    """Represents a nested table"""

    def __init__(self, element_type: str):
        self.element_type = element_type
        self.data = []  # Dense storage (1-indexed)

    def get(self, index: int):
        """Get element at index (1-indexed)"""
        if index < 1 or index > len(self.data):
            raise IndexError(f"Index {index} out of range")
        return self.data[index - 1]

    def set(self, index: int, value):
        """Set element at index (1-indexed)"""
        if index < 1 or index > len(self.data):
            raise IndexError(f"Index {index} out of range")
        self.data[index - 1] = value

    def count(self) -> int:
        """Get number of elements"""
        return len(self.data)

    def exists(self, index: int) -> bool:
        """Check if index exists"""
        return 1 <= index <= len(self.data)

    def first(self) -> int:
        """Get first index"""
        return 1 if self.data else None

    def last(self) -> int:
        """Get last index"""
        return len(self.data) if self.data else None

    def next(self, index: int):
        """Get next index after given index"""
        if index < len(self.data):
            return index + 1
        return None

    def prior(self, index: int):
        """Get previous index before given index"""
        if index > 1:
            return index - 1
        return None

    def extend(self, n: int = 1, copy_index: int = None):
        """Add n elements, optionally copying from copy_index"""
        if copy_index is not None:
            # EXTEND(n, i) - add n copies of element at index i
            if copy_index < 1 or copy_index > len(self.data):
                raise IndexError(f"Copy index {copy_index} out of range")
            copy_value = self.data[copy_index - 1]
            for _ in range(n):
                self.data.append(copy_value)
        else:
            # EXTEND or EXTEND(n) - add n NULL elements
            for _ in range(n):
                self.data.append(None)

    def trim(self, n: int = 1):
        """Remove n elements from end"""
        for _ in range(min(n, len(self.data))):
            self.data.pop()

    def delete(self, index: int = None, end_index: int = None):
        """Delete element(s)"""
        if index is None:
            # DELETE - delete all elements
            self.data.clear()
        elif end_index is None:
            # DELETE(i) - delete single element at index i
            if 1 <= index <= len(self.data):
                self.data[index - 1] = None  # Mark as deleted but keep position
        else:
            # DELETE(i, j) - delete range of elements
            for i in range(index, min(end_index + 1, len(self.data) + 1)):
                if 1 <= i <= len(self.data):
                    self.data[i - 1] = None


class VArray:
    """Represents a VARRAY (variable-size array)"""

    def __init__(self, element_type: str, max_size: int):
        self.element_type = element_type
        self.max_size = max_size
        self.data = []  # Dense storage (1-indexed)

    def get(self, index: int):
        """Get element at index (1-indexed)"""
        if index < 1 or index > len(self.data):
            raise IndexError(f"Index {index} out of range")
        return self.data[index - 1]

    def set(self, index: int, value):
        """Set element at index (1-indexed)"""
        if index < 1 or index > len(self.data):
            raise IndexError(f"Index {index} out of range")
        self.data[index - 1] = value

    def count(self) -> int:
        """Get number of elements"""
        return len(self.data)

    def limit(self) -> int:
        """Get maximum size"""
        return self.max_size

    def exists(self, index: int) -> bool:
        """Check if index exists"""
        return 1 <= index <= len(self.data)

    def first(self) -> int:
        """Get first index"""
        return 1 if self.data else None

    def last(self) -> int:
        """Get last index"""
        return len(self.data) if self.data else None

    def next(self, index: int):
        """Get next index after given index"""
        if index < len(self.data):
            return index + 1
        return None

    def prior(self, index: int):
        """Get previous index before given index"""
        if index > 1:
            return index - 1
        return None

    def extend(self, n: int = 1, copy_index: int = None):
        """Add n elements, optionally copying from copy_index"""
        if len(self.data) + n > self.max_size:
            raise RuntimeError(f"Cannot extend beyond max size {self.max_size}")

        if copy_index is not None:
            # EXTEND(n, i) - add n copies of element at index i
            if copy_index < 1 or copy_index > len(self.data):
                raise IndexError(f"Copy index {copy_index} out of range")
            copy_value = self.data[copy_index - 1]
            for _ in range(n):
                self.data.append(copy_value)
        else:
            # EXTEND or EXTEND(n) - add n NULL elements
            for _ in range(n):
                self.data.append(None)

    def trim(self, n: int = 1):
        """Remove n elements from end"""
        for _ in range(min(n, len(self.data))):
            self.data.pop()

    def delete(self, index: int = None, end_index: int = None):
        """Delete element(s) - for VARRAYs, DELETE is typically not allowed, but we'll support it"""
        if index is None:
            # DELETE - delete all elements
            self.data.clear()
        elif end_index is None:
            # DELETE(i) - delete single element at index i
            if 1 <= index <= len(self.data):
                self.data[index - 1] = None  # Mark as deleted but keep position
        else:
            # DELETE(i, j) - delete range of elements
            for i in range(index, min(end_index + 1, len(self.data) + 1)):
                if 1 <= i <= len(self.data):
                    self.data[i - 1] = None


class ExecutionContext:
    """Manages variables and execution state"""

    def __init__(self, parent: Optional['ExecutionContext'] = None):
        self.variables: Dict[str, Any] = {}
        self.cursors: Dict[str, Cursor] = {}
        self.record_types: Dict[str, RecordType] = {}  # User-defined RECORD types
        self.collection_types: Dict[str, CollectionTypeDeclaration] = {}  # User-defined collection types
        self.parent = parent
        self.output_buffer: List[str] = []
        self.exit_loop = False
        self.exception_raised = None
        # Bulk operation tracking
        self.bulk_rowcount: Dict[int, int] = {}  # Track rows affected per FORALL iteration
        self.bulk_exceptions: List[Dict[str, Any]] = []  # Track exceptions in FORALL SAVE EXCEPTIONS

    def get_variable(self, name: str) -> Any:
        """Get variable value (check current scope then parent)"""
        name_upper = name.upper()
        if name_upper in self.variables:
            return self.variables[name_upper]
        if self.parent:
            return self.parent.get_variable(name)
        raise NameError(f"Variable '{name}' not found")

    def set_variable(self, name: str, value: Any):
        """Set variable value in the scope where it was declared"""
        name_upper = name.upper()

        # If variable exists in current scope, update it here
        if name_upper in self.variables:
            self.variables[name_upper] = value
            return

        # If variable exists in parent scope, update it there
        if self.parent and self.parent.has_variable(name):
            self.parent.set_variable(name, value)
            return

        # Otherwise, create it in current scope
        self.variables[name_upper] = value

    def has_variable(self, name: str) -> bool:
        """Check if variable exists"""
        name_upper = name.upper()
        if name_upper in self.variables:
            return True
        if self.parent:
            return self.parent.has_variable(name)
        return False

    def add_output(self, text: str):
        """Add text to output buffer"""
        self.output_buffer.append(text)

    def get_output(self) -> List[str]:
        """Get all output"""
        return self.output_buffer

    def declare_cursor(self, name: str, query: str):
        """Declare a cursor"""
        name_upper = name.upper()
        self.cursors[name_upper] = Cursor(query)

    def get_cursor(self, name: str) -> Cursor:
        """Get cursor by name"""
        name_upper = name.upper()
        if name_upper in self.cursors:
            return self.cursors[name_upper]
        if self.parent:
            return self.parent.get_cursor(name)
        raise NameError(f"Cursor '{name}' not found")


class PLSQLExecutor:
    """
    Executor for PL/SQL AST
    Interprets and runs parsed PL/SQL code
    """

    def __init__(self, rdbms_engine=None):
        """
        Initialize executor

        Args:
            rdbms_engine: RDBMSEngine instance for SQL execution
        """
        self.rdbms_engine = rdbms_engine
        self.global_context = ExecutionContext()
        self.procedures: Dict[str, ProcedureDefinition] = {}
        self.functions: Dict[str, FunctionDefinition] = {}
        self.packages: Dict[str, Dict] = {}  # Package storage
        # Each package: {'spec': PackageSpecification, 'body': PackageBody, 'state': {}}
        self.return_value = None  # For function returns

    def execute(self, ast) -> Dict[str, Any]:
        """
        Execute PL/SQL block, procedure definition, or function definition

        Args:
            ast: PLSQLBlock, ProcedureDefinition, or FunctionDefinition AST node

        Returns:
            Dict with status, output, and any results
        """
        try:
            # Handle package specifications
            if isinstance(ast, PackageSpecification):
                self._execute_package_specification(ast)
                return {
                    'status': 'success',
                    'message': f"Package {ast.package_name} specification created",
                    'output': []
                }

            # Handle package bodies
            elif isinstance(ast, PackageBody):
                self._execute_package_body(ast)
                return {
                    'status': 'success',
                    'message': f"Package {ast.package_name} body created",
                    'output': []
                }

            # Handle procedure and function definitions
            elif isinstance(ast, ProcedureDefinition):
                self._execute_procedure_definition(ast)
                return {
                    'status': 'success',
                    'message': f"Procedure {ast.proc_name} created successfully",
                    'output': []
                }
            elif isinstance(ast, FunctionDefinition):
                self._execute_function_definition(ast)
                return {
                    'status': 'success',
                    'message': f"Function {ast.func_name} created successfully",
                    'output': []
                }

            # Handle regular PL/SQL block
            context = ExecutionContext(self.global_context)
            self._execute_block(ast, context)

            return {
                'status': 'success',
                'output': context.get_output(),
                'variables': context.variables
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'error_type': type(e).__name__
            }

    def _execute_block(self, block: PLSQLBlock, context: ExecutionContext):
        """Execute a PL/SQL block"""
        # Process declarations
        for decl in block.declarations:
            self._execute_declaration(decl, context)

        # Execute statements
        try:
            for stmt in block.statements:
                self._execute_statement(stmt, context)
        except Exception as e:
            # Handle exceptions
            if block.exception_handlers:
                handled = self._handle_exception(e, block.exception_handlers, context)
                if not handled:
                    raise
            else:
                raise

    def _execute_declaration(self, decl, context: ExecutionContext):
        """Execute variable or cursor declaration"""
        if isinstance(decl, CursorDeclaration):
            # Cursor declaration
            context.declare_cursor(decl.cursor_name, decl.query)

        elif isinstance(decl, RecordTypeDeclaration):
            # TYPE ... IS RECORD declaration
            fields = {}
            for field in decl.fields:
                fields[field.field_name.upper()] = field.field_type
            record_type = RecordType(decl.type_name, fields)
            context.record_types[decl.type_name.upper()] = record_type

        elif isinstance(decl, CollectionTypeDeclaration):
            # TYPE ... IS TABLE OF / VARRAY declaration
            context.collection_types[decl.type_name.upper()] = decl

        elif isinstance(decl, TypeAttributeDeclaration):
            # %TYPE or %ROWTYPE declaration
            if decl.attribute_type == 'ROWTYPE':
                # Get table schema from RDBMS
                table_name = decl.source_name
                # Create a record type based on table schema
                if self.rdbms_engine:
                    # Get table columns
                    result = self.rdbms_engine.execute(f"PRAGMA table_info({table_name})")
                    if result['status'] == 'success':
                        fields = {}
                        for row in result.get('rows', []):
                            col_name = row[1]  # column name
                            col_type = row[2]  # column type
                            fields[col_name.upper()] = col_type.upper()

                        # Create a RecordInstance with these fields
                        record_type = RecordType(f"{table_name}_ROWTYPE", fields)
                        record_instance = RecordInstance(record_type)
                        context.set_variable(decl.var_name, record_instance)
                    else:
                        # Table not found, create empty record
                        context.set_variable(decl.var_name, None)
                else:
                    # No RDBMS, create empty record
                    context.set_variable(decl.var_name, None)

            elif decl.attribute_type == 'TYPE':
                # %TYPE - copy type from another variable or column
                # For now, just initialize to None
                context.set_variable(decl.var_name, None)

        else:
            # Regular variable declaration
            initial_value = None

            # Check if this is a RECORD type variable
            if hasattr(decl, 'var_type'):
                var_type_upper = decl.var_type.upper()

                # Check if it's a user-defined RECORD type
                if var_type_upper in context.record_types:
                    record_type = context.record_types[var_type_upper]
                    initial_value = RecordInstance(record_type)

                # Check if it's a user-defined collection type
                elif var_type_upper in context.collection_types:
                    coll_decl = context.collection_types[var_type_upper]
                    if coll_decl.collection_type == 'ASSOC_ARRAY':
                        initial_value = AssociativeArray(coll_decl.element_type, coll_decl.index_type)
                    elif coll_decl.collection_type == 'NESTED_TABLE':
                        initial_value = NestedTable(coll_decl.element_type)
                    elif coll_decl.collection_type == 'VARRAY':
                        initial_value = VArray(coll_decl.element_type, coll_decl.max_size)

                # Check for initial value from declaration
                elif decl.initial_value:
                    initial_value = self._evaluate_expression(decl.initial_value, context)
                else:
                    # Default initial values for primitive types
                    if var_type_upper in ('NUMBER', 'INTEGER', 'INT'):
                        initial_value = 0
                    elif var_type_upper in ('VARCHAR2', 'VARCHAR', 'CHAR', 'STRING'):
                        initial_value = ''
                    elif var_type_upper == 'BOOLEAN':
                        initial_value = False
                    elif var_type_upper == 'DATE':
                        initial_value = None

                context.set_variable(decl.var_name, initial_value)

    def _execute_statement(self, stmt: Any, context: ExecutionContext):
        """Execute a single statement"""
        if stmt is None:
            return

        stmt_type = stmt.node_type

        if stmt_type == 'assignment':
            self._execute_assignment(stmt, context)
        elif stmt_type == 'record_assignment':
            self._execute_record_assignment(stmt, context)
        elif stmt_type == 'if_statement':
            self._execute_if_statement(stmt, context)
        elif stmt_type == 'loop_statement':
            self._execute_loop_statement(stmt, context)
        elif stmt_type == 'exit_statement':
            self._execute_exit_statement(stmt, context)
        elif stmt_type == 'output_statement':
            self._execute_output_statement(stmt, context)
        elif stmt_type == 'sql_statement':
            self._execute_sql_statement(stmt, context)
        elif stmt_type == 'plsql_block':
            # Nested BEGIN...END block
            self._execute_block(stmt, context)
        elif stmt_type == 'cursor_statement':
            self._execute_cursor_statement(stmt, context)
        elif stmt_type == 'cursor_for_loop':
            self._execute_cursor_for_loop(stmt, context)
        elif stmt_type == 'call_statement':
            self._execute_call_statement(stmt, context)
        elif stmt_type == 'return_statement':
            self._execute_return_statement(stmt, context)
        elif stmt_type == 'procedure_definition':
            self._execute_procedure_definition(stmt)
        elif stmt_type == 'function_definition':
            self._execute_function_definition(stmt)
        elif stmt_type == 'execute_immediate':
            self._execute_execute_immediate(stmt, context)
        elif stmt_type == 'pragma':
            self._execute_pragma(stmt, context)
        elif stmt_type == 'pipe_row':
            self._execute_pipe_row(stmt, context)
        elif stmt_type == 'forall':
            self._execute_forall(stmt, context)
        elif stmt_type == 'bulk_collect':
            self._execute_bulk_collect(stmt, context)
        else:
            raise NotImplementedError(f"Statement type '{stmt_type}' not implemented")

    def _execute_assignment(self, stmt: Assignment, context: ExecutionContext):
        """Execute variable assignment or collection element assignment"""
        value = self._evaluate_expression(stmt.expression, context)

        # Check if this is collection element assignment: collection(index) := value
        if '(' in stmt.var_name and ')' in stmt.var_name:
            # Parse collection_name(index)
            match = re.match(r'(\w+)\((.*)\)', stmt.var_name)
            if match:
                collection_name = match.group(1)
                index_expr = match.group(2)

                # Get the collection
                collection = context.get_variable(collection_name)

                # Evaluate the index
                index = self._evaluate_expression(index_expr, context)

                # Set the element
                if isinstance(collection, (AssociativeArray, NestedTable, VArray)):
                    collection.set(index, value)
                else:
                    raise TypeError(f"{collection_name} is not a collection type")
                return

        # Regular variable assignment
        context.set_variable(stmt.var_name, value)

    def _execute_record_assignment(self, stmt: RecordAssignment, context: ExecutionContext):
        """Execute record.field := value"""
        record = context.get_variable(stmt.record_name)
        if not isinstance(record, RecordInstance):
            raise TypeError(f"{stmt.record_name} is not a RECORD type")

        value = self._evaluate_expression(stmt.expression, context)
        record.set_field(stmt.field_name, value)

    def _execute_if_statement(self, stmt: IfStatement, context: ExecutionContext):
        """Execute IF statement"""
        condition_result = self._evaluate_condition(stmt.condition, context)

        if condition_result:
            # Execute THEN statements
            for s in stmt.then_statements:
                self._execute_statement(s, context)
        else:
            # Check ELSIF clauses
            executed = False
            for elsif_condition, elsif_statements in stmt.elsif_clauses:
                if self._evaluate_condition(elsif_condition, context):
                    for s in elsif_statements:
                        self._execute_statement(s, context)
                    executed = True
                    break

            # Execute ELSE if no ELSIF matched
            if not executed and stmt.else_statements:
                for s in stmt.else_statements:
                    self._execute_statement(s, context)

    def _execute_loop_statement(self, stmt: LoopStatement, context: ExecutionContext):
        """Execute LOOP statement"""
        context.exit_loop = False

        if stmt.loop_type == 'basic':
            # Basic LOOP...END LOOP
            while not context.exit_loop:
                for s in stmt.statements:
                    self._execute_statement(s, context)
                    if context.exit_loop:
                        break

        elif stmt.loop_type == 'while':
            # WHILE condition LOOP
            while not context.exit_loop and self._evaluate_condition(stmt.condition, context):
                for s in stmt.statements:
                    self._execute_statement(s, context)
                    if context.exit_loop:
                        break

        elif stmt.loop_type == 'for':
            # FOR i IN start..end LOOP
            start_val = self._evaluate_expression(stmt.range_start, context)
            end_val = self._evaluate_expression(stmt.range_end, context)

            # Create loop context with iterator variable
            loop_context = ExecutionContext(context)

            for i in range(int(start_val), int(end_val) + 1):
                loop_context.set_variable(stmt.iterator, i)

                for s in stmt.statements:
                    self._execute_statement(s, loop_context)
                    if loop_context.exit_loop:
                        break

                if loop_context.exit_loop:
                    break

            # Copy output from loop context
            context.output_buffer.extend(loop_context.output_buffer)

        context.exit_loop = False

    def _execute_exit_statement(self, stmt: ExitStatement, context: ExecutionContext):
        """Execute EXIT statement"""
        if stmt.condition:
            if self._evaluate_condition(stmt.condition, context):
                context.exit_loop = True
        else:
            context.exit_loop = True

    def _execute_output_statement(self, stmt: OutputStatement, context: ExecutionContext):
        """Execute DBMS_OUTPUT.PUT_LINE"""
        output = self._evaluate_expression(stmt.expression, context)
        context.add_output(str(output))

    def _execute_sql_statement(self, stmt: SQLStatement, context: ExecutionContext):
        """Execute SQL statement"""
        if not self.rdbms_engine:
            raise RuntimeError("No RDBMS engine available for SQL execution")

        if stmt.sql_type == 'select_into':
            # SELECT ... INTO variables
            result = self.rdbms_engine.execute(stmt.sql_text)

            if result['status'] == 'success' and result['rows']:
                if len(result['rows']) > 1:
                    raise RuntimeError("TOO_MANY_ROWS: SELECT INTO returned more than one row")

                row = result['rows'][0]
                values = list(row.values())

                if len(stmt.into_variables) != len(values):
                    raise RuntimeError(f"INTO variable count mismatch: expected {len(stmt.into_variables)}, got {len(values)}")

                for var_name, value in zip(stmt.into_variables, values):
                    context.set_variable(var_name, value)
            elif not result['rows']:
                raise RuntimeError("NO_DATA_FOUND: SELECT INTO returned no rows")
            else:
                raise RuntimeError(f"SQL error: {result.get('error', 'Unknown error')}")

        else:
            # INSERT, UPDATE, DELETE
            result = self.rdbms_engine.execute(stmt.sql_text)
            if result['status'] != 'success':
                raise RuntimeError(f"SQL error: {result.get('error', 'Unknown error')}")

    def _handle_exception(self, exception: Exception, handlers: List[ExceptionHandler],
                         context: ExecutionContext) -> bool:
        """Handle exception with exception handlers"""
        exc_name = type(exception).__name__
        exc_message = str(exception)

        # Map Python exceptions to PL/SQL exception names
        if 'NO_DATA_FOUND' in exc_message:
            plsql_exc = 'NO_DATA_FOUND'
        elif 'TOO_MANY_ROWS' in exc_message:
            plsql_exc = 'TOO_MANY_ROWS'
        else:
            plsql_exc = 'OTHERS'

        # Find matching handler
        for handler in handlers:
            if handler.exception_name.upper() == plsql_exc or handler.exception_name.upper() == 'OTHERS':
                # Execute handler statements
                for stmt in handler.statements:
                    self._execute_statement(stmt, context)
                return True

        return False

    def _evaluate_expression(self, expr: str, context: ExecutionContext) -> Any:
        """
        Evaluate expression

        Supports:
        - Literals: 123, 'string', TRUE, FALSE
        - Variables: v_count
        - Arithmetic: +, -, *, /
        - String concatenation: ||
        - Functions: UPPER(), LOWER(), etc.
        """
        expr = expr.strip()

        # Fix SQL%BULK_ attributes that get tokenized as "SQL BULK_"
        # The tokenizer removes % so we need to reconstruct it
        expr = re.sub(r'\bSQL\s+BULK_', 'SQL%BULK_', expr, flags=re.IGNORECASE)

        # NULL literal
        if expr.upper() == 'NULL':
            return None

        # Boolean literals
        if expr.upper() == 'TRUE':
            return True
        if expr.upper() == 'FALSE':
            return False

        # String concatenation (||) - check BEFORE string literal detection
        if '||' in expr:
            parts = expr.split('||')
            result = ''
            for part in parts:
                part_value = self._evaluate_expression(part.strip(), context)
                # Convert None to empty string for Oracle compatibility
                if part_value is None:
                    part_value = ''
                result += str(part_value)
            return result

        # String literal
        if expr.startswith("'") and expr.endswith("'"):
            # Strip outer quotes and handle escaped quotes ''  → '
            string_content = expr[1:-1]
            # Replace doubled quotes with single quotes (PL/SQL escape sequence)
            string_content = string_content.replace("''", "'")
            return string_content

        # Parenthesized expressions - handle first
        # Strip expression to handle spaces: "( 10 + 20 )" -> "(10 + 20)"
        expr_stripped = expr.strip()
        if expr_stripped.startswith("(") and expr_stripped.endswith(")"):
            # Check if parentheses are balanced and matched
            depth = 0
            for i, char in enumerate(expr_stripped):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                # If depth reaches 0 before the end, these aren't wrapping parens
                if depth == 0 and i < len(expr_stripped) - 1:
                    break
            # If we made it to the end with depth 0, these are wrapping parentheses
            if depth == 0 and i == len(expr_stripped) - 1:
                # Evaluate the inner expression
                return self._evaluate_expression(expr_stripped[1:-1], context)

        # Number literal (check early to avoid confusion with operators)
        try:
            if '.' in expr:
                return float(expr)
            else:
                return int(expr)
        except ValueError:
            pass

        # Arithmetic operators (check BEFORE function calls to handle expressions like func() + 5)
        # We need to split respecting parentheses - only split on operators outside parens
        for op in ['+', '-', '*', '/']:
            if op in expr:
                # Find the operator position outside of parentheses
                paren_depth = 0
                split_pos = -1
                for i, char in enumerate(expr):
                    if char == '(':
                        paren_depth += 1
                    elif char == ')':
                        paren_depth -= 1
                    elif char == op and paren_depth == 0:
                        # Found operator outside parentheses
                        split_pos = i
                        break

                if split_pos > 0:
                    # Split at this position
                    left = self._evaluate_expression(expr[:split_pos].strip(), context)
                    right = self._evaluate_expression(expr[split_pos+1:].strip(), context)

                    if op == '+':
                        return left + right
                    elif op == '-':
                        return left - right
                    elif op == '*':
                        return left * right
                    elif op == '/':
                        return left / right

        # Collection element access: collection(index) - check BEFORE function calls
        # Match pattern: word(anything) where word is a variable name
        coll_access_match = re.match(r'(\w+)\s*\((.*)\)$', expr.strip())
        if coll_access_match:
            coll_name = coll_access_match.group(1)
            index_expr = coll_access_match.group(2).strip()

            # Check if it's a collection variable (not a function)
            if context.has_variable(coll_name):
                var_value = context.get_variable(coll_name)
                if isinstance(var_value, (AssociativeArray, NestedTable, VArray)):
                    # It's a collection - evaluate index expression (which may contain dots like v_data.FIRST)
                    index = self._evaluate_expression(index_expr, context)
                    return var_value.get(index)

        # SQL% attributes - handle before function calls
        if expr.upper().startswith('SQL%'):
            return self._evaluate_sql_attribute(expr, context)

        # Collection method calls: collection.METHOD(args)
        if '.' in expr and '(' in expr and ')' in expr:
            # Try to parse as collection.method(args)
            method_match = re.match(r'(\w+)\s*\.\s*(\w+)\s*\((.*)\)', expr.strip(), re.IGNORECASE)
            if method_match:
                var_name = method_match.group(1)
                method_name = method_match.group(2).upper()
                args_str = method_match.group(3).strip()

                if context.has_variable(var_name):
                    var_value = context.get_variable(var_name)

                    if isinstance(var_value, (AssociativeArray, NestedTable, VArray)):
                        # Collection method with argument
                        if method_name == 'EXISTS':
                            index = int(self._evaluate_expression(args_str, context))
                            return var_value.exists(index)
                        elif method_name == 'NEXT':
                            index = int(self._evaluate_expression(args_str, context))
                            # NEXT returns the next index after the given index
                            return var_value.next(index) if hasattr(var_value, 'next') else None
                        elif method_name == 'PRIOR':
                            index = int(self._evaluate_expression(args_str, context))
                            # PRIOR returns the previous index before the given index
                            return var_value.prior(index) if hasattr(var_value, 'prior') else None

        # Function call
        if '(' in expr and ')' in expr:
            # Support both simple (FUNC) and qualified (PKG.FUNC) names
            # Remove spaces around dots and parentheses for matching
            expr_normalized = expr.replace(' . ', '.').replace(' (', '(').replace('( ', '(').replace(' )', ')')
            func_match = re.match(r'([\w.]+)\s*\((.*)\)', expr_normalized, re.IGNORECASE)
            if func_match:
                func_name = func_match.group(1).upper()
                func_args_str = func_match.group(2).strip()

                # Parse arguments (simple comma split)
                if func_args_str:
                    # Split by comma (this is simplified - doesn't handle nested function calls properly)
                    func_args = [arg.strip() for arg in func_args_str.split(',')]
                else:
                    func_args = []

                # Check if it's a user-defined function
                # Try exact match first, then let _call_function handle package search
                if func_name in self.functions or '.' in func_name:
                    return self._call_function(func_name, func_args, context)

                # Built-in functions (with single argument)
                if func_args:
                    arg_value = self._evaluate_expression(func_args[0], context)
                else:
                    arg_value = None

                if func_name == 'UPPER':
                    return str(arg_value).upper()
                elif func_name == 'LOWER':
                    return str(arg_value).lower()
                elif func_name == 'LENGTH':
                    return len(str(arg_value))
                elif func_name == 'TRIM':
                    return str(arg_value).strip()
                elif func_name == 'CHR':
                    # CHR(n) - convert ASCII code to character
                    return chr(int(arg_value))

        # Record field access: record.field
        if '.' in expr and '(' not in expr:
            # Could be record.field or collection.method
            parts = expr.split('.', 1)
            if len(parts) == 2:
                var_name = parts[0].strip()
                field_or_method = parts[1].strip().upper()

                if context.has_variable(var_name):
                    var_value = context.get_variable(var_name)

                    # Check if it's a record instance
                    if isinstance(var_value, RecordInstance):
                        return var_value.get_field(field_or_method)

                    # Check if it's a collection method (COUNT, EXISTS, etc.)
                    elif isinstance(var_value, (AssociativeArray, NestedTable, VArray)):
                        # Collection methods without arguments
                        if field_or_method == 'COUNT':
                            return var_value.count()
                        elif field_or_method == 'FIRST':
                            return var_value.first()
                        elif field_or_method == 'LAST':
                            return var_value.last()
                        elif field_or_method == 'LIMIT' and isinstance(var_value, VArray):
                            return var_value.limit()

        # Variable reference
        if context.has_variable(expr):
            return context.get_variable(expr)

        # If nothing else matches, return as-is
        return expr

    def _evaluate_condition(self, condition: str, context: ExecutionContext) -> bool:
        """
        Evaluate boolean condition

        Supports:
        - Comparisons: =, <>, !=, <, >, <=, >=
        - Logical: AND, OR, NOT
        """
        condition = condition.strip()

        # Logical operators (simple implementation)
        if ' AND ' in condition.upper():
            parts = re.split(r'\s+AND\s+', condition, flags=re.IGNORECASE)
            return all(self._evaluate_condition(p, context) for p in parts)

        if ' OR ' in condition.upper():
            parts = re.split(r'\s+OR\s+', condition, flags=re.IGNORECASE)
            return any(self._evaluate_condition(p, context) for p in parts)

        if condition.upper().startswith('NOT '):
            return not self._evaluate_condition(condition[4:], context)

        # Comparison operators
        for op in ['<=', '>=', '<>', '!=', '=', '<', '>']:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2:
                    left = self._evaluate_expression(parts[0].strip(), context)
                    right = self._evaluate_expression(parts[1].strip(), context)

                    if op == '=':
                        return left == right
                    elif op in ('<>', '!='):
                        return left != right
                    elif op == '<':
                        return left < right
                    elif op == '>':
                        return left > right
                    elif op == '<=':
                        return left <= right
                    elif op == '>=':
                        return left >= right

        # If no operator, evaluate as expression and check truthiness
        value = self._evaluate_expression(condition, context)
        return bool(value)

    def _execute_cursor_statement(self, stmt: CursorStatement, context: ExecutionContext):
        """Execute OPEN, FETCH, or CLOSE cursor"""
        cursor = context.get_cursor(stmt.cursor_name)

        if stmt.operation == 'open':
            cursor.open(self.rdbms_engine)
        elif stmt.operation == 'fetch':
            row = cursor.fetch()
            if row:
                # Store row values into variables
                values = list(row.values())
                if len(stmt.into_variables) != len(values):
                    raise RuntimeError(f"FETCH variable count mismatch: expected {len(stmt.into_variables)}, got {len(values)}")
                for var_name, value in zip(stmt.into_variables, values):
                    context.set_variable(var_name, value)
            # If no row, variables keep their values (Oracle behavior)
        elif stmt.operation == 'close':
            cursor.close()

    def _execute_cursor_for_loop(self, stmt: CursorForLoop, context: ExecutionContext):
        """Execute cursor FOR loop"""
        # Get or create cursor
        if stmt.cursor_query:
            # Inline query: FOR rec IN (SELECT ...)
            cursor = Cursor(stmt.cursor_query)
            cursor.open(self.rdbms_engine)
        else:
            # Named cursor: FOR rec IN cursor_name
            cursor = context.get_cursor(stmt.cursor_name)
            was_open = cursor.is_open
            if not was_open:
                cursor.open(self.rdbms_engine)

        # Create loop context
        loop_context = ExecutionContext(context)

        try:
            # Fetch and process each row
            while True:
                row = cursor.fetch()
                if not row:
                    break

                # Set record as variables in loop context (rec.column_name becomes REC variable with value)
                # For simplicity, we'll make each column available as a variable
                for col_name, col_value in row.items():
                    loop_context.set_variable(f"{stmt.record_name}.{col_name}", col_value)
                    # Also set as plain variables for easier access
                    loop_context.set_variable(col_name, col_value)

                # Execute loop statements
                for s in stmt.statements:
                    self._execute_statement(s, loop_context)
                    if loop_context.exit_loop:
                        break

                if loop_context.exit_loop:
                    break

            # Copy output from loop context
            context.output_buffer.extend(loop_context.output_buffer)

        finally:
            # Close cursor if we opened it (inline queries or if it wasn't already open)
            if stmt.cursor_query or not was_open:
                if cursor.is_open:
                    cursor.close()

    def _execute_procedure_definition(self, proc_def: ProcedureDefinition):
        """Store procedure definition"""
        proc_name_upper = proc_def.proc_name.upper()
        self.procedures[proc_name_upper] = proc_def

    def _execute_function_definition(self, func_def: FunctionDefinition):
        """Store function definition"""
        func_name_upper = func_def.func_name.upper()
        self.functions[func_name_upper] = func_def

    def _execute_call_statement(self, stmt: CallStatement, context: ExecutionContext):
        """Execute procedure call (supports package.procedure syntax)"""
        proc_name_upper = stmt.proc_name.upper()

        # Check for qualified name (package.procedure)
        if '.' in proc_name_upper:
            # Already qualified
            qualified_name = proc_name_upper
        else:
            # Try unqualified first
            qualified_name = proc_name_upper

            # If not found, search in packages
            if qualified_name not in self.procedures:
                # Search all packages for this procedure
                for pkg_name, pkg_data in self.packages.items():
                    test_name = f"{pkg_name}.{proc_name_upper}"
                    if test_name in self.procedures:
                        qualified_name = test_name
                        break

        if qualified_name not in self.procedures:
            raise NameError(f"Procedure '{stmt.proc_name}' not found")

        proc_def = self.procedures[qualified_name]

        # Create new context for procedure execution
        proc_context = ExecutionContext(self.global_context)

        # Bind parameters
        self._bind_parameters(proc_def.parameters, stmt.arguments, context, proc_context)

        # Execute procedure declarations and statements
        for decl in proc_def.declarations:
            self._execute_declaration(decl, proc_context)

        try:
            for s in proc_def.statements:
                self._execute_statement(s, proc_context)
        except Exception as e:
            # Handle exceptions
            if proc_def.exception_handlers:
                handled = self._handle_exception(e, proc_def.exception_handlers, proc_context)
                if not handled:
                    raise
            else:
                raise

        # Copy output to calling context
        context.output_buffer.extend(proc_context.output_buffer)

        # Handle OUT and IN OUT parameters - update values in calling context
        for i, param in enumerate(proc_def.parameters):
            if param.param_mode in ('OUT', 'IN OUT'):
                if i < len(stmt.arguments):
                    # Get the argument name (variable name in calling context)
                    arg_expr = stmt.arguments[i].strip()
                    # Get the value from procedure context
                    param_value = proc_context.get_variable(param.param_name)
                    # Set in calling context
                    context.set_variable(arg_expr, param_value)

    def _execute_return_statement(self, stmt: ReturnStatement, context: ExecutionContext):
        """Execute RETURN statement (for functions)"""
        self.return_value = self._evaluate_expression(stmt.expression, context)
        # Raise special exception to exit function immediately
        raise FunctionReturnException(self.return_value)

    def _execute_execute_immediate(self, stmt: ExecuteImmediateStatement, context: ExecutionContext):
        """Execute EXECUTE IMMEDIATE dynamic SQL"""
        # Evaluate the SQL expression to get the actual SQL string
        sql_string = self._evaluate_expression(stmt.sql_expression, context)

        # Translate Oracle types to SQLite types for DDL statements
        if 'CREATE TABLE' in sql_string.upper() or 'ALTER TABLE' in sql_string.upper():
            # Map Oracle types to SQLite types
            type_mapping = {
                'NUMBER': 'REAL',
                'VARCHAR2': 'TEXT',
                'CLOB': 'TEXT',
                'BLOB': 'BLOB',
                'DATE': 'TEXT',
                'TIMESTAMP': 'TEXT',
                'BOOLEAN': 'INTEGER'
            }
            for oracle_type, sqlite_type in type_mapping.items():
                # Replace type names (with word boundaries)
                import re
                sql_string = re.sub(r'\b' + oracle_type + r'\b', sqlite_type, sql_string, flags=re.IGNORECASE)

        # Bind USING variables (replace placeholders)
        if stmt.using_variables:
            for i, var_name in enumerate(stmt.using_variables):
                var_value = context.get_variable(var_name)
                # Simple placeholder replacement (supports :1, :2, etc. or named :var)
                sql_string = sql_string.replace(f':{i+1}', str(var_value))
                sql_string = sql_string.replace(f':{var_name}', str(var_value))

        # Execute the dynamic SQL
        if self.rdbms_engine:
            result = self.rdbms_engine.execute(sql_string)

            # Check for errors
            if result['status'] == 'error':
                raise RuntimeError(f"EXECUTE IMMEDIATE error: {result.get('error', 'Unknown error')}")

            # Handle INTO clause (for SELECT)
            if stmt.into_variables and result['status'] == 'success':
                rows = result.get('rows', [])
                if rows:
                    row = rows[0]
                    # Row is a dictionary, get values in order
                    row_values = list(row.values()) if isinstance(row, dict) else row
                    for i, var_name in enumerate(stmt.into_variables):
                        if i < len(row_values):
                            context.set_variable(var_name, row_values[i])

            # Handle RETURNING clause (for DML)
            if stmt.returning_variables and result['status'] == 'success':
                returning_data = result.get('returning', [])
                if returning_data:
                    for i, var_name in enumerate(stmt.returning_variables):
                        if i < len(returning_data):
                            context.set_variable(var_name, returning_data[i])

    def _execute_pragma(self, stmt: PragmaStatement, context: ExecutionContext):
        """Execute PRAGMA statement"""
        if stmt.pragma_type == 'AUTONOMOUS_TRANSACTION':
            # Mark this execution context as autonomous
            # In a real implementation, this would start a new transaction
            context.is_autonomous = True
            # Store current transaction state if needed
            if hasattr(context, 'parent_transaction'):
                context.parent_transaction = self.current_transaction if hasattr(self, 'current_transaction') else None

    def _execute_pipe_row(self, stmt: PipelineStatement, context: ExecutionContext):
        """Execute PIPE ROW statement (for pipelined functions)"""
        # Evaluate the row expression
        row_value = self._evaluate_expression(stmt.row_expression, context)

        # Add to pipelined results
        if not hasattr(context, 'piped_rows'):
            context.piped_rows = []
        context.piped_rows.append(row_value)

    def _execute_forall(self, stmt: ForallStatement, context: ExecutionContext):
        """Execute FORALL bulk DML statement"""
        # Evaluate bounds
        lower = int(self._evaluate_expression(stmt.lower_bound, context))
        upper = int(self._evaluate_expression(stmt.upper_bound, context))

        # Clear bulk tracking
        context.bulk_rowcount = {}
        context.bulk_exceptions = []

        # Execute DML for each index value
        for index_value in range(lower, upper + 1):
            # Set index variable
            context.set_variable(stmt.index_name, index_value)

            try:
                # Execute the DML statement
                self._execute_statement(stmt.dml_statement, context)

                # Track row count (default to 1 if not tracked)
                context.bulk_rowcount[index_value] = 1

            except Exception as e:
                if stmt.save_exceptions:
                    # Save exception and continue
                    context.bulk_exceptions.append({
                        'error_index': index_value,
                        'error_code': -1,
                        'error_msg': str(e)
                    })
                    context.bulk_rowcount[index_value] = 0
                else:
                    # Re-raise the exception
                    raise

    def _evaluate_sql_attribute(self, expr: str, context: ExecutionContext):
        """Evaluate SQL% attributes like SQL%BULK_ROWCOUNT, SQL%BULK_EXCEPTIONS"""
        # Normalize expression by removing extra spaces
        expr_normalized = re.sub(r'\s+', ' ', expr.upper().strip())
        # Remove spaces around dots and parentheses
        expr_normalized = expr_normalized.replace(' . ', '.').replace(' (', '(').replace('( ', '(').replace(' )', ')')

        # SQL%BULK_ROWCOUNT(index) - returns row count for that index in FORALL
        if expr_normalized.startswith('SQL%BULK_ROWCOUNT'):
            # Parse: SQL%BULK_ROWCOUNT(index)
            match = re.match(r'SQL%BULK_ROWCOUNT\((.+)\)', expr_normalized, re.IGNORECASE)
            if match:
                index_expr = match.group(1)
                index = int(self._evaluate_expression(index_expr, context))
                return context.bulk_rowcount.get(index, 0)
            else:
                raise SyntaxError(f"Invalid SQL%BULK_ROWCOUNT syntax: {expr}")

        # SQL%BULK_EXCEPTIONS.COUNT - returns number of exceptions
        if 'SQL%BULK_EXCEPTIONS' in expr_normalized:
            if '.COUNT' in expr_normalized:
                return len(context.bulk_exceptions)
            elif match := re.match(r'SQL%BULK_EXCEPTIONS\((\d+)\)\.ERROR_INDEX', expr_normalized, re.IGNORECASE):
                idx = int(match.group(1))
                if 0 < idx <= len(context.bulk_exceptions):
                    return context.bulk_exceptions[idx - 1]['error_index']
                return None
            elif match := re.match(r'SQL%BULK_EXCEPTIONS\((\d+)\)\.ERROR_CODE', expr_normalized, re.IGNORECASE):
                idx = int(match.group(1))
                if 0 < idx <= len(context.bulk_exceptions):
                    return context.bulk_exceptions[idx - 1]['error_code']
                return None
            else:
                raise SyntaxError(f"Invalid SQL%BULK_EXCEPTIONS syntax: {expr}")

        # Unknown SQL% attribute
        raise RuntimeError(f"Unknown SQL attribute: {expr}")

    def _execute_bulk_collect(self, stmt, context: ExecutionContext):
        """Execute BULK COLLECT INTO statement"""
        from .parser import BulkCollectStatement

        # Get the collection variable
        collection_name = stmt.collection_name

        # Check if this is a cursor fetch or a SELECT query
        is_cursor_fetch = hasattr(stmt, 'is_cursor_fetch') and stmt.is_cursor_fetch

        if is_cursor_fetch:
            # FETCH cursor BULK COLLECT INTO collection
            cursor_name = stmt.cursor_name
            cursor = context.get_cursor(cursor_name)

            if cursor is None:
                raise RuntimeError(f"Cursor '{cursor_name}' not found")

            # Fetch rows
            rows = []
            # Evaluate LIMIT: can be int literal or variable name
            limit = None
            if stmt.limit is not None:
                if isinstance(stmt.limit, int):
                    limit = stmt.limit
                elif isinstance(stmt.limit, str):
                    # It's a variable name - evaluate it
                    limit = self._evaluate_expression(stmt.limit, context)
                    limit = int(limit) if limit is not None else None
            count = 0

            while True:
                row = cursor.fetch()
                if row is None:
                    break

                rows.append(row)
                count += 1

                if limit and count >= limit:
                    break

            # Store rows in collection
            # Get or create the collection
            try:
                collection = context.get_variable(collection_name)
            except:
                # Create a new nested table if it doesn't exist
                from .types import NestedTable
                collection = NestedTable()
                context.set_variable(collection_name, collection)

            # Clear existing collection and add new rows
            if hasattr(collection, 'clear'):
                collection.clear()

            # Add rows to collection
            for i, row in enumerate(rows, start=1):
                # If row is a dict (from cursor), extract value if single column
                if isinstance(row, dict):
                    # For single-column cursor, extract the value
                    if len(row) == 1:
                        collection.set(i, list(row.values())[0])
                    else:
                        # For multi-column, store the dict
                        collection.set(i, row)
                else:
                    collection.set(i, row)

        else:
            # SELECT ... BULK COLLECT INTO collection
            query = stmt.query

            # Execute the query
            if self.rdbms_engine:
                result = self.rdbms_engine.execute(query)

                if result['status'] == 'success':
                    rows = result.get('rows', [])

                    # Apply LIMIT if specified
                    # Evaluate LIMIT: can be int literal or variable name
                    if stmt.limit is not None:
                        limit = None
                        if isinstance(stmt.limit, int):
                            limit = stmt.limit
                        elif isinstance(stmt.limit, str):
                            # It's a variable name - evaluate it
                            limit = self._evaluate_expression(stmt.limit, context)
                            limit = int(limit) if limit is not None else None

                        if limit is not None:
                            rows = rows[:limit]

                    # Get or create the collection
                    try:
                        collection = context.get_variable(collection_name)
                    except:
                        # Create a new nested table if it doesn't exist
                        from .types import NestedTable
                        collection = NestedTable()
                        context.set_variable(collection_name, collection)

                    # Clear existing collection and add new rows
                    if hasattr(collection, 'clear'):
                        collection.clear()

                    # Add rows to collection
                    for i, row in enumerate(rows, start=1):
                        if isinstance(row, dict):
                            # For single-column selects, extract the value
                            if len(row) == 1:
                                collection.set(i, list(row.values())[0])
                            else:
                                # For multi-column, store the dict
                                collection.set(i, row)
                        else:
                            collection.set(i, row)
                else:
                    raise RuntimeError(f"Query failed: {result.get('error', 'Unknown error')}")
            else:
                raise RuntimeError("BULK COLLECT requires RDBMS engine")

    def _bind_parameters(self, parameters: List[Parameter], arguments: List[str],
                        calling_context: ExecutionContext, target_context: ExecutionContext):
        """Bind procedure/function parameters"""
        if len(arguments) > len(parameters):
            raise RuntimeError(f"Too many arguments: expected {len(parameters)}, got {len(arguments)}")

        for i, param in enumerate(parameters):
            if i < len(arguments):
                # Argument provided
                arg_value = self._evaluate_expression(arguments[i], calling_context)
                target_context.set_variable(param.param_name, arg_value)
            elif param.default_value is not None:
                # Use default value
                default_val = self._evaluate_expression(param.default_value, calling_context)
                target_context.set_variable(param.param_name, default_val)
            else:
                raise RuntimeError(f"Missing required parameter: {param.param_name}")

    def _call_function(self, func_name: str, arguments: List[str], context: ExecutionContext) -> Any:
        """Call a user-defined function and return its value (supports package.function syntax)"""
        func_name_upper = func_name.upper()

        # Check for qualified name (package.function)
        if '.' in func_name_upper:
            # Already qualified
            qualified_name = func_name_upper
        else:
            # Try unqualified first
            qualified_name = func_name_upper

            # If not found, search in packages
            if qualified_name not in self.functions:
                # Search all packages for this function
                for pkg_name, pkg_data in self.packages.items():
                    test_name = f"{pkg_name}.{func_name_upper}"
                    if test_name in self.functions:
                        qualified_name = test_name
                        break

        if qualified_name not in self.functions:
            raise NameError(f"Function '{func_name}' not found")

        func_def = self.functions[qualified_name]

        # Create new context for function execution
        func_context = ExecutionContext(self.global_context)

        # Bind parameters
        self._bind_parameters(func_def.parameters, arguments, context, func_context)

        # Execute function declarations and statements
        for decl in func_def.declarations:
            self._execute_declaration(decl, func_context)

        try:
            for s in func_def.statements:
                self._execute_statement(s, func_context)
        except FunctionReturnException as e:
            # Normal function return
            return e.return_value
        except Exception as e:
            # Handle exceptions
            if func_def.exception_handlers:
                handled = self._handle_exception(e, func_def.exception_handlers, func_context)
                if not handled:
                    raise
            else:
                raise

        # If no RETURN was executed, return None
        return None

    def _execute_package_specification(self, pkg_spec: PackageSpecification):
        """Store package specification"""
        pkg_name_upper = pkg_spec.package_name.upper()

        if pkg_name_upper not in self.packages:
            self.packages[pkg_name_upper] = {
                'spec': None,
                'body': None,
                'state': {}  # Package-level variables
            }

        self.packages[pkg_name_upper]['spec'] = pkg_spec

    def _execute_package_body(self, pkg_body: PackageBody):
        """Store package body and execute initialization"""
        pkg_name_upper = pkg_body.package_name.upper()

        if pkg_name_upper not in self.packages:
            raise RuntimeError(f"Package specification for '{pkg_body.package_name}' not found")

        self.packages[pkg_name_upper]['body'] = pkg_body

        # Store procedures and functions in package namespace
        for proc in pkg_body.procedures:
            self.procedures[f"{pkg_name_upper}.{proc.proc_name.upper()}"] = proc

        for func in pkg_body.functions:
            self.functions[f"{pkg_name_upper}.{func.func_name.upper()}"] = func

        # Execute initialization block if present
        if pkg_body.initialization:
            pkg_context = ExecutionContext(self.global_context)
            # Initialize package state variables
            for decl in pkg_body.declarations:
                self._execute_declaration(decl, pkg_context)

            # Execute initialization statements
            for stmt in pkg_body.initialization:
                self._execute_statement(stmt, pkg_context)

            # Store package state
            self.packages[pkg_name_upper]['state'] = pkg_context.variables


class FunctionReturnException(Exception):
    """Special exception to handle function RETURN"""
    def __init__(self, return_value):
        self.return_value = return_value
        super().__init__(f"Function returned: {return_value}")
