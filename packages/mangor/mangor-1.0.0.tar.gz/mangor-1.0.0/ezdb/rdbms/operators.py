"""
Query operators for EzDB RDBMS
Physical operators for query execution: Scan, Filter, Join, Aggregate, Sort, etc.
"""

from typing import Any, Dict, List, Optional, Tuple, Callable, Iterator
from .storage import TableStore
from .functions import call_function, AggregateFunctions
import numpy as np


class Operator:
    """Base class for query operators"""

    def execute(self) -> Iterator[Dict[str, Any]]:
        """Execute operator and yield rows"""
        raise NotImplementedError


class ScanOperator(Operator):
    """Table scan operator"""

    def __init__(self, table_store: TableStore):
        """
        Initialize scan operator.

        Args:
            table_store: Table to scan
        """
        self.table_store = table_store

    def execute(self) -> Iterator[Dict[str, Any]]:
        """Scan all rows in table"""
        for row_id, row in enumerate(self.table_store.rows):
            if row is not None:  # Skip deleted rows
                yield row.copy()


class FilterOperator(Operator):
    """Filter (WHERE clause) operator"""

    def __init__(self, input_op: Operator, predicate: Callable[[Dict], bool]):
        """
        Initialize filter operator.

        Args:
            input_op: Input operator
            predicate: Filter function (row -> bool)
        """
        self.input_op = input_op
        self.predicate = predicate

    def execute(self) -> Iterator[Dict[str, Any]]:
        """Filter rows based on predicate"""
        for row in self.input_op.execute():
            if self.predicate(row):
                yield row


class ProjectOperator(Operator):
    """Projection (SELECT columns) operator"""

    def __init__(self, input_op: Operator, columns: List[str]):
        """
        Initialize project operator.

        Args:
            input_op: Input operator
            columns: List of column names to project (or ['*'] for all)
        """
        self.input_op = input_op
        self.columns = columns

        # Cache parser and evaluator for function expression evaluation
        self._parser = None
        self._evaluator = None

    def _get_parser_and_evaluator(self):
        """Lazily import and cache parser and evaluator"""
        if self._parser is None:
            from .expression_parser import ExpressionParser
            from .expression_evaluator import ExpressionEvaluator
            self._parser = ExpressionParser()
            self._evaluator = ExpressionEvaluator()
        return self._parser, self._evaluator

    def execute(self) -> Iterator[Dict[str, Any]]:
        """Project specified columns"""
        for row in self.input_op.execute():
            if '*' in self.columns:
                yield row
            else:
                projected = {}
                for col in self.columns:
                    # Handle simple columns
                    if col in row:
                        projected[col] = row[col]
                    # Handle function expressions (e.g., UPPER(name), SUBSTR(name, 1, 3))
                    elif '(' in col:
                        try:
                            parser, evaluator = self._get_parser_and_evaluator()
                            from .expression_evaluator import EvaluationContext

                            # Parse and evaluate the expression
                            ast = parser.parse(col)
                            context = EvaluationContext(row=row)
                            projected[col] = evaluator.evaluate(ast, context)
                        except Exception:
                            # If expression evaluation fails, set to None
                            projected[col] = None
                    else:
                        # Column might be aliased/renamed
                        projected[col] = None
                yield projected


class SortOperator(Operator):
    """Sort (ORDER BY) operator"""

    def __init__(self, input_op: Operator, sort_keys: List[Tuple[str, str]]):
        """
        Initialize sort operator.

        Args:
            input_op: Input operator
            sort_keys: List of (column, direction) tuples
                      direction is 'ASC' or 'DESC'
        """
        self.input_op = input_op
        self.sort_keys = sort_keys

    def execute(self) -> Iterator[Dict[str, Any]]:
        """Sort rows by specified keys"""
        # Materialize all rows (sorting requires full data)
        rows = list(self.input_op.execute())

        # Sort by each key (in reverse order for proper precedence)
        for col, direction in reversed(self.sort_keys):
            reverse = (direction.upper() == 'DESC')

            def sort_key(row):
                value = row.get(col)
                # Handle None values
                if value is None:
                    return (1, 0) if not reverse else (0, 0)
                return (0, value)

            rows.sort(key=sort_key, reverse=reverse)

        # Yield sorted rows
        for row in rows:
            yield row


