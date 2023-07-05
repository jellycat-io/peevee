from typing import Callable, List

from node import (
    AssignmentExpression,
    BinaryExpression,
    BlockStatement,
    BoolLiteral,
    Expression,
    ExpressionStatement,
    FloatLiteral,
    GroupedExpression,
    Identifier,
    IfStatement,
    IntegerLiteral,
    Literal,
    LogicalExpression,
    Node,
    NullLiteral,
    PrimaryExpression,
    Program,
    Statement,
    StringLiteral,
    VariableStatement,
    VariableDeclaration,
)
from lexer import (
    Token,
    TokenType,
    AND,
    ASSIGN,
    COMMA,
    DEDENT,
    ELSE,
    EOF,
    EQ,
    FALSE,
    FLOAT,
    GT,
    GT_EQ,
    IDENT,
    IF,
    INDENT,
    INT,
    LET,
    LT,
    LT_EQ,
    LPAREN,
    MINUS,
    MINUS_ASSIGN,
    NIL,
    NOT_EQ,
    OR,
    PERCENT,
    PLUS,
    PLUS_ASSIGN,
    RPAREN,
    SLASH,
    SLASH_ASSIGN,
    STAR,
    STAR_ASSIGN,
    STRING,
    THEN,
    TRUE,
)


class Parser:
    def __init__(self, tokens: List[Token]):
        self.current_token_idx = 0
        self.tokens = tokens
        self.current_token = self.tokens[self.current_token_idx]

    def parse(self):
        if len(self.tokens) == 0:
            return
        return self.parse_program()

    def parse_program(self) -> Program:
        statements = self.parse_statements(EOF)

        return Program(statements)

    def parse_statements(self, stop_token_type: TokenType) -> List[Statement]:
        statements = []

        while not self.match(stop_token_type):
            statements.append(self.parse_statement())

        return statements

    def parse_statement(self):
        if self.match(INDENT):
            return self.parse_block_statement()
        elif self.match(LET):
            return self.parse_variable_statement()
        elif self.match(IF):
            return self.parse_if_statement()

        return self.parse_expression_statement()

    def parse_block_statement(self) -> BlockStatement:
        statements = []
        self.eat(INDENT)

        if not self.match(DEDENT):
            statements = self.parse_statements(DEDENT)
        else:
            statements = []

        self.eat(DEDENT)

        return BlockStatement(statements)

    def parse_variable_statement(self) -> VariableStatement:
        self.eat(LET)

        declarations = self.parse_variable_declaration_list()

        return VariableStatement(declarations)

    def parse_variable_declaration_list(self) -> List[VariableDeclaration]:
        declarations = [self.parse_variable_declaration()]

        while self.match(COMMA) and self.eat(COMMA):
            declarations.append(self.parse_variable_declaration())

        return declarations

    def parse_variable_declaration(self) -> VariableDeclaration:
        identifier = self.parse_identifier()
        initializer = None

        if not self.match(COMMA) and self.match(ASSIGN):
            initializer = self.parse_variable_initializer()

        return VariableDeclaration(identifier, initializer)

    def parse_variable_initializer(self) -> AssignmentExpression:
        self.eat(ASSIGN)
        return self.parse_assignment_expression()

    def parse_if_statement(self) -> IfStatement:
        self.eat(IF)
        condition = self.parse_expression()
        self.eat(THEN)
        consequent = self.parse_statement()
        if self.match(ELSE):
            self.eat(ELSE)
            alternate = self.parse_statement()
        else:
            alternate = None

        return IfStatement(condition, consequent, alternate)

    def parse_expression_statement(self) -> ExpressionStatement:
        expression = self.parse_expression()
        return ExpressionStatement(expression)

    def parse_expression(self) -> Expression:
        return self.parse_assignment_expression()

    def parse_grouped_expression(self) -> GroupedExpression:
        self.eat(LPAREN)
        expression = self.parse_expression()
        self.eat(RPAREN)

        return expression

    def parse_assignment_expression(self) -> AssignmentExpression:
        left = self.parse_logical_or_expression()

        if not self.is_assignment_operator(self.current_token.type):
            return left

        return AssignmentExpression(
            self.parse_assignment_operator().literal,
            self.check_valid_assignment_target(left),
            self.parse_assignment_expression()
        )

    def parse_logical_or_expression(self) -> LogicalExpression:
        return self.parse_logical_expression(self.parse_logical_and_expression, OR)

    def parse_logical_and_expression(self) -> LogicalExpression:
        return self.parse_logical_expression(self.parse_equality_expression, AND)

    def parse_logical_expression(self, builder: Callable[[], LogicalExpression], op: TokenType) -> LogicalExpression:
        left = builder()

        if self.match(op):
            operator_string = self.eat(op).literal
            if operator_string == "&&":
                operator_string = "and"
            if operator_string == "||":
                operator_string = "or"
            right = builder()
            left = LogicalExpression(operator_string, left, right)

        return left

    def parse_equality_expression(self) -> BinaryExpression:
        return self.parse_binary_expression(self.parse_relational_expression, EQ, NOT_EQ)

    def parse_relational_expression(self) -> BinaryExpression:
        return self.parse_binary_expression(self.parse_additive_expression, LT, LT_EQ, GT, GT_EQ)

    def parse_additive_expression(self) -> BinaryExpression:
        return self.parse_binary_expression(self.parse_multiplicative_expression, PLUS, MINUS)

    def parse_multiplicative_expression(self) -> BinaryExpression:
        return self.parse_binary_expression(self.parse_primary_expression, STAR, SLASH, PERCENT)

    def parse_binary_expression(self, builder: Callable[[], BinaryExpression], *ops: TokenType) -> BinaryExpression:
        left = builder()

        for op in ops:
            if self.match(op):
                operator_string = self.eat(op).literal
                if operator_string == "is":
                    operator_string = "=="
                if operator_string == "not":
                    operator_string = "!="
                right = builder()
                left = BinaryExpression(operator_string, left, right)

        return left

    def parse_left_hand_side_expression(self) -> Expression:
        if self.match(IDENT):
            return self.parse_identifier()
        else:
            raise SyntaxError(
                f"[{self.current_token.line}:{self.current_token.column}] Unexpected token: {self.current_token.type}"
            )

    def parse_primary_expression(self) -> PrimaryExpression:
        if self.is_literal(self.current_token.type):
            return self.parse_literal()
        elif self.match(LPAREN):
            return self.parse_grouped_expression()
        else:
            return self.parse_left_hand_side_expression()

    def parse_literal(self) -> Literal:
        if self.match(INT):
            return self.parse_integer_literal()
        elif self.match(FLOAT):
            return self.parse_float_literal()
        elif self.match(STRING):
            return self.parse_string_literal()
        elif self.match(TRUE):
            return self.parse_bool_literal(True)
        elif self.match(FALSE):
            return self.parse_bool_literal(False)
        elif self.match(NIL):
            return self.parse_null_literal()
        else:
            raise SyntaxError(
                f"[{self.current_token.line}:{self.current_token.column}] Unexpected token: {self.current_token.type}"
            )

    def parse_integer_literal(self) -> IntegerLiteral:
        value = self.eat(INT).literal
        return IntegerLiteral(int(value))

    def parse_float_literal(self) -> FloatLiteral:
        value = self.eat(FLOAT).literal
        return FloatLiteral(float(value))

    def parse_string_literal(self) -> StringLiteral:
        value = self.eat(STRING).literal
        return StringLiteral(value)

    def parse_bool_literal(self, value: bool) -> BoolLiteral:
        if value:
            self.eat(TRUE)
        else:
            self.eat(FALSE)

        return BoolLiteral(value)

    def parse_null_literal(self) -> NullLiteral:
        self.eat(NIL)
        return NullLiteral()

    def parse_identifier(self) -> Identifier:
        name = self.eat(IDENT).literal
        return Identifier(name)

    def parse_assignment_operator(self) -> Token:
        if self.match(ASSIGN):
            return self.eat(ASSIGN)

        return self.eat(self.check_complex_assignment_operator())

    def is_assignment_operator(self, token_type: TokenType) -> bool:
        return token_type == ASSIGN or token_type == self.check_complex_assignment_operator()

    def check_complex_assignment_operator(self) -> TokenType:
        if self.match(PLUS_ASSIGN):
            return PLUS_ASSIGN
        elif self.match(MINUS_ASSIGN):
            return MINUS_ASSIGN
        elif self.match(STAR_ASSIGN):
            return STAR_ASSIGN
        elif self.match(SLASH_ASSIGN):
            return SLASH_ASSIGN

    def check_valid_assignment_target(self, node: Node) -> Node:
        if isinstance(node, Identifier):
            return node

        raise SyntaxError(
            f"[{self.current_token.line}:{self.current_token.column}] Invalid left-hand side in assignment expression"
        )

    def is_literal(self, token_type: TokenType) -> bool:
        return token_type == INT or token_type == FLOAT or token_type == STRING or token_type == TRUE or token_type == FALSE or token_type == NIL

    def advance(self):
        self.current_token_idx += 1
        if self.current_token_idx < len(self.tokens):
            self.current_token = self.tokens[self.current_token_idx]
        else:
            self.current_token = None

    def eat(self, token_type: TokenType) -> Token:
        token = self.current_token
        if self.match(token_type):
            self.advance()
        else:
            raise SyntaxError(
                f"[{self.current_token.line}:{self.current_token.column}] Expected {token_type}, but got {self.current_token.type}"
            )

        return token

    def expect(self, token_type: TokenType):
        if not self.match(token_type):
            raise SyntaxError(
                f"[{self.current_token.line}:{self.current_token.column}] Expected {token_type}, but got {self.current_token.type}"
            )

    def match(self, token_type: TokenType) -> bool:
        return self.current_token is not None and self.current_token.type == token_type

    def is_at_end(self) -> bool:
        return self.current_token is None or self.current_token.type == EOF
