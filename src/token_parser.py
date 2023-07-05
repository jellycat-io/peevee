from typing import Callable, List

from node import (
    AssignmentExpression,
    BinaryExpression,
    BlockStatement,
    Expression,
    ExpressionStatement,
    FloatLiteral,
    GroupedExpression,
    Identifier,
    IntegerLiteral,
    Literal,
    Node,
    PrimaryExpression,
    Program,
    Statement,
    StringLiteral,
)
from lexer import (
    Token,
    TokenType,
    ASSIGN,
    DEDENT,
    EOF,
    FLOAT,
    IDENT,
    INDENT,
    INT,
    LPAREN,
    MINUS,
    MINUS_ASSIGN,
    PERCENT,
    PLUS,
    PLUS_ASSIGN,
    RPAREN,
    SLASH,
    SLASH_ASSIGN,
    STAR,
    STAR_ASSIGN,
    STRING,
)


class Parser:
    def __init__(self, tokens: List[Token]):
        self.current_token_idx = 0
        self.tokens = tokens
        self.current_token = self.tokens[self.current_token_idx]

    def parse(self):
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
        left = self.parse_additive_expression()

        if not self.is_assignment_operator(self.current_token.type):
            return left

        return AssignmentExpression(
            self.parse_assignment_operator().literal,
            self.check_valid_assignment_target(left),
            self.parse_assignment_expression()
        )

    def parse_additive_expression(self) -> BinaryExpression:
        return self.parse_binary_expression(self.parse_multiplicative_expression, PLUS, MINUS)

    def parse_multiplicative_expression(self) -> BinaryExpression:
        return self.parse_binary_expression(self.parse_primary_expression, STAR, SLASH, PERCENT)

    def parse_binary_expression(self, builder: Callable[[], BinaryExpression], *ops: TokenType) -> BinaryExpression:
        left = builder()

        for op in ops:
            if self.match(op):
                operator = self.eat(op)
                right = builder()
                left = BinaryExpression(operator.literal, left, right)

        return left

    def parse_left_hand_side_expression(self) -> Expression:
        return self.parse_identifier()

    def parse_primary_expression(self) -> PrimaryExpression:
        if self.is_literal(self.current_token.type):
            return self.parse_literal()
        elif self.match(LPAREN):
            return self.parse_grouped_expression()
        else:
            return self.parse_left_hand_side_expression()

    def parse_literal(self) -> Literal:
        if self.current_token.type == INT:
            return self.parse_integer_literal()
        elif self.current_token.type == FLOAT:
            return self.parse_float_literal()
        elif self.current_token.type == STRING:
            return self.parse_string_literal()
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
        return token_type == INT or token_type == FLOAT or token_type == STRING

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

    def match(self, token_type: TokenType) -> bool:
        return self.current_token.type == token_type

    def is_at_end(self) -> bool:
        return self.current_token is None or self.current_token.type == EOF