class LimitOperator(Operator):
    """Limit (LIMIT/OFFSET) operator"""

    def __init__(self, input_op: Operator, limit: Optional[int] = None, offset: int = 0):
        """
        Initialize limit operator.

        Args:
            input_op: Input operator
            limit: Maximum rows to return
            offset: Number of rows to skip
        """
        self.input_op = input_op
        self.limit = limit
        self.offset = offset

    def execute(self) -> Iterator[Dict[str, Any]]:
        """Apply limit and offset"""
        count = 0
        skipped = 0

        for row in self.input_op.execute():
            # Skip offset rows
            if skipped < self.offset:
                skipped += 1
                continue

            # Yield row
            yield row
            count += 1

            # Stop if limit reached
            if self.limit and count >= self.limit:
                break


class NestedLoopJoinOperator(Operator):
    """Nested loop join operator"""

    def __init__(self,
                 left_op: Operator,
                 right_op: Operator,
                 join_predicate: Callable[[Dict, Dict], bool],
                 join_type: str = 'INNER'):
        """
        Initialize nested loop join.

        Args:
            left_op: Left input operator
            right_op: Right input operator
            join_predicate: Join condition function (left_row, right_row -> bool)
            join_type: 'INNER', 'LEFT', 'RIGHT', or 'FULL'
        """
        self.left_op = left_op
        self.right_op = right_op
        self.join_predicate = join_predicate
        self.join_type = join_type.upper()

    def execute(self) -> Iterator[Dict[str, Any]]:
        """Execute nested loop join"""
        # Materialize right side (for repeated scans)
        right_rows = list(self.right_op.execute())

        for left_row in self.left_op.execute():
            matched = False

            for right_row in right_rows:
                if self.join_predicate(left_row, right_row):
                    # Merge rows
                    joined = {**left_row, **right_row}
                    yield joined
                    matched = True

            # Handle LEFT JOIN
            if not matched and self.join_type in ('LEFT', 'FULL'):
                # Pad with NULLs for right columns
                joined = left_row.copy()
                for key in (right_rows[0].keys() if right_rows else []):
                    if key not in joined:
                        joined[key] = None
                yield joined

        # Handle FULL JOIN (right unmatched)
        if self.join_type == 'FULL':
            left_rows = list(self.left_op.execute())
            for right_row in right_rows:
                matched = any(self.join_predicate(left_row, right_row) for left_row in left_rows)
                if not matched:
                    # Pad with NULLs for left columns
                    joined = right_row.copy()
                    for key in (left_rows[0].keys() if left_rows else []):
                        if key not in joined:
                            joined[key] = None
                    yield joined


class HashJoinOperator(Operator):
    """Hash join operator (more efficient for equality joins)"""

    def __init__(self,
                 left_op: Operator,
                 right_op: Operator,
                 left_key: str,
                 right_key: str,
                 join_type: str = 'INNER'):
        """
        Initialize hash join.

        Args:
            left_op: Left input operator
            right_op: Right input operator
            left_key: Join key column from left table
            right_key: Join key column from right table
            join_type: 'INNER', 'LEFT', etc.
        """
        self.left_op = left_op
        self.right_op = right_op
        self.left_key = left_key
        self.right_key = right_key
        self.join_type = join_type.upper()

    def execute(self) -> Iterator[Dict[str, Any]]:
        """Execute hash join"""
        # Build hash table from right side
        hash_table: Dict[Any, List[Dict]] = {}

        for right_row in self.right_op.execute():
            key_value = right_row.get(self.right_key)
            if key_value not in hash_table:
                hash_table[key_value] = []
            hash_table[key_value].append(right_row)

        # Probe with left side
        for left_row in self.left_op.execute():
            key_value = left_row.get(self.left_key)
            matched_rows = hash_table.get(key_value, [])

            if matched_rows:
                for right_row in matched_rows:
                    joined = {**left_row, **right_row}
                    yield joined
            elif self.join_type in ('LEFT', 'FULL'):
                # Unmatched left row
                joined = left_row.copy()
                # Pad with NULLs
                if hash_table:
                    sample_right = next(iter(hash_table.values()))[0]
                    for key in sample_right.keys():
                        if key not in joined:
                            joined[key] = None
                yield joined


