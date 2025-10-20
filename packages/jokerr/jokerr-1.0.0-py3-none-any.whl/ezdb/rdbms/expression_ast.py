"""
Expression AST (Abstract Syntax Tree) Classes
Represents SQL expressions as a tree structure for evaluation
"""

from typing import Any, List, Optional, Union
from enum import Enum


class ExpressionType(Enum):
    """Types of expression nodes"""
    LITERAL = "literal"
    COLUMN = "column"
    BINARY_OP = "binary_op"
    UNARY_OP = "unary_op"
    FUNCTION_CALL = "function_call"
    CASE = "case"
    CAST = "cast"
    PARENTHESES = "parentheses"
    BETWEEN = "between"
    IN = "in"
    IS_NULL = "is_null"
    EXISTS = "exists"
    SUBQUERY = "subquery"
    ALL = "all"
    ANY = "any"


class Operator(Enum):
    """SQL operators with their precedence"""
    # Logical operators (lowest precedence)
    OR = ("OR", 1)
    AND = ("AND", 2)
    NOT = ("NOT", 3)

    # Comparison operators
    EQ = ("=", 4)
    NE = ("<>", 4)
    NE_ALT = ("!=", 4)
    LT = ("<", 4)
    GT = (">", 4)
    LE = ("<=", 4)
    GE = (">=", 4)
    LIKE = ("LIKE", 4)
    NOT_LIKE = ("NOT LIKE", 4)
    IS = ("IS", 4)
    IS_NOT = ("IS NOT", 4)
    IN = ("IN", 4)
    NOT_IN = ("NOT IN", 4)
    BETWEEN = ("BETWEEN", 4)
    NOT_BETWEEN = ("NOT BETWEEN", 4)

    # String concatenation
    CONCAT = ("||", 5)

    # Arithmetic operators
    ADD = ("+", 6)
    SUBTRACT = ("-", 6)
    MULTIPLY = ("*", 7)
    DIVIDE = ("/", 7)
    MOD = ("MOD", 7)

    # Unary operators (highest precedence)
    UNARY_PLUS = ("+", 8)
    UNARY_MINUS = ("-", 8)

    def __init__(self, symbol: str, precedence: int):
        self.symbol = symbol
        self.precedence = precedence

    @classmethod
    def from_symbol(cls, symbol: str) -> Optional['Operator']:
        """Get operator from its symbol"""
        symbol_upper = symbol.upper()
        for op in cls:
            if op.symbol.upper() == symbol_upper:
                return op
        return None


class ExpressionNode:
    """Base class for all expression AST nodes"""

    def __init__(self, expr_type: ExpressionType):
        self.expr_type = expr_type

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class LiteralNode(ExpressionNode):
    """Literal value: 42, 'hello', 3.14, TRUE, NULL"""

    def __init__(self, value: Any, data_type: str = None):
        super().__init__(ExpressionType.LITERAL)
        self.value = value
        self.data_type = data_type  # 'number', 'string', 'boolean', 'null'

    def __repr__(self):
        return f"Literal({self.value!r}, type={self.data_type})"


class ColumnNode(ExpressionNode):
    """Column reference: column_name, table.column, schema.table.column"""

    def __init__(self, column_name: str, table_name: str = None, schema_name: str = None):
        super().__init__(ExpressionType.COLUMN)
        self.column_name = column_name
        self.table_name = table_name
        self.schema_name = schema_name

    def __repr__(self):
        parts = []
        if self.schema_name:
            parts.append(self.schema_name)
        if self.table_name:
            parts.append(self.table_name)
        parts.append(self.column_name)
        return f"Column({'.'.join(parts)})"


class BinaryOpNode(ExpressionNode):
    """Binary operation: left OPERATOR right"""

    def __init__(self, left: ExpressionNode, operator: Operator, right: ExpressionNode):
        super().__init__(ExpressionType.BINARY_OP)
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left} {self.operator.symbol} {self.right})"


class UnaryOpNode(ExpressionNode):
    """Unary operation: OPERATOR operand"""

    def __init__(self, operator: Operator, operand: ExpressionNode):
        super().__init__(ExpressionType.UNARY_OP)
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.operator.symbol} {self.operand})"


class FunctionCallNode(ExpressionNode):
    """Function call: FUNCTION_NAME(arg1, arg2, ...)"""

    def __init__(self, function_name: str, arguments: List[ExpressionNode], distinct: bool = False):
        super().__init__(ExpressionType.FUNCTION_CALL)
        self.function_name = function_name.upper()
        self.arguments = arguments
        self.distinct = distinct

    def __repr__(self):
        args_str = ', '.join(str(arg) for arg in self.arguments)
        distinct_str = "DISTINCT " if self.distinct else ""
        return f"Function({self.function_name}({distinct_str}{args_str}))"


class CaseWhenClause:
    """Single WHEN clause in CASE expression"""

    def __init__(self, condition: ExpressionNode, result: ExpressionNode):
        self.condition = condition
        self.result = result

    def __repr__(self):
        return f"WHEN {self.condition} THEN {self.result}"


