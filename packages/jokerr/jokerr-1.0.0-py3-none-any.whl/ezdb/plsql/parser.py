"""
PL/SQL Parser
Parses PL/SQL code into an Abstract Syntax Tree (AST)
"""

import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ASTNode:
    """Base class for AST nodes"""
    node_type: str


@dataclass
class PLSQLBlock(ASTNode):
    """DECLARE...BEGIN...END block"""
    declarations: List['Declaration']
    statements: List['Statement']
    exception_handlers: List['ExceptionHandler'] = None

    def __init__(self, declarations, statements, exception_handlers=None):
        super().__init__('plsql_block')
        self.declarations = declarations or []
        self.statements = statements or []
        self.exception_handlers = exception_handlers or []


@dataclass
class Declaration(ASTNode):
    """Variable declaration"""
    var_name: str
    var_type: str
    initial_value: Any = None
    is_constant: bool = False

    def __init__(self, var_name, var_type, initial_value=None, is_constant=False):
        super().__init__('declaration')
        self.var_name = var_name
        self.var_type = var_type
        self.initial_value = initial_value
        self.is_constant = is_constant


@dataclass
class Assignment(ASTNode):
    """Variable assignment"""
    var_name: str
    expression: Any

    def __init__(self, var_name, expression):
        super().__init__('assignment')
        self.var_name = var_name
        self.expression = expression


@dataclass
class IfStatement(ASTNode):
    """IF-THEN-ELSE statement"""
    condition: str
    then_statements: List['Statement']
    elsif_clauses: List[tuple] = None  # [(condition, statements), ...]
    else_statements: List['Statement'] = None

    def __init__(self, condition, then_statements, elsif_clauses=None, else_statements=None):
        super().__init__('if_statement')
        self.condition = condition
        self.then_statements = then_statements
        self.elsif_clauses = elsif_clauses or []
        self.else_statements = else_statements or []


@dataclass
class LoopStatement(ASTNode):
    """LOOP statement"""
    loop_type: str  # 'basic', 'while', 'for'
    condition: str = None  # for WHILE loops
    iterator: str = None  # for FOR loops
    range_start: Any = None
    range_end: Any = None
    statements: List['Statement'] = None

    def __init__(self, loop_type, condition=None, iterator=None, range_start=None, range_end=None, statements=None):
        super().__init__('loop_statement')
        self.loop_type = loop_type
        self.condition = condition
        self.iterator = iterator
        self.range_start = range_start
        self.range_end = range_end
        self.statements = statements or []


@dataclass
class ExitStatement(ASTNode):
    """EXIT statement"""
    condition: str = None

    def __init__(self, condition=None):
        super().__init__('exit_statement')
        self.condition = condition


@dataclass
class SQLStatement(ASTNode):
    """Embedded SQL statement"""
    sql_type: str  # 'select_into', 'insert', 'update', 'delete'
    sql_text: str
    into_variables: List[str] = None

    def __init__(self, sql_type, sql_text, into_variables=None):
        super().__init__('sql_statement')
        self.sql_type = sql_type
        self.sql_text = sql_text
        self.into_variables = into_variables or []


@dataclass
class OutputStatement(ASTNode):
    """DBMS_OUTPUT.PUT_LINE statement"""
    expression: str

    def __init__(self, expression):
        super().__init__('output_statement')
        self.expression = expression


@dataclass
class ExceptionHandler(ASTNode):
    """Exception handler"""
    exception_name: str
    statements: List['Statement']

    def __init__(self, exception_name, statements):
        super().__init__('exception_handler')
        self.exception_name = exception_name
        self.statements = statements


@dataclass
class CursorDeclaration(ASTNode):
    """Cursor declaration"""
    cursor_name: str
    query: str

    def __init__(self, cursor_name, query):
        super().__init__('cursor_declaration')
        self.cursor_name = cursor_name
        self.query = query


@dataclass
class CursorStatement(ASTNode):
    """Cursor operation (OPEN, FETCH, CLOSE)"""
    operation: str  # 'open', 'fetch', 'close'
    cursor_name: str
    into_variables: List[str] = None

    def __init__(self, operation, cursor_name, into_variables=None):
        super().__init__('cursor_statement')
        self.operation = operation
        self.cursor_name = cursor_name
        self.into_variables = into_variables or []


@dataclass
class CursorForLoop(ASTNode):
    """Cursor FOR loop"""
    record_name: str
    cursor_name: str
    cursor_query: str = None  # For inline cursor queries
    statements: List['Statement'] = None

    def __init__(self, record_name, cursor_name, cursor_query=None, statements=None):
        super().__init__('cursor_for_loop')
        self.record_name = record_name
        self.cursor_name = cursor_name
        self.cursor_query = cursor_query
        self.statements = statements or []


@dataclass
class Parameter(ASTNode):
    """Procedure/Function parameter"""
    param_name: str
    param_mode: str  # 'IN', 'OUT', 'IN OUT'
    param_type: str
    default_value: Any = None

    def __init__(self, param_name, param_mode, param_type, default_value=None):
        super().__init__('parameter')
        self.param_name = param_name
        self.param_mode = param_mode
        self.param_type = param_type
        self.default_value = default_value


@dataclass
class ProcedureDefinition(ASTNode):
    """CREATE PROCEDURE definition"""
    proc_name: str
    parameters: List[Parameter]
    declarations: List['Declaration']
    statements: List['Statement']
    exception_handlers: List['ExceptionHandler'] = None

    def __init__(self, proc_name, parameters, declarations, statements, exception_handlers=None):
        super().__init__('procedure_definition')
        self.proc_name = proc_name
        self.parameters = parameters or []
        self.declarations = declarations or []
        self.statements = statements or []
        self.exception_handlers = exception_handlers or []


@dataclass
class FunctionDefinition(ASTNode):
    """CREATE FUNCTION definition"""
    func_name: str
    parameters: List[Parameter]
    return_type: str
    declarations: List['Declaration']
    statements: List['Statement']
    exception_handlers: List['ExceptionHandler'] = None
    is_pipelined: bool = False

    def __init__(self, func_name, parameters, return_type, declarations, statements, exception_handlers=None, is_pipelined=False):
        super().__init__('function_definition')
        self.func_name = func_name
        self.parameters = parameters or []
        self.return_type = return_type
        self.declarations = declarations or []
        self.statements = statements or []
        self.exception_handlers = exception_handlers or []
        self.is_pipelined = is_pipelined


@dataclass
class CallStatement(ASTNode):
    """Procedure call"""
    proc_name: str
    arguments: List[str]

    def __init__(self, proc_name, arguments):
        super().__init__('call_statement')
        self.proc_name = proc_name
        self.arguments = arguments or []


@dataclass
class ReturnStatement(ASTNode):
    """RETURN statement for functions"""
    expression: str

    def __init__(self, expression):
        super().__init__('return_statement')
        self.expression = expression