class AggregateOperator(Operator):
    """Aggregate (GROUP BY) operator"""

    def __init__(self,
                 input_op: Operator,
                 group_by: Optional[List[str]] = None,
                 aggregates: Optional[Dict[str, Tuple[str, str]]] = None):
        """
        Initialize aggregate operator.

        Args:
            input_op: Input operator
            group_by: List of columns to group by (None = single group)
            aggregates: Dict of {output_col: (agg_func, input_col)}
                       e.g., {'total': ('sum', 'price'), 'count': ('count', '*')}
        """
        self.input_op = input_op
        self.group_by = group_by or []
        self.aggregates = aggregates or {}

    def execute(self) -> Iterator[Dict[str, Any]]:
        """Execute aggregation"""
        # Materialize input and build groups
        groups: Dict[Tuple, List[Dict]] = {}

        for row in self.input_op.execute():
            # Build group key
            if self.group_by:
                group_key = tuple(row.get(col) for col in self.group_by)
            else:
                group_key = ()  # Single group

            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(row)

        # Compute aggregates for each group
        for group_key, group_rows in groups.items():
            result = {}

            # Add group by columns
            for i, col in enumerate(self.group_by):
                result[col] = group_key[i]

            # Compute aggregates
            for output_col, (agg_func, input_col) in self.aggregates.items():
                if input_col == '*':
                    # COUNT(*)
                    values = [1] * len(group_rows)
                else:
                    # Extract values
                    values = [row.get(input_col) for row in group_rows]

                # Call aggregate function
                agg_result = call_function(agg_func, values)
                result[output_col] = agg_result

            yield result


def build_predicate_from_where(where_dict: Dict[str, Any], table_prefix: Optional[str] = None) -> Callable[[Dict], bool]:
    """
    Build a predicate function from a WHERE dictionary.

    Args:
        where_dict: WHERE clause dictionary
        table_prefix: Optional table name prefix for columns

    Returns:
        Predicate function
    """
    # Cache parser and evaluator for function expression evaluation
    _parser = None
    _evaluator = None

    def get_parser_and_evaluator():
        nonlocal _parser, _evaluator
        if _parser is None:
            from .expression_parser import ExpressionParser
            from .expression_evaluator import ExpressionEvaluator
            _parser = ExpressionParser()
            _evaluator = ExpressionEvaluator()
        return _parser, _evaluator

    def predicate(row: Dict[str, Any]) -> bool:
        for col, condition in where_dict.items():
            # Handle table prefix
            full_col = f"{table_prefix}.{col}" if table_prefix else col

            # Get value from row
            # Check if this is a function expression (contains '(')
            if '(' in col:
                try:
                    parser, evaluator = get_parser_and_evaluator()
                    from .expression_evaluator import EvaluationContext

                    # Parse and evaluate the function expression
                    ast = parser.parse(col)
                    context = EvaluationContext(row=row)
                    value = evaluator.evaluate(ast, context)
                except Exception:
                    # If evaluation fails, treat as None
                    value = None
            else:
                # Simple column lookup
                value = row.get(full_col) or row.get(col)

            # Check condition
            if not _match_condition(value, condition):
                return False

        return True

    return predicate


def _match_condition(value: Any, condition: Any) -> bool:
    """
    Check if value matches condition.

    Supports operators: $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin, $regex
    """
    # If condition is not a dict, treat as equality check
    if not isinstance(condition, dict):
        return value == condition

    # Handle operator-based conditions
    for op, op_value in condition.items():
        if op == "$eq":
            if value != op_value:
                return False
        elif op == "$ne":
            if value == op_value:
                return False
        elif op == "$gt":
            if not (value > op_value):
                return False
        elif op == "$gte":
            if not (value >= op_value):
                return False
        elif op == "$lt":
            if not (value < op_value):
                return False
        elif op == "$lte":
            if not (value <= op_value):
                return False
        elif op == "$in":
            if value not in op_value:
                return False
        elif op == "$nin":
            if value in op_value:
                return False
        elif op == "$regex":
            import re
            if not isinstance(value, str):
                return False
            if not re.search(op_value, value):
                return False
        else:
            # Unknown operator, treat as direct comparison
            return value == condition

    return True
