"""
Expression Parser for SQL
Parses SQL expressions into AST using operator precedence climbing
"""

import re
from typing import List, Optional, Union
from .expression_ast import (
    ExpressionNode, LiteralNode, ColumnNode, BinaryOpNode, UnaryOpNode,
    FunctionCallNode, CaseNode, CaseWhenClause, CastNode, ParenthesesNode,
    BetweenNode, InNode, IsNullNode, ExistsNode, SubqueryNode,
    AllNode, AnyNode, Operator, ExpressionType
)


class Token:
    """Token in expression"""

    def __init__(self, token_type: str, value: str, position: int):
        self.type = token_type  # 'operator', 'literal', 'identifier', 'keyword', 'punctuation'
        self.value = value
        self.position = position

    def __repr__(self):
        return f"Token({self.type}: {self.value!r})"


class ExpressionParser:
    """
    Parses SQL expressions into AST

    Uses operator precedence climbing algorithm for correct operator precedence:
    1. OR (lowest)
    2. AND
    3. NOT
    4. Comparison (=, <>, <, >, <=, >=, LIKE, BETWEEN, IN, IS)
    5. String concatenation (||)
    6. Addition/Subtraction (+, -)
    7. Multiplication/Division/Modulo (*, /, MOD)
    8. Unary operators (+, -)
    9. Function calls, literals, column references (highest)
    """

    def __init__(self):
        self.tokens: List[Token] = []
        self.current_pos = 0

    def parse(self, expression: str) -> ExpressionNode:
        """Parse an expression string into AST"""
        if not expression or not expression.strip():
            raise ValueError("Empty expression")

        # Tokenize
        self.tokens = self._tokenize(expression)
        self.current_pos = 0

        # Parse using precedence climbing
        result = self._parse_expression(0)

        # Check for unexpected tokens
        if self.current_pos < len(self.tokens):
            raise ValueError(f"Unexpected token: {self.tokens[self.current_pos]}")

        return result

    def _tokenize(self, expression: str) -> List[Token]:
        """Tokenize expression into tokens"""
        tokens = []
        pos = 0
        length = len(expression)

        while pos < length:
            # Skip whitespace
            if expression[pos].isspace():
                pos += 1
                continue

            # String literals (single quotes)
            if expression[pos] == "'":
                end_pos = pos + 1
                while end_pos < length:
                    if expression[end_pos] == "'":
                        # Check for escaped quote ''
                        if end_pos + 1 < length and expression[end_pos + 1] == "'":
                            end_pos += 2
                        else:
                            break
                    end_pos += 1

                if end_pos >= length:
                    raise ValueError("Unterminated string literal")

                value = expression[pos:end_pos + 1]
                tokens.append(Token('literal', value, pos))
                pos = end_pos + 1
                continue

            # Numbers (including decimals)
            if expression[pos].isdigit() or (expression[pos] == '.' and pos + 1 < length and expression[pos + 1].isdigit()):
                end_pos = pos
                has_dot = False
                while end_pos < length and (expression[end_pos].isdigit() or
                                            (expression[end_pos] == '.' and not has_dot)):
                    if expression[end_pos] == '.':
                        has_dot = True
                    end_pos += 1

                value = expression[pos:end_pos]
                tokens.append(Token('literal', value, pos))
                pos = end_pos
                continue

            # Multi-character operators
            if pos + 1 < length:
                two_char = expression[pos:pos + 2]
                if two_char in ['<=', '>=', '<>', '!=', '||']:
                    tokens.append(Token('operator', two_char, pos))
                    pos += 2
                    continue

            # Single character operators and punctuation
            if expression[pos] in '()+-*/<>=,':
                token_type = 'punctuation' if expression[pos] in '(),' else 'operator'
                tokens.append(Token(token_type, expression[pos], pos))
                pos += 1
                continue

            # Identifiers and keywords
            if expression[pos].isalpha() or expression[pos] == '_':
                end_pos = pos
                while end_pos < length and (expression[end_pos].isalnum() or expression[end_pos] in '_.'):
                    end_pos += 1

                value = expression[pos:end_pos]

                # Check if it's a keyword
                upper_value = value.upper()
                keywords = ['AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN', 'IS', 'NULL',
                           'TRUE', 'FALSE', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
                           'CAST', 'AS', 'EXISTS', 'MOD', 'DISTINCT', 'ALL', 'ANY', 'SOME',
                           'SELECT', 'FROM', 'WHERE', 'GROUP', 'BY', 'HAVING', 'ORDER', 'LIMIT']

                token_type = 'keyword' if upper_value in keywords else 'identifier'
                tokens.append(Token(token_type, value, pos))
                pos = end_pos
                continue

            # Unknown character
            raise ValueError(f"Unexpected character at position {pos}: {expression[pos]}")

        return tokens

    def _current_token(self) -> Optional[Token]:
        """Get current token without consuming it"""
        if self.current_pos < len(self.tokens):
            return self.tokens[self.current_pos]
        return None

    def _consume_token(self) -> Optional[Token]:
        """Consume and return current token"""
        token = self._current_token()
        if token:
            self.current_pos += 1
        return token

    def _peek_token(self, offset: int = 1) -> Optional[Token]:
        """Peek at token at offset from current position"""
        pos = self.current_pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def _parse_expression(self, min_precedence: int) -> ExpressionNode:
        """
        Parse expression using precedence climbing algorithm

        Algorithm:
        1. Parse left operand (primary expression)
        2. While next operator has precedence >= min_precedence:
           - Consume operator
           - Parse right operand with higher precedence
           - Create binary operation node
        """
        # Parse left operand (primary expression)
        left = self._parse_primary()

        # Precedence climbing
        while True:
            token = self._current_token()
            if not token:
                break

            # Check if it's a binary operator
            operator = self._get_binary_operator(token)
            if not operator:
                break

            # Check precedence
            if operator.precedence < min_precedence:
                break

            # Special handling for multi-token operators
            if operator in [Operator.NOT_LIKE, Operator.NOT_IN, Operator.IS_NOT,
                           Operator.NOT_BETWEEN, Operator.IS, Operator.IN]:
                left = self._parse_complex_operator(left, operator)
                continue

            # Consume operator
            self._consume_token()

            # Special case: BETWEEN
            if operator == Operator.BETWEEN:
                left = self._parse_between(left, negated=False)
                continue

            # Check for ALL/ANY quantifiers after comparison operators
            next_token = self._current_token()
            if (operator in [Operator.EQ, Operator.NE, Operator.NE_ALT,
                           Operator.LT, Operator.GT, Operator.LE, Operator.GE] and
                next_token and next_token.type == 'keyword' and
                next_token.value.upper() in ['ALL', 'ANY', 'SOME']):

                quantifier = next_token.value.upper()
                self._consume_token()  # consume ALL/ANY/SOME

                # Expect (
                paren = self._consume_token()
                if not paren or paren.value != '(':
                    raise ValueError(f"Expected '(' after {quantifier}")

                # Parse subquery
                subquery_token = self._current_token()
                if not subquery_token or subquery_token.type != 'keyword' or subquery_token.value.upper() != 'SELECT':
                    raise ValueError(f"Expected SELECT after {quantifier} (")

                subquery = self._parse_subquery()

                # Create ALL or ANY node
                if quantifier == 'ALL':
                    left = AllNode(left, operator, subquery)
                else:  # ANY or SOME
                    left = AnyNode(left, operator, subquery)

                continue

            # Parse right operand with higher precedence
            right = self._parse_expression(operator.precedence + 1)

            # Create binary operation
            left = BinaryOpNode(left, operator, right)

        return left

    def _parse_primary(self) -> ExpressionNode:
        """Parse primary expression (highest precedence)"""
        token = self._current_token()

        if not token:
            raise ValueError("Unexpected end of expression")

        # Parentheses
        if token.type == 'punctuation' and token.value == '(':
            self._consume_token()

            # Check for subquery (starts with SELECT)
            next_token = self._current_token()
            if next_token and next_token.type == 'keyword' and next_token.value.upper() == 'SELECT':
                # Parse subquery (it consumes the closing paren)
                return self._parse_subquery()

            # Regular parenthesized expression
            expr = self._parse_expression(0)

            close_paren = self._consume_token()
            if not close_paren or close_paren.value != ')':
                raise ValueError("Expected closing parenthesis")

            return ParenthesesNode(expr)

        # Unary operators
        if token.type == 'operator' and token.value in ['+', '-']:
            self._consume_token()
            operand = self._parse_primary()
            op = Operator.UNARY_PLUS if token.value == '+' else Operator.UNARY_MINUS
            return UnaryOpNode(op, operand)

        # NOT operator
        if token.type == 'keyword' and token.value.upper() == 'NOT':
            self._consume_token()
            operand = self._parse_expression(Operator.NOT.precedence + 1)
            return UnaryOpNode(Operator.NOT, operand)

        # EXISTS
        if token.type == 'keyword' and token.value.upper() == 'EXISTS':
            self._consume_token()
            # Expect (subquery)
            paren = self._consume_token()
            if not paren or paren.value != '(':
                raise ValueError("Expected '(' after EXISTS")

            # Parse the subquery
            subquery = self._parse_subquery()
            return ExistsNode(subquery, negated=False)

        # CASE expression
        if token.type == 'keyword' and token.value.upper() == 'CASE':
            return self._parse_case()

        # CAST expression
        if token.type == 'keyword' and token.value.upper() == 'CAST':
            return self._parse_cast()

        # Literals
        if token.type == 'literal':
            return self._parse_literal()

        # Keywords: TRUE, FALSE, NULL
        if token.type == 'keyword':
            upper_value = token.value.upper()
            if upper_value == 'TRUE':
                self._consume_token()
                return LiteralNode(True, 'boolean')
            elif upper_value == 'FALSE':
                self._consume_token()
                return LiteralNode(False, 'boolean')
            elif upper_value == 'NULL':
                self._consume_token()
                return LiteralNode(None, 'null')

        # Identifier (column or function call)
        if token.type == 'identifier':
            return self._parse_identifier()

        raise ValueError(f"Unexpected token: {token}")

    def _parse_literal(self) -> LiteralNode:
        """Parse a literal value"""
        token = self._consume_token()
        value = token.value

        # String literal
        if value.startswith("'"):
            # Remove quotes and handle escaped quotes
            string_value = value[1:-1].replace("''", "'")
            return LiteralNode(string_value, 'string')

        # Number literal
        if '.' in value:
            return LiteralNode(float(value), 'number')
        else:
            return LiteralNode(int(value), 'number')

    def _parse_identifier(self) -> Union[ColumnNode, FunctionCallNode]:
        """Parse identifier (column reference or function call)"""
        token = self._consume_token()
        name = token.value

        # Check for function call
        next_token = self._current_token()
        if next_token and next_token.type == 'punctuation' and next_token.value == '(':
            return self._parse_function_call(name)

        # Check for qualified column name (table.column or schema.table.column)
        parts = [name]
        while True:
            dot_token = self._current_token()
            if not dot_token or dot_token.value != '.':
                break

            self._consume_token()  # consume '.'

            next_part = self._consume_token()
            if not next_part or next_part.type != 'identifier':
                raise ValueError("Expected identifier after '.'")

            parts.append(next_part.value)

        # Create column node
        if len(parts) == 1:
            return ColumnNode(parts[0])
        elif len(parts) == 2:
            return ColumnNode(parts[1], table_name=parts[0])
        elif len(parts) == 3:
            return ColumnNode(parts[2], table_name=parts[1], schema_name=parts[0])
        else:
            raise ValueError("Invalid column reference")

    def _parse_function_call(self, function_name: str) -> FunctionCallNode:
        """Parse function call: FUNCTION_NAME(args)"""
        # Consume opening parenthesis
        self._consume_token()

        # Check for DISTINCT
        distinct = False
        token = self._current_token()
        if token and token.type == 'keyword' and token.value.upper() == 'DISTINCT':
            distinct = True
            self._consume_token()

        # Parse arguments
        arguments = []

        # Check for empty argument list
        token = self._current_token()
        if token and token.value == ')':
            self._consume_token()
            return FunctionCallNode(function_name, arguments, distinct)

        # Parse first argument
        arguments.append(self._parse_expression(0))

        # Parse additional arguments
        while True:
            token = self._current_token()
            if not token:
                raise ValueError("Expected ')' after function arguments")

            if token.value == ')':
                self._consume_token()
                break

            if token.value != ',':
                raise ValueError(f"Expected ',' or ')' in function arguments, got {token}")

            self._consume_token()  # consume ','
            arguments.append(self._parse_expression(0))

        return FunctionCallNode(function_name, arguments, distinct)

    def _parse_case_expr_until_when(self) -> ExpressionNode:
        """Parse expression until WHEN keyword"""
        return self._parse_case_expr_until_keyword(['WHEN'])

    def _parse_case_expr_until_keyword(self, keywords: list) -> ExpressionNode:
        """Parse expression until one of the specified keywords is encountered"""
        # Save position in case we need to backtrack
        start_pos = self.current_pos

        # Parse expression with precedence 0, but stop at keywords
        left = self._parse_primary()

        while True:
            token = self._current_token()
            if not token:
                break

            # Stop if we hit one of the target keywords
            if token.type == 'keyword' and token.value.upper() in keywords:
                break

            operator = self._get_binary_operator(token)
            if not operator:
                break

            # Check for complex operators
            if operator in [Operator.NOT_LIKE, Operator.BETWEEN, Operator.NOT_BETWEEN,
                           Operator.IN, Operator.NOT_IN, Operator.IS, Operator.IS_NOT]:
                left = self._parse_complex_operator(left, operator)
                continue

            # Consume operator
            self._consume_token()

            # Parse right operand - also stop at keywords
            right = self._parse_primary()

            # Check if next token is an operator with higher precedence
            next_token = self._current_token()
            while next_token and not (next_token.type == 'keyword' and next_token.value.upper() in keywords):
                next_op = self._get_binary_operator(next_token)
                if not next_op or next_op.precedence <= operator.precedence:
                    break

                # Right-associative: parse right side with higher precedence
                if next_op in [Operator.NOT_LIKE, Operator.BETWEEN, Operator.NOT_BETWEEN,
                             Operator.IN, Operator.NOT_IN, Operator.IS, Operator.IS_NOT]:
                    right = self._parse_complex_operator(right, next_op)
                else:
                    self._consume_token()
                    right_right = self._parse_primary()
                    right = BinaryOpNode(right, next_op, right_right)

                next_token = self._current_token()

            left = BinaryOpNode(left, operator, right)

        return left

    def _parse_case(self) -> CaseNode:
        """Parse CASE expression"""
        self._consume_token()  # consume CASE

        # Check if it's a simple CASE (CASE expr WHEN value ...)
        case_expr = None
        token = self._current_token()
        if token and not (token.type == 'keyword' and token.value.upper() == 'WHEN'):
            # Parse case expression - stop before WHEN
            case_expr = self._parse_case_expr_until_when()

        # Parse WHEN clauses
        when_clauses = []
        while True:
            token = self._current_token()
            if not token or not (token.type == 'keyword' and token.value.upper() == 'WHEN'):
                break

            self._consume_token()  # consume WHEN

            # Parse condition - stop before THEN
            condition = self._parse_case_expr_until_keyword(['THEN'])

            then_token = self._consume_token()
            if not then_token or then_token.value.upper() != 'THEN':
                raise ValueError("Expected THEN after WHEN condition")

            # Parse result - stop before WHEN/ELSE/END
            result = self._parse_case_expr_until_keyword(['WHEN', 'ELSE', 'END'])

            when_clauses.append(CaseWhenClause(condition, result))

        if not when_clauses:
            raise ValueError("CASE expression must have at least one WHEN clause")

        # Parse optional ELSE
        else_clause = None
        token = self._current_token()
        if token and token.type == 'keyword' and token.value.upper() == 'ELSE':
            self._consume_token()
            # Parse else result - stop before END
            else_clause = self._parse_case_expr_until_keyword(['END'])

        # Consume END
        end_token = self._consume_token()
        if not end_token or end_token.value.upper() != 'END':
            raise ValueError("Expected END to close CASE expression")

        return CaseNode(when_clauses, else_clause, case_expr)

    def _parse_cast(self) -> CastNode:
        """Parse CAST expression: CAST(expr AS type)"""
        self._consume_token()  # consume CAST

        # Expect (
        paren = self._consume_token()
        if not paren or paren.value != '(':
            raise ValueError("Expected '(' after CAST")

        # Parse expression
        expr = self._parse_expression(0)

        # Expect AS
        as_token = self._consume_token()
        if not as_token or as_token.value.upper() != 'AS':
            raise ValueError("Expected AS in CAST expression")

        # Parse target type
        type_token = self._consume_token()
        if not type_token or type_token.type != 'identifier':
            raise ValueError("Expected data type after AS")

        target_type = type_token.value

        # Expect )
        close_paren = self._consume_token()
        if not close_paren or close_paren.value != ')':
            raise ValueError("Expected ')' to close CAST")

        return CastNode(expr, target_type)

    def _parse_subquery(self) -> SubqueryNode:
        """Parse subquery: SELECT ...

        Assumes opening '(' has already been consumed and current token is SELECT.
        Consumes tokens until the matching closing ')'.
        """
        # Collect all tokens until closing parenthesis
        # We need to track nested parentheses to find the correct closing paren

        subquery_tokens = []
        paren_depth = 0  # We're parsing the SELECT statement itself

        while True:
            token = self._current_token()
            if not token:
                raise ValueError("Unexpected end of expression while parsing subquery")

            # Track parenthesis depth
            if token.value == '(':
                paren_depth += 1
                subquery_tokens.append(token)
                self._consume_token()
            elif token.value == ')':
                if paren_depth == 0:
                    # This is the closing paren for our subquery
                    self._consume_token()
                    break
                else:
                    paren_depth -= 1
                    subquery_tokens.append(token)
                    self._consume_token()
            else:
                subquery_tokens.append(token)
                self._consume_token()

        # Reconstruct SQL from tokens
        sql_parts = []
        for token in subquery_tokens:
            if token.type == 'literal':
                # String literals already have quotes, numbers don't
                if token.value.startswith("'"):
                    # Already a string literal with quotes
                    sql_parts.append(token.value)
                else:
                    # Numeric literal - use as-is
                    sql_parts.append(token.value)
            else:
                sql_parts.append(token.value)

        sql = ' '.join(sql_parts)

        # For now, store as string - it will be parsed when executed
        # TODO: Detect if it's correlated by checking for outer column references
        return SubqueryNode(sql, is_correlated=False)

    def _parse_between(self, expr: ExpressionNode, negated: bool) -> BetweenNode:
        """Parse BETWEEN: expr BETWEEN lower AND upper"""
        lower = self._parse_expression(Operator.BETWEEN.precedence + 1)

        and_token = self._consume_token()
        if not and_token or and_token.value.upper() != 'AND':
            raise ValueError("Expected AND in BETWEEN expression")

        upper = self._parse_expression(Operator.BETWEEN.precedence + 1)

        return BetweenNode(expr, lower, upper, negated)

    def _parse_complex_operator(self, left: ExpressionNode, operator: Operator) -> ExpressionNode:
        """Parse complex operators that span multiple tokens"""

        # IS NULL / IS NOT NULL
        if operator == Operator.IS or operator == Operator.IS_NOT:
            negated = (operator == Operator.IS_NOT)

            if negated:
                self._consume_token()  # consume IS
                self._consume_token()  # consume NOT
            else:
                self._consume_token()  # consume IS

            null_token = self._consume_token()
            if not null_token or null_token.value.upper() != 'NULL':
                raise ValueError("Expected NULL after IS [NOT]")

            return IsNullNode(left, negated)

        # NOT LIKE
        if operator == Operator.NOT_LIKE:
            self._consume_token()  # consume NOT
            like_token = self._consume_token()
            if not like_token or like_token.value.upper() != 'LIKE':
                raise ValueError("Expected LIKE after NOT")

            right = self._parse_expression(Operator.LIKE.precedence + 1)
            return BinaryOpNode(left, Operator.NOT_LIKE, right)

        # NOT BETWEEN
        if operator == Operator.NOT_BETWEEN:
            self._consume_token()  # consume NOT
            between_token = self._consume_token()
            if not between_token or between_token.value.upper() != 'BETWEEN':
                raise ValueError("Expected BETWEEN after NOT")

            return self._parse_between(left, negated=True)

        # IN / NOT IN
        if operator in [Operator.IN, Operator.NOT_IN]:
            negated = (operator == Operator.NOT_IN)

            if negated:
                self._consume_token()  # consume NOT
                in_token = self._consume_token()
                if not in_token or in_token.value.upper() != 'IN':
                    raise ValueError("Expected IN after NOT")
            else:
                self._consume_token()  # consume IN

            # Expect (
            paren = self._consume_token()
            if not paren or paren.value != '(':
                raise ValueError("Expected '(' after IN")

            # Check if this is a subquery (starts with SELECT)
            next_token = self._current_token()
            if next_token and next_token.type == 'keyword' and next_token.value.upper() == 'SELECT':
                # Parse subquery
                subquery = self._parse_subquery()
                return InNode(left, subquery, negated)

            # Parse list of values
            values = []
            # Parse first value with high precedence to stop at ',' or ')'
            values.append(self._parse_expression(100))

            while True:
                token = self._current_token()
                if not token:
                    raise ValueError("Expected ')' after IN values")

                if token.value == ')':
                    self._consume_token()
                    break

                if token.value != ',':
                    raise ValueError(f"Expected ',' or ')' in IN list")

                self._consume_token()  # consume ','
                values.append(self._parse_expression(100))

            return InNode(left, values, negated)

        raise ValueError(f"Unknown complex operator: {operator}")

    def _get_binary_operator(self, token: Token) -> Optional[Operator]:
        """Get binary operator from token"""
        if token.type == 'operator':
            return Operator.from_symbol(token.value)

        if token.type == 'keyword':
            upper_value = token.value.upper()

            # Check for multi-token operators
            if upper_value == 'NOT':
                next_token = self._peek_token()
                if next_token:
                    next_upper = next_token.value.upper()
                    if next_upper == 'LIKE':
                        return Operator.NOT_LIKE
                    elif next_upper == 'IN':
                        return Operator.NOT_IN
                    elif next_upper == 'BETWEEN':
                        return Operator.NOT_BETWEEN

            elif upper_value == 'IS':
                next_token = self._peek_token()
                if next_token and next_token.value.upper() == 'NOT':
                    return Operator.IS_NOT
                return Operator.IS

            return Operator.from_symbol(upper_value)

        return None