@dataclass
class PackageSpecification(ASTNode):
    """CREATE PACKAGE specification"""
    package_name: str
    declarations: List  # Can include procedure/function signatures, variables, constants

    def __init__(self, package_name, declarations):
        super().__init__('package_specification')
        self.package_name = package_name
        self.declarations = declarations or []


@dataclass
class PackageBody(ASTNode):
    """CREATE PACKAGE BODY implementation"""
    package_name: str
    declarations: List  # Private variables, local procedures/functions
    procedures: List[ProcedureDefinition]
    functions: List[FunctionDefinition]
    initialization: List  # Initialization block statements

    def __init__(self, package_name, declarations, procedures, functions, initialization=None):
        super().__init__('package_body')
        self.package_name = package_name
        self.declarations = declarations or []
        self.procedures = procedures or []
        self.functions = functions or []
        self.initialization = initialization or []


@dataclass
class ProcedureSignature(ASTNode):
    """Procedure signature (for package spec)"""
    proc_name: str
    parameters: List[Parameter]

    def __init__(self, proc_name, parameters):
        super().__init__('procedure_signature')
        self.proc_name = proc_name
        self.parameters = parameters or []


@dataclass
class FunctionSignature(ASTNode):
    """Function signature (for package spec)"""
    func_name: str
    parameters: List[Parameter]
    return_type: str

    def __init__(self, func_name, parameters, return_type):
        super().__init__('function_signature')
        self.func_name = func_name
        self.parameters = parameters or []
        self.return_type = return_type


@dataclass
class RecordTypeDeclaration(ASTNode):
    """TYPE...IS RECORD declaration"""
    type_name: str
    fields: List['RecordField']

    def __init__(self, type_name, fields):
        super().__init__('record_type_declaration')
        self.type_name = type_name
        self.fields = fields or []


@dataclass
class RecordField(ASTNode):
    """Field in a RECORD type"""
    field_name: str
    field_type: str
    default_value: Any = None

    def __init__(self, field_name, field_type, default_value=None):
        super().__init__('record_field')
        self.field_name = field_name
        self.field_type = field_type
        self.default_value = default_value


@dataclass
class RecordVariableDeclaration(ASTNode):
    """Variable declaration of RECORD type"""
    var_name: str
    record_type: str  # Name of the record type

    def __init__(self, var_name, record_type):
        super().__init__('record_variable_declaration')
        self.var_name = var_name
        self.record_type = record_type


@dataclass
class RecordAccess(ASTNode):
    """Access to record field: record.field"""
    record_name: str
    field_name: str

    def __init__(self, record_name, field_name):
        super().__init__('record_access')
        self.record_name = record_name
        self.field_name = field_name


@dataclass
class RecordAssignment(ASTNode):
    """Assignment to record field: record.field := value"""
    record_name: str
    field_name: str
    expression: Any

    def __init__(self, record_name, field_name, expression):
        super().__init__('record_assignment')
        self.record_name = record_name
        self.field_name = field_name
        self.expression = expression


@dataclass
class CollectionTypeDeclaration(ASTNode):
    """TYPE...IS TABLE OF... or VARRAY declaration"""
    type_name: str
    collection_type: str  # 'ASSOC_ARRAY', 'NESTED_TABLE', 'VARRAY'
    element_type: str
    index_type: str = None  # For associative arrays (INDEX BY type)
    max_size: int = None    # For VARRAYs

    def __init__(self, type_name, collection_type, element_type, index_type=None, max_size=None):
        super().__init__('collection_type_declaration')
        self.type_name = type_name
        self.collection_type = collection_type
        self.element_type = element_type
        self.index_type = index_type
        self.max_size = max_size


@dataclass
class CollectionVariableDeclaration(ASTNode):
    """Variable declaration of collection type"""
    var_name: str
    collection_type: str  # Name of the collection type

    def __init__(self, var_name, collection_type):
        super().__init__('collection_variable_declaration')
        self.var_name = var_name
        self.collection_type = collection_type


@dataclass
class CollectionAccess(ASTNode):
    """Access to collection element: collection(index)"""
    collection_name: str
    index_expression: str

    def __init__(self, collection_name, index_expression):
        super().__init__('collection_access')
        self.collection_name = collection_name
        self.index_expression = index_expression


@dataclass
class CollectionMethod(ASTNode):
    """Collection method call: collection.COUNT, collection.EXISTS(n), etc."""
    collection_name: str
    method_name: str
    arguments: List[str]

    def __init__(self, collection_name, method_name, arguments=None):
        super().__init__('collection_method')
        self.collection_name = collection_name
        self.method_name = method_name
        self.arguments = arguments or []


@dataclass
class TypeAttributeDeclaration(ASTNode):
    """%TYPE or %ROWTYPE declaration"""
    var_name: str
    attribute_type: str  # 'TYPE' or 'ROWTYPE'
    source_name: str     # Table/cursor name or column name

    def __init__(self, var_name, attribute_type, source_name):
        super().__init__('type_attribute_declaration')
        self.var_name = var_name
        self.attribute_type = attribute_type
        self.source_name = source_name


@dataclass
class ExecuteImmediateStatement(ASTNode):
    """EXECUTE IMMEDIATE for dynamic SQL"""
    sql_expression: str  # Expression that evaluates to SQL string
    into_variables: List[str] = None  # For SELECT with INTO
    using_variables: List[str] = None  # Bind variables
    returning_variables: List[str] = None  # For DML with RETURNING

    def __init__(self, sql_expression, into_variables=None, using_variables=None, returning_variables=None):
        super().__init__('execute_immediate')
        self.sql_expression = sql_expression
        self.into_variables = into_variables or []
        self.using_variables = using_variables or []
        self.returning_variables = returning_variables or []


@dataclass
class PragmaStatement(ASTNode):
    """PRAGMA directives (AUTONOMOUS_TRANSACTION, etc.)"""
    pragma_type: str  # 'AUTONOMOUS_TRANSACTION', etc.
    pragma_value: Any = None

    def __init__(self, pragma_type, pragma_value=None):
        super().__init__('pragma')
        self.pragma_type = pragma_type
        self.pragma_value = pragma_value


@dataclass
class PipelineStatement(ASTNode):
    """PIPE ROW statement for pipelined functions"""
    row_expression: Any

    def __init__(self, row_expression):
        super().__init__('pipe_row')
        self.row_expression = row_expression


@dataclass
class BulkCollectStatement(ASTNode):
    """BULK COLLECT INTO for bulk operations"""
    query: str
    collection_name: str
    limit: int = None

    def __init__(self, query, collection_name, limit=None):
        super().__init__('bulk_collect')
        self.query = query
        self.collection_name = collection_name
        self.limit = limit


@dataclass
class ForallStatement(ASTNode):
    """FORALL for bulk DML operations"""
    index_name: str
    lower_bound: str
    upper_bound: str
    dml_statement: Any
    save_exceptions: bool = False

    def __init__(self, index_name, lower_bound, upper_bound, dml_statement, save_exceptions=False):
        super().__init__('forall')
        self.index_name = index_name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.dml_statement = dml_statement
        self.save_exceptions = save_exceptions


