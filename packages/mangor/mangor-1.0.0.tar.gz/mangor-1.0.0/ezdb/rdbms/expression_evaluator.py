"""
Expression Evaluator
Evaluates expression AST nodes against data rows
"""

from typing import Any, Dict, Optional
import re
from .expression_ast import (
    ExpressionNode, LiteralNode, ColumnNode, BinaryOpNode, UnaryOpNode,
    FunctionCallNode, CaseNode, CastNode, ParenthesesNode,
    BetweenNode, InNode, IsNullNode, ExistsNode, SubqueryNode,
    AllNode, AnyNode, Operator, ExpressionType
)


class EvaluationContext:
    """Context for expression evaluation"""

    def __init__(self, row: Dict[str, Any] = None, variables: Dict[str, Any] = None, engine=None):
        self.row = row or {}
        self.variables = variables or {}
        self.engine = engine  # RDBMSEngine instance for executing subqueries

    def get_column_value(self, column_name: str) -> Any:
        """Get value of a column from current row"""
        # Try case-insensitive lookup
        for key, value in self.row.items():
            if key.upper() == column_name.upper():
                return value
        raise ValueError(f"Column not found: {column_name}")

    def get_variable(self, var_name: str) -> Any:
        """Get value of a variable"""
        return self.variables.get(var_name)