class CaseNode(ExpressionNode):
    """CASE expression: CASE [expr] WHEN ... THEN ... [ELSE ...] END"""

    def __init__(self,
                 when_clauses: List[CaseWhenClause],
                 else_clause: Optional[ExpressionNode] = None,
                 case_expr: Optional[ExpressionNode] = None):
        super().__init__(ExpressionType.CASE)
        self.when_clauses = when_clauses
        self.else_clause = else_clause
        self.case_expr = case_expr  # For simple CASE (CASE expr WHEN value ...)

    def __repr__(self):
        when_str = ' '.join(str(w) for w in self.when_clauses)
        else_str = f" ELSE {self.else_clause}" if self.else_clause else ""
        case_str = f" {self.case_expr}" if self.case_expr else ""
        return f"Case({case_str} {when_str}{else_str})"


class CastNode(ExpressionNode):
    """CAST expression: CAST(expr AS type)"""

    def __init__(self, expression: ExpressionNode, target_type: str):
        super().__init__(ExpressionType.CAST)
        self.expression = expression
        self.target_type = target_type

    def __repr__(self):
        return f"Cast({self.expression} AS {self.target_type})"


class ParenthesesNode(ExpressionNode):
    """Parenthesized expression: (expr)"""

    def __init__(self, expression: ExpressionNode):
        super().__init__(ExpressionType.PARENTHESES)
        self.expression = expression

    def __repr__(self):
        return f"({self.expression})"


class BetweenNode(ExpressionNode):
    """BETWEEN expression: expr BETWEEN lower AND upper"""

    def __init__(self, expression: ExpressionNode, lower: ExpressionNode,
                 upper: ExpressionNode, negated: bool = False):
        super().__init__(ExpressionType.BETWEEN)
        self.expression = expression
        self.lower = lower
        self.upper = upper
        self.negated = negated

    def __repr__(self):
        not_str = "NOT " if self.negated else ""
        return f"{self.expression} {not_str}BETWEEN {self.lower} AND {self.upper}"


class InNode(ExpressionNode):
    """IN expression: expr IN (value1, value2, ...) or expr IN (subquery)"""

    def __init__(self, expression: ExpressionNode,
                 values: Union[List[ExpressionNode], 'SubqueryNode'],
                 negated: bool = False):
        super().__init__(ExpressionType.IN)
        self.expression = expression
        self.values = values
        self.negated = negated

    def __repr__(self):
        not_str = "NOT " if self.negated else ""
        if isinstance(self.values, list):
            values_str = ', '.join(str(v) for v in self.values)
            return f"{self.expression} {not_str}IN ({values_str})"
        else:
            return f"{self.expression} {not_str}IN ({self.values})"


class IsNullNode(ExpressionNode):
    """IS NULL expression: expr IS [NOT] NULL"""

    def __init__(self, expression: ExpressionNode, negated: bool = False):
        super().__init__(ExpressionType.IS_NULL)
        self.expression = expression
        self.negated = negated

    def __repr__(self):
        not_str = "NOT " if self.negated else ""
        return f"{self.expression} IS {not_str}NULL"


class ExistsNode(ExpressionNode):
    """EXISTS expression: EXISTS (subquery)"""

    def __init__(self, subquery: 'SubqueryNode', negated: bool = False):
        super().__init__(ExpressionType.EXISTS)
        self.subquery = subquery
        self.negated = negated

    def __repr__(self):
        not_str = "NOT " if self.negated else ""
        return f"{not_str}EXISTS ({self.subquery})"


class SubqueryNode(ExpressionNode):
    """Subquery: (SELECT ...)

    The query attribute can be:
    - A SelectQuery object (from ezdb.rdbms.parser)
    - A string SQL query (to be parsed later)
    """

    def __init__(self, query, is_correlated: bool = False):
        super().__init__(ExpressionType.SUBQUERY)
        self.query = query  # SelectQuery object or string SQL
        self.is_correlated = is_correlated  # References outer query columns

    def __repr__(self):
        correlated_str = " CORRELATED" if self.is_correlated else ""
        return f"Subquery({self.query}{correlated_str})"


class AllNode(ExpressionNode):
    """ALL quantifier: value OPERATOR ALL (subquery)

    Returns true if comparison is true for ALL values returned by the subquery.
    Example: 95000 >= ALL (SELECT salary FROM employees)
    Returns true only if 95000 >= every salary in the result set.
    """

    def __init__(self, left: ExpressionNode, operator: Operator, subquery: 'SubqueryNode'):
        super().__init__(ExpressionType.ALL)
        self.left = left
        self.operator = operator
        self.subquery = subquery

    def __repr__(self):
        return f"{self.left} {self.operator.symbol} ALL ({self.subquery})"


class AnyNode(ExpressionNode):
    """ANY quantifier: value OPERATOR ANY (subquery)

    Returns true if comparison is true for ANY value returned by the subquery.
    Also known as SOME in SQL standard.
    Example: 90000 = ANY (SELECT salary FROM employees)
    Returns true if 90000 equals at least one salary in the result set.
    """

    def __init__(self, left: ExpressionNode, operator: Operator, subquery: 'SubqueryNode'):
        super().__init__(ExpressionType.ANY)
        self.left = left
        self.operator = operator
        self.subquery = subquery

    def __repr__(self):
        return f"{self.left} {self.operator.symbol} ANY ({self.subquery})"