class PLSQLParser:
    """
    Parser for PL/SQL code
    Converts PL/SQL text into an Abstract Syntax Tree
    """

    def __init__(self):
        self.tokens = []
        self.current_pos = 0

    def parse(self, plsql_code: str):
        """
        Parse PL/SQL code and return AST

        Args:
            plsql_code: PL/SQL source code

        Returns:
            PLSQLBlock, ProcedureDefinition, or FunctionDefinition AST node
        """
        # Tokenize
        self.tokens = self._tokenize(plsql_code)
        self.current_pos = 0

        # Check if this is CREATE PROCEDURE, CREATE FUNCTION, or CREATE PACKAGE
        if self._peek() and self._peek().upper() == 'CREATE':
            self._consume()  # CREATE

            # Check for OR REPLACE
            or_replace = False
            if self._peek() and self._peek().upper() == 'OR':
                self._consume()  # OR
                self._expect('REPLACE')
                or_replace = True

            next_token = self._peek()
            if next_token and next_token.upper() == 'PACKAGE':
                self._consume()  # PACKAGE
                # Check if BODY
                if self._peek() and self._peek().upper() == 'BODY':
                    self._consume()  # BODY
                    return self._parse_package_body(or_replace)
                else:
                    return self._parse_package_specification(or_replace)
            elif next_token and next_token.upper() == 'PROCEDURE':
                return self._parse_create_procedure()
            elif next_token and next_token.upper() == 'FUNCTION':
                return self._parse_create_function()
            else:
                # Not a procedure, function, or package - put CREATE back by rewinding
                self.current_pos -= 1

        # Parse regular block
        return self._parse_block()

    def _tokenize(self, code: str) -> List[str]:
        """
        Simple tokenizer for PL/SQL

        Splits code into tokens (keywords, identifiers, operators, literals)
        """
        # Remove comments
        code = re.sub(r'--.*?$', '', code, flags=re.MULTILINE)  # Single-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)  # Multi-line comments

        # Token pattern (order matters!)
        token_pattern = r'''
            (?P<string>'(?:''|[^'])*')             | # String literals (supports '' as escaped quote)
            (?P<range_op>\.\.)                     | # Range operator (must come first!)
            (?P<number>\d+\.\d+|\d+)               | # Numbers (int or decimal, no trailing dot)
            (?P<operator>:=|<=|>=|<>|!=|=>|\|\||[+\-*/=<>(),:;.])  | # Operators
            (?P<identifier>[a-zA-Z_][a-zA-Z0-9_]*) | # Identifiers/keywords
            (?P<whitespace>\s+)                      # Whitespace
        '''

        tokens = []
        for match in re.finditer(token_pattern, code, re.VERBOSE | re.IGNORECASE):
            token_type = match.lastgroup
            token_value = match.group()

            # Skip whitespace
            if token_type == 'whitespace':
                continue

            tokens.append(token_value)

        return tokens

    def _peek(self, offset: int = 0) -> Optional[str]:
        """Peek at token without consuming it"""
        pos = self.current_pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def _consume(self) -> Optional[str]:
        """Consume and return current token"""
        if self.current_pos < len(self.tokens):
            token = self.tokens[self.current_pos]
            self.current_pos += 1
            return token
        return None

    def _expect(self, expected: str) -> str:
        """Consume token and verify it matches expected"""
        token = self._consume()
        if token and token.upper() == expected.upper():
            return token
        raise SyntaxError(f"Expected '{expected}', got '{token}'")

    def _parse_block(self) -> PLSQLBlock:
        """Parse DECLARE...BEGIN...END block"""
        declarations = []
        statements = []
        exception_handlers = []

        # Optional DECLARE section
        if self._peek() and self._peek().upper() == 'DECLARE':
            self._consume()  # DECLARE
            declarations = self._parse_declarations()

        # BEGIN section
        self._expect('BEGIN')
        statements = self._parse_statements()

        # Optional EXCEPTION section
        if self._peek() and self._peek().upper() == 'EXCEPTION':
            self._consume()  # EXCEPTION
            exception_handlers = self._parse_exception_handlers()

        # END
        self._expect('END')

        # Optional semicolon
        if self._peek() == ';':
            self._consume()

        # Optional slash
        if self._peek() == '/':
            self._consume()

        return PLSQLBlock(declarations, statements, exception_handlers)

    def _parse_declarations(self) -> List[Declaration]:
        """Parse variable declarations and cursor declarations"""
        declarations = []

        while self._peek() and self._peek().upper() not in ('BEGIN', 'END'):
            token_upper = self._peek().upper()

            # Check if this is a TYPE declaration
            if token_upper == 'TYPE':
                decl = self._parse_type_declaration()
            # Check if this is a cursor declaration
            elif token_upper == 'CURSOR':
                decl = self._parse_cursor_declaration()
            else:
                decl = self._parse_declaration()

            if decl:
                declarations.append(decl)

        return declarations

    def _parse_declaration(self) -> Optional[Declaration]:
        """Parse single variable declaration"""
        var_name = self._consume()
        if not var_name:
            return None

        # Check for CONSTANT keyword
        is_constant = False
        if self._peek() and self._peek().upper() == 'CONSTANT':
            self._consume()
            is_constant = True

        # Type - could be a simple type, %TYPE, %ROWTYPE, or a record type
        var_type = self._consume()

        # Check for %ROWTYPE or %TYPE attribute
        if self._peek() and self._peek() == '%':
            self._consume()  # %
            attribute = self._consume().upper()  # TYPE or ROWTYPE

            # Semicolon
            if self._peek() == ';':
                self._consume()

            # Return TypeAttributeDeclaration instead of regular Declaration
            return TypeAttributeDeclaration(var_name, attribute, var_type)

        # Optional initial value
        initial_value = None
        if self._peek() == ':=':
            self._consume()  # :=
            initial_value = self._parse_expression_until(';')

        # Semicolon
        if self._peek() == ';':
            self._consume()

        return Declaration(var_name, var_type, initial_value, is_constant)

    def _parse_cursor_declaration(self) -> CursorDeclaration:
        """Parse cursor declaration: CURSOR cursor_name IS SELECT ..."""
        self._expect('CURSOR')
        cursor_name = self._consume()
        self._expect('IS')

        # Parse SELECT query
        query_parts = []
        while self._peek() and self._peek() != ';':
            query_parts.append(self._consume())

        if self._peek() == ';':
            self._consume()

        query = ' '.join(query_parts)
        return CursorDeclaration(cursor_name, query)

    def _parse_type_declaration(self):
        """Parse TYPE declaration - RECORD, TABLE OF, VARRAY"""
        self._expect('TYPE')
        type_name = self._consume()

        # IS or AS
        if self._peek() and self._peek().upper() in ('IS', 'AS'):
            self._consume()
        else:
            raise SyntaxError(f"Expected IS or AS after TYPE {type_name}")

        next_token = self._peek().upper()

        # TYPE ... IS RECORD
        if next_token == 'RECORD':
            return self._parse_record_type(type_name)

        # TYPE ... IS TABLE OF
        elif next_token == 'TABLE':
            self._consume()  # TABLE
            self._expect('OF')
            return self._parse_collection_type(type_name, 'TABLE')

        # TYPE ... IS VARRAY
        elif next_token == 'VARRAY':
            self._consume()  # VARRAY
            return self._parse_varray_type(type_name)

        else:
            raise SyntaxError(f"Unexpected token after TYPE {type_name} IS: {next_token}")

    def _parse_record_type(self, type_name: str) -> RecordTypeDeclaration:
        """Parse RECORD type definition"""
        self._expect('RECORD')

        # Expect (
        if self._peek() != '(':
            raise SyntaxError(f"Expected '(' after RECORD in TYPE {type_name}")
        self._consume()  # (

        fields = []

        # Parse fields
        while self._peek() and self._peek() != ')':
            field_name = self._consume()

            # Field type
            field_type = self._consume()

            # Optional default value
            default_value = None
            if self._peek() and self._peek() == ':=':
                self._consume()  # :=
                # Parse until comma or )
                default_parts = []
                while self._peek() and self._peek() not in (',', ')'):
                    default_parts.append(self._consume())
                default_value = ' '.join(default_parts)

            fields.append(RecordField(field_name, field_type, default_value))

            # Comma between fields
            if self._peek() == ',':
                self._consume()

        # Expect )
        if self._peek() == ')':
            self._consume()

        # Semicolon
        if self._peek() == ';':
            self._consume()

        return RecordTypeDeclaration(type_name, fields)

    def _parse_collection_type(self, type_name: str, collection_keyword: str) -> CollectionTypeDeclaration:
        """Parse TABLE OF (associative array or nested table)"""
        # Element type
        element_type = self._consume()

        # Check for INDEX BY (associative array)
        index_type = None
        collection_type = 'NESTED_TABLE'

        if self._peek() and self._peek().upper() == 'INDEX':
            self._consume()  # INDEX
            self._expect('BY')
            index_type = self._consume()  # BINARY_INTEGER, VARCHAR2, etc.
            collection_type = 'ASSOC_ARRAY'

        # Semicolon
        if self._peek() == ';':
            self._consume()

        return CollectionTypeDeclaration(type_name, collection_type, element_type, index_type)

    def _parse_varray_type(self, type_name: str) -> CollectionTypeDeclaration:
        """Parse VARRAY type definition"""
        # Expect (size)
        if self._peek() != '(':
            raise SyntaxError(f"Expected '(' after VARRAY in TYPE {type_name}")
        self._consume()  # (

        # Max size
        max_size = int(self._consume())

        # Expect )
        if self._peek() == ')':
            self._consume()

        # OF
        self._expect('OF')

        # Element type
        element_type = self._consume()

        # Semicolon
        if self._peek() == ';':
            self._consume()

        return CollectionTypeDeclaration(type_name, 'VARRAY', element_type, max_size=max_size)

    def _parse_statements(self) -> List[Any]:
        """Parse statements until END or EXCEPTION"""
        statements = []

        while self._peek() and self._peek().upper() not in ('END', 'EXCEPTION', 'ELSIF', 'ELSE'):
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        return statements

    def _parse_statement(self) -> Optional[ASTNode]:
        """Parse single statement"""
        token = self._peek()
        if not token:
            return None

        token_upper = token.upper()

        # IF statement
        if token_upper == 'IF':
            return self._parse_if_statement()

        # LOOP statement
        if token_upper == 'LOOP':
            return self._parse_basic_loop()

        # WHILE loop
        if token_upper == 'WHILE':
            return self._parse_while_loop()

        # FOR loop (check if it's a cursor FOR loop or regular FOR loop)
        if token_upper == 'FOR':
            # Look ahead to see if this is a cursor FOR loop
            # FOR record_name IN cursor_name LOOP or FOR record_name IN (SELECT...) LOOP
            if self._is_cursor_for_loop():
                return self._parse_cursor_for_loop()
            else:
                return self._parse_for_loop()

        # Cursor operations: OPEN, FETCH, CLOSE
        if token_upper in ('OPEN', 'FETCH', 'CLOSE'):
            return self._parse_cursor_statement()

        # EXIT statement
        if token_upper == 'EXIT':
            return self._parse_exit_statement()

        # DBMS_OUTPUT.PUT_LINE
        if token_upper == 'DBMS_OUTPUT':
            return self._parse_output_statement()

        # SELECT statement
        if token_upper == 'SELECT':
            return self._parse_select_into()

        # INSERT/UPDATE/DELETE
        if token_upper in ('INSERT', 'UPDATE', 'DELETE'):
            return self._parse_dml_statement()

        # Nested BEGIN...END block
        if token_upper == 'BEGIN':
            return self._parse_block()

        # CALL statement
        if token_upper == 'CALL':
            return self._parse_call_statement()

        # RETURN statement
        if token_upper == 'RETURN':
            return self._parse_return_statement()

        # EXECUTE IMMEDIATE (Dynamic SQL)
        if token_upper == 'EXECUTE':
            return self._parse_execute_immediate()

        # PRAGMA statement
        if token_upper == 'PRAGMA':
            return self._parse_pragma()

        # PIPE ROW (for pipelined functions)
        if token_upper == 'PIPE':
            return self._parse_pipe_row()

        # FORALL (bulk DML)
        if token_upper == 'FORALL':
            return self._parse_forall()

        # Assignment or procedure call
        # Look ahead for :=
        if self._peek(1) == ':=':
            return self._parse_assignment()

        # Check for record.field := value or collection(index) := value
        if self._peek(1) == '.':
            # Could be record.field := value or collection.method
            # Look ahead further
            if self._peek(3) == ':=':
                # It's record.field := value
                return self._parse_record_assignment()
            else:
                # It's a method call or qualified procedure
                return self._parse_call_statement()

        # Check if it's a direct procedure call (without CALL keyword)
        # or collection element assignment: collection(index) := value
        if self._peek(1) == '(':
            # Look ahead to see if this is collection(index) := value
            # We need to find the matching ) and check if := follows
            # Simple heuristic: if we see ) := it's collection assignment
            saved_pos = self.current_pos
            self._consume()  # identifier
            self._consume()  # (

            # Skip to matching )
            paren_depth = 1
            while self._peek() and paren_depth > 0:
                if self._peek() == '(':
                    paren_depth += 1
                elif self._peek() == ')':
                    paren_depth -= 1
                self._consume()

            # Now check if := follows
            is_collection_assignment = (self._peek() == ':=')

            # Restore position
            self.current_pos = saved_pos

            if is_collection_assignment:
                return self._parse_collection_assignment()
            else:
                return self._parse_call_statement()

        # Skip unknown statements for now
        # Consume until semicolon
        while self._peek() and self._peek() != ';':
            self._consume()
        if self._peek() == ';':
            self._consume()

        return None

    def _parse_if_statement(self) -> IfStatement:
        """Parse IF-THEN-ELSIF-ELSE-END IF"""
        self._expect('IF')

        # Condition
        condition = self._parse_expression_until('THEN')
        self._expect('THEN')

        # THEN statements
        then_statements = []
        while self._peek() and self._peek().upper() not in ('ELSIF', 'ELSE', 'END'):
            stmt = self._parse_statement()
            if stmt:
                then_statements.append(stmt)

        # ELSIF clauses
        elsif_clauses = []
        while self._peek() and self._peek().upper() == 'ELSIF':
            self._consume()  # ELSIF
            elsif_condition = self._parse_expression_until('THEN')
            self._expect('THEN')

            elsif_statements = []
            while self._peek() and self._peek().upper() not in ('ELSIF', 'ELSE', 'END'):
                stmt = self._parse_statement()
                if stmt:
                    elsif_statements.append(stmt)

            elsif_clauses.append((elsif_condition, elsif_statements))

        # ELSE clause
        else_statements = []
        if self._peek() and self._peek().upper() == 'ELSE':
            self._consume()  # ELSE
            while self._peek() and self._peek().upper() != 'END':
                stmt = self._parse_statement()
                if stmt:
                    else_statements.append(stmt)

        # END IF
        self._expect('END')
        self._expect('IF')
        if self._peek() == ';':
            self._consume()

        return IfStatement(condition, then_statements, elsif_clauses, else_statements)

    def _parse_basic_loop(self) -> LoopStatement:
        """Parse LOOP...END LOOP"""
        self._expect('LOOP')

        statements = []
        while self._peek() and self._peek().upper() != 'END':
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        self._expect('END')
        self._expect('LOOP')
        if self._peek() == ';':
            self._consume()

        return LoopStatement('basic', statements=statements)

    def _parse_while_loop(self) -> LoopStatement:
        """Parse WHILE condition LOOP...END LOOP"""
        self._expect('WHILE')

        condition = self._parse_expression_until('LOOP')
        self._expect('LOOP')

        statements = []
        while self._peek() and self._peek().upper() != 'END':
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        self._expect('END')
        self._expect('LOOP')
        if self._peek() == ';':
            self._consume()

        return LoopStatement('while', condition=condition, statements=statements)

    def _parse_for_loop(self) -> LoopStatement:
        """Parse FOR i IN start..end LOOP...END LOOP"""
        self._expect('FOR')

        iterator = self._consume()  # Variable name
        self._expect('IN')

        # Range start (can be number or expression)
        range_start = self._consume()
        self._expect('..')

        # Range end (can be number, variable, or expression like v_numbers.COUNT)
        # Parse until we hit LOOP keyword
        range_end_tokens = []
        while self._peek() and self._peek().upper() != 'LOOP':
            range_end_tokens.append(self._consume())

        # Reconstruct range end expression
        range_end = ' '.join(range_end_tokens) if range_end_tokens else '1'

        self._expect('LOOP')

        statements = []
        while self._peek() and self._peek().upper() != 'END':
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        self._expect('END')
        self._expect('LOOP')
        if self._peek() == ';':
            self._consume()

        return LoopStatement('for', iterator=iterator, range_start=range_start,
                           range_end=range_end, statements=statements)

    def _parse_exit_statement(self) -> ExitStatement:
        """Parse EXIT or EXIT WHEN"""
        self._expect('EXIT')

        condition = None
        if self._peek() and self._peek().upper() == 'WHEN':
            self._consume()  # WHEN
            condition = self._parse_expression_until(';')

        if self._peek() == ';':
            self._consume()

        return ExitStatement(condition)

    def _parse_assignment(self) -> Assignment:
        """Parse variable := expression"""
        var_name = self._consume()
        self._expect(':=')
        expression = self._parse_expression_until(';')

        if self._peek() == ';':
            self._consume()

        return Assignment(var_name, expression)

    def _parse_record_assignment(self) -> RecordAssignment:
        """Parse record.field := expression"""
        record_name = self._consume()
        self._expect('.')
        field_name = self._consume()
        self._expect(':=')
        expression = self._parse_expression_until(';')

        if self._peek() == ';':
            self._consume()

        return RecordAssignment(record_name, field_name, expression)

    def _parse_collection_assignment(self):
        """Parse collection(index) := expression"""
        collection_name = self._consume()
        self._expect('(')

        # Parse index expression (until matching ))
        index_parts = []
        paren_depth = 1
        while self._peek() and paren_depth > 0:
            token = self._peek()
            if token == '(':
                paren_depth += 1
                index_parts.append(self._consume())
            elif token == ')':
                paren_depth -= 1
                if paren_depth > 0:
                    index_parts.append(self._consume())
                else:
                    self._consume()  # consume the final )
            else:
                index_parts.append(self._consume())

        index_expression = ' '.join(index_parts)

        self._expect(':=')
        value_expression = self._parse_expression_until(';')

        if self._peek() == ';':
            self._consume()

        # Create a CollectionAssignment node (we need to add this AST node)
        # For now, return a special Assignment with collection syntax
        from .parser import Assignment
        return Assignment(f"{collection_name}({index_expression})", value_expression)

    def _parse_output_statement(self) -> OutputStatement:
        """Parse DBMS_OUTPUT.PUT_LINE(...)"""
        self._expect('DBMS_OUTPUT')
        self._expect('.')
        self._expect('PUT_LINE')
        self._expect('(')

        expression = self._parse_expression_until(')')
        self._expect(')')

        if self._peek() == ';':
            self._consume()

        return OutputStatement(expression)

    def _parse_select_into(self):
        """Parse SELECT...INTO or SELECT...BULK COLLECT INTO statement"""
        sql_parts = []
        into_variables = []
        is_bulk_collect = False
        limit_value = None

        # Collect SELECT clause up to BULK or INTO
        while self._peek() and self._peek().upper() not in ('BULK', 'INTO'):
            sql_parts.append(self._consume())

        # Check for BULK COLLECT
        if self._peek() and self._peek().upper() == 'BULK':
            self._consume()  # BULK
            self._expect('COLLECT')
            is_bulk_collect = True

        # INTO clause
        if self._peek() and self._peek().upper() == 'INTO':
            self._consume()  # INTO

            # Variables (comma-separated)
            while self._peek() and self._peek().upper() not in ('FROM', 'WHERE', 'LIMIT', ';'):
                var = self._consume()
                if var != ',':
                    into_variables.append(var)

        # Rest of SELECT (FROM, WHERE clauses)
        while self._peek() and self._peek().upper() not in ('LIMIT', ';'):
            sql_parts.append(self._consume())

        # LIMIT clause (for BULK COLLECT)
        if self._peek() and self._peek().upper() == 'LIMIT':
            self._consume()  # LIMIT
            limit_value = self._consume()

        if self._peek() == ';':
            self._consume()

        sql_text = ' '.join(sql_parts)

        # Return appropriate statement type
        if is_bulk_collect:
            # For BULK COLLECT, return a BulkCollectStatement
            # We'll need to handle this in execution
            # LIMIT can be a literal number OR a variable (e.g., p_limit, v_count)
            # Try to convert to int if it's a literal, otherwise keep as variable name
            limit_parsed = None
            if limit_value:
                try:
                    limit_parsed = int(limit_value)
                except ValueError:
                    # It's a variable name, keep as string for runtime evaluation
                    limit_parsed = limit_value

            stmt = BulkCollectStatement(
                query=sql_text,
                collection_name=into_variables[0] if into_variables else None,
                limit=limit_parsed
            )
            return stmt
        else:
            # Regular SELECT INTO
            return SQLStatement('select_into', sql_text, into_variables)

    def _parse_dml_statement(self) -> SQLStatement:
        """Parse INSERT/UPDATE/DELETE statement"""
        sql_type = self._consume().lower()  # INSERT, UPDATE, or DELETE
        sql_parts = [sql_type]

        # Collect until semicolon
        while self._peek() and self._peek() != ';':
            sql_parts.append(self._consume())

        if self._peek() == ';':
            self._consume()

        sql_text = ' '.join(sql_parts)
        return SQLStatement(sql_type, sql_text)

    def _parse_exception_handlers(self) -> List[ExceptionHandler]:
        """Parse exception handlers"""
        handlers = []

        while self._peek() and self._peek().upper() == 'WHEN':
            self._consume()  # WHEN

            exception_name = self._consume()
            self._expect('THEN')

            statements = []
            while self._peek() and self._peek().upper() not in ('WHEN', 'END'):
                stmt = self._parse_statement()
                if stmt:
                    statements.append(stmt)

            handlers.append(ExceptionHandler(exception_name, statements))

        return handlers

    def _parse_expression_until(self, *terminators) -> str:
        """Parse expression until one of the terminators"""
        parts = []
        terminators_upper = [t.upper() for t in terminators]

        while self._peek():
            token = self._peek()
            if token.upper() in terminators_upper or token in terminators:
                break
            parts.append(self._consume())

        return ' '.join(parts)

    def _is_cursor_for_loop(self) -> bool:
        """Check if FOR loop is a cursor FOR loop"""
        # Save position
        saved_pos = self.current_pos

        try:
            # FOR
            if not self._peek() or self._peek().upper() != 'FOR':
                return False
            self._consume()

            # record_name
            record_name = self._consume()
            if not record_name:
                return False

            # IN
            if not self._peek() or self._peek().upper() != 'IN':
                return False
            self._consume()

            # Check next token: if it's '(' then it's an inline query, otherwise cursor name
            # Both cases are cursor FOR loops, not numeric range loops
            next_token = self._peek()
            if next_token and (next_token == '(' or next_token.upper() != self._peek(1)):
                # If next is '(' it's inline query: FOR rec IN (SELECT...)
                # If next token is identifier followed by LOOP, it's cursor: FOR rec IN cur_name LOOP
                # If next token is number followed by '..' it's numeric: FOR i IN 1..10 LOOP
                if next_token == '(':
                    return True
                # Check if there's a '..' ahead (numeric range)
                if self._peek(1) == '..':
                    return False
                # Otherwise it's cursor name
                return True

            return False
        finally:
            # Restore position
            self.current_pos = saved_pos

    def _parse_cursor_statement(self):
        """Parse OPEN, FETCH, or CLOSE cursor statement"""
        operation = self._consume().lower()  # OPEN, FETCH, or CLOSE
        cursor_name = self._consume()

        into_variables = []
        is_bulk_collect = False
        limit_value = None

        if operation == 'fetch':
            # Check for BULK COLLECT
            if self._peek() and self._peek().upper() == 'BULK':
                self._consume()  # BULK
                self._expect('COLLECT')
                is_bulk_collect = True

            # FETCH cursor_name [BULK COLLECT] INTO var1, var2, ...
            if self._peek() and self._peek().upper() == 'INTO':
                self._consume()  # INTO

                # Parse variable list
                while self._peek() and self._peek().upper() not in ('LIMIT', ';'):
                    var = self._consume()
                    if var != ',':
                        into_variables.append(var)

            # LIMIT clause (for BULK COLLECT)
            if self._peek() and self._peek().upper() == 'LIMIT':
                self._consume()  # LIMIT
                limit_value = self._consume()

        if self._peek() == ';':
            self._consume()

        # Return appropriate statement type
        if is_bulk_collect:
            # For FETCH BULK COLLECT, create a specialized statement
            # We'll use BulkCollectStatement with cursor info
            stmt = BulkCollectStatement(
                query=f'FETCH {cursor_name}',  # Special query format for cursor fetch
                collection_name=into_variables[0] if into_variables else None,
                limit=int(limit_value) if limit_value else None
            )
            # Add cursor_name as an attribute for execution
            stmt.cursor_name = cursor_name
            stmt.is_cursor_fetch = True
            return stmt
        else:
            return CursorStatement(operation, cursor_name, into_variables)

    def _parse_cursor_for_loop(self) -> CursorForLoop:
        """Parse cursor FOR loop: FOR rec IN cursor_name LOOP or FOR rec IN (SELECT...) LOOP"""
        self._expect('FOR')

        record_name = self._consume()
        self._expect('IN')

        # Check if inline query or cursor name
        cursor_name = None
        cursor_query = None

        if self._peek() == '(':
            # Inline query: FOR rec IN (SELECT ...)
            self._consume()  # (
            query_parts = []
            paren_depth = 1

            while self._peek() and paren_depth > 0:
                token = self._consume()
                if token == '(':
                    paren_depth += 1
                elif token == ')':
                    paren_depth -= 1
                    if paren_depth == 0:
                        break
                query_parts.append(token)

            cursor_query = ' '.join(query_parts)
        else:
            # Cursor name: FOR rec IN cursor_name
            cursor_name = self._consume()

        self._expect('LOOP')

        # Parse loop statements
        statements = []
        while self._peek() and self._peek().upper() != 'END':
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        self._expect('END')
        self._expect('LOOP')
        if self._peek() == ';':
            self._consume()

        return CursorForLoop(record_name, cursor_name, cursor_query, statements)

    def _parse_create_procedure(self) -> ProcedureDefinition:
        """Parse CREATE PROCEDURE statement"""
        self._expect('PROCEDURE')

        # Procedure name
        proc_name = self._consume()

        # Parameters
        parameters = []
        if self._peek() == '(':
            parameters = self._parse_parameters()

        # IS or AS keyword
        if self._peek() and self._peek().upper() in ('IS', 'AS'):
            self._consume()

        # Parse declarations
        declarations = []
        if self._peek() and self._peek().upper() != 'BEGIN':
            declarations = self._parse_declarations()

        # Parse body
        self._expect('BEGIN')
        statements = self._parse_statements()

        # Optional EXCEPTION section
        exception_handlers = []
        if self._peek() and self._peek().upper() == 'EXCEPTION':
            self._consume()  # EXCEPTION
            exception_handlers = self._parse_exception_handlers()

        # END
        self._expect('END')

        # Optional procedure name after END
        if self._peek() and self._peek().upper() == proc_name.upper():
            self._consume()

        # Optional semicolon
        if self._peek() == ';':
            self._consume()

        # Optional slash
        if self._peek() == '/':
            self._consume()

        return ProcedureDefinition(proc_name, parameters, declarations, statements, exception_handlers)

    def _parse_create_function(self) -> FunctionDefinition:
        """Parse CREATE FUNCTION statement"""
        self._expect('FUNCTION')

        # Function name
        func_name = self._consume()

        # Parameters
        parameters = []
        if self._peek() == '(':
            parameters = self._parse_parameters()

        # RETURN type
        self._expect('RETURN')
        return_type = self._consume()

        # IS or AS keyword
        if self._peek() and self._peek().upper() in ('IS', 'AS'):
            self._consume()

        # Parse declarations
        declarations = []
        if self._peek() and self._peek().upper() != 'BEGIN':
            declarations = self._parse_declarations()

        # Parse body
        self._expect('BEGIN')
        statements = self._parse_statements()

        # Optional EXCEPTION section
        exception_handlers = []
        if self._peek() and self._peek().upper() == 'EXCEPTION':
            self._consume()  # EXCEPTION
            exception_handlers = self._parse_exception_handlers()

        # END
        self._expect('END')

        # Optional function name after END
        if self._peek() and self._peek().upper() == func_name.upper():
            self._consume()

        # Optional semicolon
        if self._peek() == ';':
            self._consume()

        # Optional slash
        if self._peek() == '/':
            self._consume()

        return FunctionDefinition(func_name, parameters, return_type, declarations, statements, exception_handlers)

    def _parse_parameters(self) -> List[Parameter]:
        """Parse parameter list: (param1 IN TYPE, param2 OUT TYPE, ...)"""
        self._expect('(')

        parameters = []

        while self._peek() and self._peek() != ')':
            # Parameter name
            param_name = self._consume()

            # Parameter mode (IN, OUT, IN OUT) - default is IN
            param_mode = 'IN'
            if self._peek() and self._peek().upper() in ('IN', 'OUT'):
                mode_token = self._consume().upper()
                if mode_token == 'IN' and self._peek() and self._peek().upper() == 'OUT':
                    self._consume()  # OUT
                    param_mode = 'IN OUT'
                else:
                    param_mode = mode_token

            # Parameter type
            param_type = self._consume()

            # Optional default value
            default_value = None
            if self._peek() and self._peek() in (':=', 'DEFAULT'):
                if self._peek() == 'DEFAULT':
                    self._consume()
                else:
                    self._consume()  # :=
                default_value = self._parse_expression_until(',', ')')

            parameters.append(Parameter(param_name, param_mode, param_type, default_value))

            # Comma between parameters
            if self._peek() == ',':
                self._consume()

        self._expect(')')

        return parameters

    def _parse_call_statement(self) -> CallStatement:
        """Parse CALL proc_name(arg1, arg2, ...) or direct proc_name(arg1, arg2, ...) or package.proc_name(...)"""
        # Optional CALL keyword
        if self._peek() and self._peek().upper() == 'CALL':
            self._consume()

        # Procedure name (may be qualified: package.procedure)
        proc_name = self._consume()

        # Check for qualified name (package.procedure)
        if self._peek() == '.':
            self._consume()  # dot
            proc_name = proc_name + '.' + self._consume()

        # Arguments
        arguments = []
        if self._peek() == '(':
            self._consume()  # (

            while self._peek() and self._peek() != ')':
                arg = self._parse_expression_until(',', ')')
                if arg:
                    arguments.append(arg)

                if self._peek() == ',':
                    self._consume()

            self._expect(')')

        # Semicolon
        if self._peek() == ';':
            self._consume()

        return CallStatement(proc_name, arguments)

    def _parse_return_statement(self) -> ReturnStatement:
        """Parse RETURN expression;"""
        self._expect('RETURN')

        expression = self._parse_expression_until(';')

        if self._peek() == ';':
            self._consume()

        return ReturnStatement(expression)

    def _parse_execute_immediate(self) -> ExecuteImmediateStatement:
        """Parse EXECUTE IMMEDIATE dynamic SQL statement"""
        self._expect('EXECUTE')
        self._expect('IMMEDIATE')

        # Parse the SQL expression (until INTO, USING, RETURNING, or ;)
        sql_parts = []
        while self._peek() and self._peek().upper() not in ('INTO', 'USING', 'RETURNING', ';'):
            sql_parts.append(self._consume())
        sql_expression = ' '.join(sql_parts)

        into_variables = []
        using_variables = []
        returning_variables = []

        # Parse optional INTO clause
        if self._peek() and self._peek().upper() == 'INTO':
            self._consume()  # INTO
            # Parse variable list
            while self._peek() and self._peek() not in (';', ',') and self._peek().upper() not in ('USING', 'RETURNING'):
                into_variables.append(self._consume())
                if self._peek() == ',':
                    self._consume()

        # Parse optional USING clause
        if self._peek() and self._peek().upper() == 'USING':
            self._consume()  # USING
            # Parse variable list
            while self._peek() and self._peek() not in (';',) and self._peek().upper() not in ('RETURNING',):
                using_variables.append(self._consume())
                if self._peek() == ',':
                    self._consume()

        # Parse optional RETURNING clause
        if self._peek() and self._peek().upper() == 'RETURNING':
            self._consume()  # RETURNING
            # Skip INTO keyword if present
            if self._peek() and self._peek().upper() == 'INTO':
                self._consume()
            # Parse variable list
            while self._peek() and self._peek() != ';':
                returning_variables.append(self._consume())
                if self._peek() == ',':
                    self._consume()

        # Semicolon
        if self._peek() == ';':
            self._consume()

        return ExecuteImmediateStatement(sql_expression, into_variables, using_variables, returning_variables)

    def _parse_pragma(self) -> PragmaStatement:
        """Parse PRAGMA statement"""
        self._expect('PRAGMA')
        pragma_type = self._consume().upper()

        pragma_value = None
        # Some pragmas might have values
        if self._peek() == '(':
            self._consume()  # (
            pragma_value = self._consume()
            self._expect(')')

        # Semicolon
        if self._peek() == ';':
            self._consume()

        return PragmaStatement(pragma_type, pragma_value)

    def _parse_pipe_row(self) -> PipelineStatement:
        """Parse PIPE ROW statement"""
        self._expect('PIPE')
        self._expect('ROW')
        self._expect('(')

        # Parse row expression (until matching ))
        row_parts = []
        paren_depth = 1
        while self._peek() and paren_depth > 0:
            token = self._peek()
            if token == '(':
                paren_depth += 1
                row_parts.append(self._consume())
            elif token == ')':
                paren_depth -= 1
                if paren_depth > 0:
                    row_parts.append(self._consume())
                else:
                    self._consume()  # consume final )
            else:
                row_parts.append(self._consume())

        row_expression = ' '.join(row_parts)

        # Semicolon
        if self._peek() == ';':
            self._consume()

        return PipelineStatement(row_expression)

    def _parse_forall(self) -> ForallStatement:
        """Parse FORALL bulk DML statement"""
        self._expect('FORALL')

        # Index variable
        index_name = self._consume()

        # IN
        self._expect('IN')

        # Lower bound (can be a number or expression like v_start)
        lower_bound = self._consume()

        # Handle .. (might be tokenized as '..' or two '.')
        next_token = self._peek()
        if next_token == '..':
            self._consume()
        elif next_token == '.':
            self._consume()
            if self._peek() == '.':
                self._consume()

        # Upper bound (can be a number, variable, or expression like v_numbers.COUNT)
        # Need to parse until we hit SAVE or the DML statement
        upper_bound_tokens = []
        while self._peek() and self._peek().upper() not in ('SAVE', 'INSERT', 'UPDATE', 'DELETE', 'DBMS_OUTPUT'):
            token = self._consume()
            upper_bound_tokens.append(token)
            # Stop if we've consumed enough for an expression
            # Check if next token is SAVE or a DML keyword
            if self._peek() and self._peek().upper() in ('SAVE', 'INSERT', 'UPDATE', 'DELETE', 'DBMS_OUTPUT'):
                break

        # Reconstruct upper bound expression
        upper_bound = ' '.join(upper_bound_tokens) if upper_bound_tokens else '1'

        # Check for SAVE EXCEPTIONS
        save_exceptions = False
        if self._peek() and self._peek().upper() == 'SAVE':
            self._consume()  # SAVE
            self._expect('EXCEPTIONS')
            save_exceptions = True

        # DML statement (INSERT, UPDATE, DELETE)
        dml_statement = self._parse_statement()

        # Update ForallStatement to include save_exceptions
        stmt = ForallStatement(index_name, lower_bound, upper_bound, dml_statement)
        stmt.save_exceptions = save_exceptions
        return stmt

    def _parse_package_specification(self, or_replace=False) -> PackageSpecification:
        """Parse CREATE PACKAGE specification"""
        package_name = self._consume()

        # IS or AS keyword
        if self._peek() and self._peek().upper() in ('IS', 'AS'):
            self._consume()

        declarations = []

        # Parse public declarations
        while self._peek() and self._peek().upper() != 'END':
            token_upper = self._peek().upper()

            if token_upper == 'PROCEDURE':
                declarations.append(self._parse_procedure_signature())
            elif token_upper == 'FUNCTION':
                declarations.append(self._parse_function_signature())
            else:
                # Variable or constant declaration
                decl = self._parse_declaration()
                if decl:
                    declarations.append(decl)

        self._expect('END')

        # Optional package name after END
        if self._peek() and self._peek().upper() == package_name.upper():
            self._consume()

        # Semicolon
        if self._peek() == ';':
            self._consume()

        # Optional slash
        if self._peek() == '/':
            self._consume()

        return PackageSpecification(package_name, declarations)

    def _parse_procedure_signature(self) -> ProcedureSignature:
        """Parse procedure signature (declaration only)"""
        self._expect('PROCEDURE')
        proc_name = self._consume()

        parameters = []
        if self._peek() == '(':
            parameters = self._parse_parameters()

        # Semicolon
        if self._peek() == ';':
            self._consume()

        return ProcedureSignature(proc_name, parameters)

    def _parse_function_signature(self) -> FunctionSignature:
        """Parse function signature (declaration only)"""
        self._expect('FUNCTION')
        func_name = self._consume()

        parameters = []
        if self._peek() == '(':
            parameters = self._parse_parameters()

        self._expect('RETURN')
        return_type = self._consume()

        # Semicolon
        if self._peek() == ';':
            self._consume()

        return FunctionSignature(func_name, parameters, return_type)

    def _parse_package_body(self, or_replace=False) -> PackageBody:
        """Parse CREATE PACKAGE BODY"""
        package_name = self._consume()

        # IS or AS keyword
        if self._peek() and self._peek().upper() in ('IS', 'AS'):
            self._consume()

        declarations = []
        procedures = []
        functions = []
        initialization = []

        # Parse declarations and implementations
        while self._peek() and self._peek().upper() not in ('BEGIN', 'END'):
            token_upper = self._peek().upper()

            if token_upper == 'PROCEDURE':
                # Full procedure implementation
                self._consume()  # PROCEDURE
                proc_name = self._consume()

                parameters = []
                if self._peek() == '(':
                    parameters = self._parse_parameters()

                # IS or AS keyword
                if self._peek() and self._peek().upper() in ('IS', 'AS'):
                    self._consume()

                # Parse procedure body
                decls = []
                if self._peek() and self._peek().upper() != 'BEGIN':
                    decls = self._parse_declarations()

                self._expect('BEGIN')
                stmts = self._parse_statements()

                exc_handlers = []
                if self._peek() and self._peek().upper() == 'EXCEPTION':
                    self._consume()
                    exc_handlers = self._parse_exception_handlers()

                self._expect('END')

                # Optional proc name
                if self._peek() and self._peek().upper() == proc_name.upper():
                    self._consume()

                if self._peek() == ';':
                    self._consume()

                procedures.append(ProcedureDefinition(proc_name, parameters, decls, stmts, exc_handlers))

            elif token_upper == 'FUNCTION':
                # Full function implementation
                self._consume()  # FUNCTION
                func_name = self._consume()

                parameters = []
                if self._peek() == '(':
                    parameters = self._parse_parameters()

                self._expect('RETURN')
                return_type = self._consume()

                # IS or AS keyword
                if self._peek() and self._peek().upper() in ('IS', 'AS'):
                    self._consume()

                # Parse function body
                decls = []
                if self._peek() and self._peek().upper() != 'BEGIN':
                    decls = self._parse_declarations()

                self._expect('BEGIN')
                stmts = self._parse_statements()

                exc_handlers = []
                if self._peek() and self._peek().upper() == 'EXCEPTION':
                    self._consume()
                    exc_handlers = self._parse_exception_handlers()

                self._expect('END')

                # Optional func name
                if self._peek() and self._peek().upper() == func_name.upper():
                    self._consume()

                if self._peek() == ';':
                    self._consume()

                functions.append(FunctionDefinition(func_name, parameters, return_type, decls, stmts, exc_handlers))

            else:
                # Private variable declaration
                decl = self._parse_declaration()
                if decl:
                    declarations.append(decl)

        # Optional initialization block
        if self._peek() and self._peek().upper() == 'BEGIN':
            self._consume()  # BEGIN
            initialization = self._parse_statements()

        self._expect('END')

        # Optional package name
        if self._peek() and self._peek().upper() == package_name.upper():
            self._consume()

        # Semicolon
        if self._peek() == ';':
            self._consume()

        # Optional slash
        if self._peek() == '/':
            self._consume()

        return PackageBody(package_name, declarations, procedures, functions, initialization)
