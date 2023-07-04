from typing import List

from node import (
    ExpressionStatement,
    FloatLiteral,
    IntegerLiteral,
    PrimaryExpression,
    Program,
    BlockStatement,
    Statement,
    StringLiteral,
    BinaryExpression,
    Expression,
    Literal
)
from lexer import (
    Token,
    DEDENT,
    EOF,
    FLOAT,
    INDENT,
    INT,
    LPAREN,
    MINUS,
    PLUS,
    RPAREN,
    SLASH,
    STAR,
    STRING,
)


class Parser:
    def __init__(self, tokens):
        self.current_token_idx = 0
        self.tokens = tokens
        self.current_token = self.tokens[self.current_token_idx]

    def parse(self):
        return self.parse_program()

    def parse_program(self) -> Program:
        statement_list = self.parse_statement_list(EOF)

        return Program(statement_list)

    def parse_statement_list(self, stop_token_type) -> List[Statement]:
        statement_list = []

        while not self.match(stop_token_type):
            statement_list.append(self.parse_statement())

        return statement_list

    def parse_statement(self):
        if self.match(INDENT):
            return self.parse_block_statement()

        return self.parse_expression_statement()

    def parse_block_statement(self) -> BlockStatement:
        statement_list = []
        self.eat(INDENT)

        if not self.match(DEDENT):
            statement_list = self.parse_statement_list(DEDENT)
        else:
            statement_list = []

        self.eat(DEDENT)

        return BlockStatement(statement_list)

    def parse_expression_statement(self) -> ExpressionStatement:
        expression = self.parse_expression()
        return ExpressionStatement(expression)

    def parse_expression(self) -> Expression:
        return self.parse_additive_expression()

    def parse_grouped_expression(self) -> Expression:
        self.eat(LPAREN)
        expression = self.parse_expression()
        self.eat(RPAREN)

        return expression

    def parse_additive_expression(self) -> BinaryExpression:
        return self.parse_binary_expression(self.parse_multiplicative_expression, PLUS, MINUS)

    def parse_multiplicative_expression(self) -> BinaryExpression:
        return self.parse_binary_expression(self.parse_primary_expression, STAR, SLASH)

    def parse_binary_expression(self, builder, *ops) -> BinaryExpression:
        left = builder()

        for op in ops:
            while self.match(op):
                operator = self.eat(op)
                right = builder()
                left = BinaryExpression(operator.literal, left, right)

        return left

    def parse_primary_expression(self) -> PrimaryExpression:
        if self.match(LPAREN):
            return self.parse_grouped_expression()
        else:
            return self.parse_literal()

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

    def advance(self):
        self.current_token_idx += 1
        if self.current_token_idx < len(self.tokens):
            self.current_token = self.tokens[self.current_token_idx]
        else:
            self.current_token = None

    def eat(self, token_type) -> Token:
        token = self.current_token
        if self.match(token_type):
            self.advance()
        else:
            raise SyntaxError(
                f"[{self.current_token.line}:{self.current_token.column}] Expected {token_type}, but got {self.current_token.type}"
            )

        return token

    def match(self, token_type) -> bool:
        return self.current_token.type == token_type

    def is_at_end(self) -> bool:
        return self.current_token is None or self.current_token.type == EOF