class ExpressionEvaluator:
    """Evaluates expression AST nodes"""

    def evaluate(self, node: ExpressionNode, context: EvaluationContext = None) -> Any:
        """Evaluate an expression node and return its value"""
        if context is None:
            context = EvaluationContext()

        # Dispatch to appropriate evaluation method
        if isinstance(node, LiteralNode):
            return self._evaluate_literal(node)

        elif isinstance(node, ColumnNode):
            return self._evaluate_column(node, context)

        elif isinstance(node, BinaryOpNode):
            return self._evaluate_binary_op(node, context)

        elif isinstance(node, UnaryOpNode):
            return self._evaluate_unary_op(node, context)

        elif isinstance(node, FunctionCallNode):
            return self._evaluate_function(node, context)

        elif isinstance(node, CaseNode):
            return self._evaluate_case(node, context)

        elif isinstance(node, CastNode):
            return self._evaluate_cast(node, context)

        elif isinstance(node, ParenthesesNode):
            return self.evaluate(node.expression, context)

        elif isinstance(node, BetweenNode):
            return self._evaluate_between(node, context)

        elif isinstance(node, InNode):
            return self._evaluate_in(node, context)

        elif isinstance(node, IsNullNode):
            return self._evaluate_is_null(node, context)

        elif isinstance(node, ExistsNode):
            return self._evaluate_exists(node, context)

        elif isinstance(node, SubqueryNode):
            return self._evaluate_subquery(node, context)

        elif isinstance(node, AllNode):
            return self._evaluate_all(node, context)

        elif isinstance(node, AnyNode):
            return self._evaluate_any(node, context)

        else:
            raise ValueError(f"Unknown expression node type: {type(node)}")

    def _evaluate_literal(self, node: LiteralNode) -> Any:
        """Evaluate literal value"""
        return node.value

    def _evaluate_column(self, node: ColumnNode, context: EvaluationContext) -> Any:
        """Evaluate column reference"""
        # For now, ignore table/schema qualifiers and just get column value
        return context.get_column_value(node.column_name)

    def _evaluate_binary_op(self, node: BinaryOpNode, context: EvaluationContext) -> Any:
        """Evaluate binary operation"""
        left = self.evaluate(node.left, context)
        right = self.evaluate(node.right, context)

        op = node.operator

        # Arithmetic operators
        if op == Operator.ADD:
            return self._add(left, right)
        elif op == Operator.SUBTRACT:
            return self._subtract(left, right)
        elif op == Operator.MULTIPLY:
            return self._multiply(left, right)
        elif op == Operator.DIVIDE:
            return self._divide(left, right)
        elif op == Operator.MOD:
            return self._mod(left, right)

        # String concatenation
        elif op == Operator.CONCAT:
            return self._concat(left, right)

        # Comparison operators
        elif op == Operator.EQ:
            return left == right
        elif op in [Operator.NE, Operator.NE_ALT]:
            return left != right
        elif op == Operator.LT:
            return self._compare_less_than(left, right)
        elif op == Operator.GT:
            return self._compare_greater_than(left, right)
        elif op == Operator.LE:
            return self._compare_less_equal(left, right)
        elif op == Operator.GE:
            return self._compare_greater_equal(left, right)

        # LIKE operator
        elif op == Operator.LIKE:
            return self._like(left, right)
        elif op == Operator.NOT_LIKE:
            return not self._like(left, right)

        # Logical operators
        elif op == Operator.AND:
            return self._logical_and(left, right)
        elif op == Operator.OR:
            return self._logical_or(left, right)

        else:
            raise ValueError(f"Unknown binary operator: {op}")

    def _evaluate_unary_op(self, node: UnaryOpNode, context: EvaluationContext) -> Any:
        """Evaluate unary operation"""
        operand = self.evaluate(node.operand, context)

        if node.operator == Operator.UNARY_PLUS:
            return +operand
        elif node.operator == Operator.UNARY_MINUS:
            return -operand
        elif node.operator == Operator.NOT:
            return not self._to_boolean(operand)
        else:
            raise ValueError(f"Unknown unary operator: {node.operator}")

    def _evaluate_function(self, node: FunctionCallNode, context: EvaluationContext) -> Any:
        """Evaluate function call"""
        func_name = node.function_name.upper()

        # Evaluate arguments
        args = [self.evaluate(arg, context) for arg in node.arguments]

        # Aggregate functions (need special handling)
        if func_name in ['SUM', 'AVG', 'COUNT', 'MIN', 'MAX']:
            raise NotImplementedError(f"Aggregate function {func_name} needs to be evaluated during query execution")

        # String functions
        if func_name == 'UPPER':
            return str(args[0]).upper() if args[0] is not None else None
        elif func_name == 'LOWER':
            return str(args[0]).lower() if args[0] is not None else None
        elif func_name == 'SUBSTR' or func_name == 'SUBSTRING':
            return self._substr(args)
        elif func_name == 'LENGTH' or func_name == 'LEN':
            return len(str(args[0])) if args[0] is not None else None
        elif func_name == 'TRIM':
            return str(args[0]).strip() if args[0] is not None else None
        elif func_name == 'LTRIM':
            return str(args[0]).lstrip() if args[0] is not None else None
        elif func_name == 'RTRIM':
            return str(args[0]).rstrip() if args[0] is not None else None
        elif func_name == 'CONCAT':
            return ''.join(str(arg) if arg is not None else '' for arg in args)

        # Numeric functions
        elif func_name == 'ABS':
            return abs(args[0]) if args[0] is not None else None
        elif func_name == 'ROUND':
            if len(args) == 1:
                return round(args[0])
            else:
                return round(args[0], int(args[1]))
        elif func_name == 'FLOOR':
            import math
            return math.floor(args[0]) if args[0] is not None else None
        elif func_name == 'CEIL' or func_name == 'CEILING':
            import math
            return math.ceil(args[0]) if args[0] is not None else None
        elif func_name == 'POWER' or func_name == 'POW':
            return args[0] ** args[1] if args[0] is not None and args[1] is not None else None
        elif func_name == 'SQRT':
            import math
            return math.sqrt(args[0]) if args[0] is not None else None

        # Date functions (basic - will be expanded in Phase 8)
        elif func_name == 'NOW' or func_name == 'CURRENT_TIMESTAMP':
            from datetime import datetime
            return datetime.now()
        elif func_name == 'CURRENT_DATE':
            from datetime import datetime
            return datetime.now().date()

        # Conditional functions
        elif func_name == 'COALESCE':
            for arg in args:
                if arg is not None:
                    return arg
            return None
        elif func_name == 'NULLIF':
            return None if args[0] == args[1] else args[0]
        elif func_name == 'NVL' or func_name == 'IFNULL':
            return args[1] if args[0] is None else args[0]

        else:
            raise ValueError(f"Unknown function: {func_name}")

    def _evaluate_case(self, node: CaseNode, context: EvaluationContext) -> Any:
        """Evaluate CASE expression"""
        # Simple CASE: CASE expr WHEN value1 THEN result1 ... END
        if node.case_expr:
            case_value = self.evaluate(node.case_expr, context)
            for when_clause in node.when_clauses:
                when_value = self.evaluate(when_clause.condition, context)
                if case_value == when_value:
                    return self.evaluate(when_clause.result, context)

        # Searched CASE: CASE WHEN condition1 THEN result1 ... END
        else:
            for when_clause in node.when_clauses:
                condition = self.evaluate(when_clause.condition, context)
                if self._to_boolean(condition):
                    return self.evaluate(when_clause.result, context)

        # ELSE clause
        if node.else_clause:
            return self.evaluate(node.else_clause, context)

        # No match and no ELSE
        return None

    def _evaluate_cast(self, node: CastNode, context: EvaluationContext) -> Any:
        """Evaluate CAST expression"""
        value = self.evaluate(node.expression, context)
        target_type = node.target_type.upper()

        if value is None:
            return None

        # Cast to different types
        if target_type in ['INTEGER', 'INT', 'SMALLINT', 'BIGINT']:
            return int(float(value))
        elif target_type in ['REAL', 'FLOAT', 'DOUBLE', 'NUMBER', 'NUMERIC', 'DECIMAL']:
            return float(value)
        elif target_type in ['VARCHAR', 'VARCHAR2', 'CHAR', 'TEXT', 'STRING']:
            return str(value)
        elif target_type in ['BOOLEAN', 'BOOL']:
            return self._to_boolean(value)
        else:
            raise ValueError(f"Unsupported CAST target type: {target_type}")

    def _evaluate_between(self, node: BetweenNode, context: EvaluationContext) -> bool:
        """Evaluate BETWEEN expression"""
        value = self.evaluate(node.expression, context)
        lower = self.evaluate(node.lower, context)
        upper = self.evaluate(node.upper, context)

        result = lower <= value <= upper
        return not result if node.negated else result

    def _evaluate_in(self, node: InNode, context: EvaluationContext) -> bool:
        """Evaluate IN expression"""
        value = self.evaluate(node.expression, context)

        # Subquery
        if isinstance(node.values, SubqueryNode):
            subquery_results = self._evaluate_subquery(node.values, context)
            # Subquery should return a list of values (one column)
            if not isinstance(subquery_results, list):
                subquery_results = [subquery_results]

            for val in subquery_results:
                if value == val:
                    return not node.negated

            return node.negated

        # List of values
        for val_node in node.values:
            val = self.evaluate(val_node, context)
            if value == val:
                return not node.negated if not node.negated else False

        return node.negated

    def _evaluate_is_null(self, node: IsNullNode, context: EvaluationContext) -> bool:
        """Evaluate IS NULL expression"""
        value = self.evaluate(node.expression, context)
        is_null = value is None
        return not is_null if node.negated else is_null

    # Helper methods for operators

    def _add(self, left: Any, right: Any) -> Any:
        """Addition"""
        if left is None or right is None:
            return None
        return left + right

    def _subtract(self, left: Any, right: Any) -> Any:
        """Subtraction"""
        if left is None or right is None:
            return None
        return left - right

    def _multiply(self, left: Any, right: Any) -> Any:
        """Multiplication"""
        if left is None or right is None:
            return None
        return left * right

    def _divide(self, left: Any, right: Any) -> Any:
        """Division"""
        if left is None or right is None:
            return None
        if right == 0:
            raise ValueError("Division by zero")
        return left / right

    def _mod(self, left: Any, right: Any) -> Any:
        """Modulo"""
        if left is None or right is None:
            return None
        return left % right

    def _concat(self, left: Any, right: Any) -> str:
        """String concatenation"""
        # Oracle behavior: NULL || anything = NULL
        if left is None or right is None:
            return None
        return str(left) + str(right)

    def _compare_less_than(self, left: Any, right: Any) -> bool:
        """Less than comparison"""
        if left is None or right is None:
            return False
        return left < right

    def _compare_greater_than(self, left: Any, right: Any) -> bool:
        """Greater than comparison"""
        if left is None or right is None:
            return False
        return left > right

    def _compare_less_equal(self, left: Any, right: Any) -> bool:
        """Less than or equal comparison"""
        if left is None or right is None:
            return False
        return left <= right

    def _compare_greater_equal(self, left: Any, right: Any) -> bool:
        """Greater than or equal comparison"""
        if left is None or right is None:
            return False
        return left >= right

    def _like(self, text: Any, pattern: Any) -> bool:
        """LIKE pattern matching"""
        if text is None or pattern is None:
            return False

        # Convert SQL LIKE pattern to regex
        # % = .* (zero or more of any character)
        # _ = . (exactly one of any character)

        # First, replace % and _ with placeholders
        pattern_str = str(pattern)
        pattern_str = pattern_str.replace('%', '\x00')  # Placeholder for %
        pattern_str = pattern_str.replace('_', '\x01')  # Placeholder for _

        # Escape regex special characters
        regex_pattern = re.escape(pattern_str)

        # Replace placeholders with regex equivalents
        regex_pattern = regex_pattern.replace('\x00', '.*')  # % -> .*
        regex_pattern = regex_pattern.replace('\x01', '.')   # _ -> .

        # Add anchors
        regex_pattern = '^' + regex_pattern + '$'

        return bool(re.match(regex_pattern, str(text), re.IGNORECASE))

    def _logical_and(self, left: Any, right: Any) -> bool:
        """Logical AND with NULL handling"""
        left_bool = self._to_boolean(left) if left is not None else None
        right_bool = self._to_boolean(right) if right is not None else None

        # Three-valued logic for NULL
        if left_bool is False or right_bool is False:
            return False
        if left_bool is None or right_bool is None:
            return None
        return True

    def _logical_or(self, left: Any, right: Any) -> bool:
        """Logical OR with NULL handling"""
        left_bool = self._to_boolean(left) if left is not None else None
        right_bool = self._to_boolean(right) if right is not None else None

        # Three-valued logic for NULL
        if left_bool is True or right_bool is True:
            return True
        if left_bool is None or right_bool is None:
            return None
        return False

    def _to_boolean(self, value: Any) -> bool:
        """Convert value to boolean"""
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return bool(value)

    def _substr(self, args: list) -> str:
        """SUBSTR/SUBSTRING function"""
        if not args or args[0] is None:
            return None

        text = str(args[0])

        # SUBSTR(text, start)
        if len(args) == 2:
            start = int(args[1]) - 1  # SQL is 1-indexed
            return text[start:]

        # SUBSTR(text, start, length)
        elif len(args) == 3:
            start = int(args[1]) - 1  # SQL is 1-indexed
            length = int(args[2])
            return text[start:start + length]

        else:
            raise ValueError("SUBSTR requires 2 or 3 arguments")

    def _evaluate_subquery(self, node: SubqueryNode, context: EvaluationContext) -> Any:
        """Evaluate subquery

        For correlated subqueries, the outer row context is injected into WHERE clause evaluation
        by pre-substituting column references that exist in outer context.

        Returns:
            - Single value for scalar subqueries (SELECT single_column FROM ... LIMIT 1)
            - List of values for subqueries in IN clause
            - None if no engine context is available
        """
        # If an engine is provided in context, execute the subquery
        if hasattr(context, 'engine') and context.engine:
            from .parser import RDBMSParser

            # Parse the subquery SQL
            parser = RDBMSParser()
            subquery_sql = node.query

            # For correlated subqueries, inject outer row context
            # by substituting column references with actual values
            if hasattr(context, 'row') and context.row:
                subquery_sql = self._inject_outer_context(subquery_sql, context.row)

            subquery_parsed = parser.parse(subquery_sql)

            # Execute the subquery
            result = context.engine._execute_select(subquery_parsed)

            # Return based on result structure
            if result['status'] == 'success':
                rows = result['rows']
                if not rows:
                    return None

                # Extract values from first column
                if len(rows) == 1 and len(rows[0]) == 1:
                    # Scalar subquery - single value
                    return list(rows[0].values())[0]
                else:
                    # Multi-row subquery - return list of first column values
                    return [list(row.values())[0] for row in rows]
            else:
                raise ValueError(f"Subquery execution failed: {result.get('error')}")

        # Fallback: return None if no engine context
        return None

    def _inject_outer_context(self, sql: str, outer_row: Dict[str, Any]) -> str:
        """
        Inject outer row context into correlated subquery by substituting
        column references with literal values.

        For example:
        - Input: "SELECT COUNT(*) FROM employees WHERE department = department"
        - Outer context: {'department': 'Engineering'}
        - Output: "SELECT COUNT(*) FROM employees WHERE department = 'Engineering'"

        This handles simple column references in WHERE clauses.
        """
        import re

        # For each column in outer context, try to substitute it in WHERE clause
        # This is a simple implementation - looks for unqualified column names after =, <, >, etc.
        result_sql = sql

        for col_name, col_value in outer_row.items():
            # Pattern to match: operator followed by the column name (as standalone word)
            # e.g., "department = department" or "salary > salary"
            # We want to replace the RIGHT side (the column reference from outer query)

            # Look for patterns like "= department" or "> salary" where column is on right side
            pattern = r'([=<>!]+)\s+(' + re.escape(col_name) + r')(\s|$|,|\))'

            # Format the value based on type
            if isinstance(col_value, str):
                replacement_value = f"'{col_value}'"
            elif col_value is None:
                replacement_value = 'NULL'
            else:
                replacement_value = str(col_value)

            # Replace: keep operator and whitespace, replace column name with value
            replacement = r'\1 ' + replacement_value + r'\3'
            result_sql = re.sub(pattern, replacement, result_sql)

        return result_sql

    def _evaluate_exists(self, node: ExistsNode, context: EvaluationContext) -> bool:
        """Evaluate EXISTS expression"""
        # Evaluate the subquery
        result = self._evaluate_subquery(node.subquery, context)

        # EXISTS returns TRUE if subquery returns at least one row
        if isinstance(result, list):
            exists = len(result) > 0
        else:
            exists = result is not None

        return not exists if node.negated else exists

    def _evaluate_all(self, node: AllNode, context: EvaluationContext) -> bool:
        """Evaluate ALL quantified comparison

        Returns true if comparison is true for ALL values returned by the subquery.
        Example: 95000 >= ALL (SELECT salary FROM employees)
        Returns true only if 95000 >= every salary in the result set.

        Special cases:
        - Empty result set: Returns TRUE (vacuous truth - true for all zero elements)
        - NULL values: Three-valued logic - NULL in comparison yields NULL/unknown
        """
        # Evaluate left side
        left_value = self.evaluate(node.left, context)

        # Execute subquery to get list of values
        subquery_result = self._evaluate_subquery(node.subquery, context)

        # Handle empty result set (SQL standard: ALL with empty set is TRUE)
        if not subquery_result:
            return True

        # Ensure we have a list
        if not isinstance(subquery_result, list):
            subquery_result = [subquery_result]

        # Check if comparison holds for ALL values
        for value in subquery_result:
            # Apply the comparison operator
            comparison_result = self._apply_comparison(left_value, node.operator, value)

            # If any comparison fails, return False
            if not comparison_result:
                return False

        # All comparisons succeeded
        return True

    def _evaluate_any(self, node: AnyNode, context: EvaluationContext) -> bool:
        """Evaluate ANY quantified comparison

        Returns true if comparison is true for ANY value returned by the subquery.
        Also known as SOME in SQL standard.
        Example: 90000 = ANY (SELECT salary FROM employees)
        Returns true if 90000 equals at least one salary in the result set.

        Special cases:
        - Empty result set: Returns FALSE (false for all zero elements)
        - NULL values: Three-valued logic - NULL in comparison yields NULL/unknown
        """
        # Evaluate left side
        left_value = self.evaluate(node.left, context)

        # Execute subquery to get list of values
        subquery_result = self._evaluate_subquery(node.subquery, context)

        # Handle empty result set (SQL standard: ANY with empty set is FALSE)
        if not subquery_result:
            return False

        # Ensure we have a list
        if not isinstance(subquery_result, list):
            subquery_result = [subquery_result]

        # Check if comparison holds for ANY value
        for value in subquery_result:
            # Apply the comparison operator
            comparison_result = self._apply_comparison(left_value, node.operator, value)

            # If any comparison succeeds, return True
            if comparison_result:
                return True

        # No comparisons succeeded
        return False

    def _apply_comparison(self, left: Any, operator: Operator, right: Any) -> bool:
        """Apply a comparison operator to two values

        Helper method for ALL/ANY evaluation to apply the operator
        """
        # Handle NULL values (NULL comparisons return NULL/False in boolean context)
        if left is None or right is None:
            return False

        # Apply the operator
        if operator == Operator.EQ:
            return left == right
        elif operator in [Operator.NE, Operator.NE_ALT]:
            return left != right
        elif operator == Operator.LT:
            return left < right
        elif operator == Operator.GT:
            return left > right
        elif operator == Operator.LE:
            return left <= right
        elif operator == Operator.GE:
            return left >= right
        else:
            raise ValueError(f"Unsupported operator for ALL/ANY: {operator}")
