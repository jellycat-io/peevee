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
)
from lexer import DEDENT, EOF, FLOAT, INDENT, INT, STRING


class Parser:
    def __init__(self, tokens):
        self.current_token_idx = 0
        self.tokens = tokens
        self.current_token = self.tokens[self.current_token_idx]

    def advance(self):
        self.current_token_idx += 1
        if self.current_token_idx < len(self.tokens):
            self.current_token = self.tokens[self.current_token_idx]
        else:
            self.current_token = None

    def expect(self, token_type):
        if self.current_token.type == token_type and not self.is_at_end():
            self.advance()
        else:
            raise SyntaxError(
                f"[{self.current_token.line}:{self.current_token.column}] Expected {token_type}, but got {self.current_token.type}"
            )

    def parse(self):
        return self.parse_program()

    def parse_program(self) -> Program:
        statement_list = self.parse_statement_list()
        # Check for remaining tokens

        if not self.is_at_end():
            raise SyntaxError(
                f"[{self.current_token.line}:{self.current_token.column}] Unexpected token: {self.current_token.type}"
            )

        return Program(statement_list)

    def parse_statement_list(self) -> List[Statement]:
        statement_list = []

        while not self.is_at_end() and self.current_token.type != DEDENT:
            if self.current_token.type == INDENT:
                statement_list.append(self.parse_block_statement())
            else:
                statement_list.append(self.parse_expression_statement())

        return statement_list

    def parse_block_statement(self) -> BlockStatement:
        statement_list = []
        self.expect(INDENT)
        statement_list = self.parse_statement_list()
        self.expect(DEDENT)

        return BlockStatement(statement_list)

    def parse_expression_statement(self) -> ExpressionStatement:
        expression = self.parse_expression()
        return ExpressionStatement(expression)

    def parse_expression(self):
        return self.parse_primary_expression()

    def parse_primary_expression(self) -> PrimaryExpression:
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
        value = int(self.current_token.literal)
        self.expect(INT)
        return IntegerLiteral(value)

    def parse_float_literal(self) -> FloatLiteral:
        value = float(self.current_token.literal)
        self.expect(FLOAT)
        return FloatLiteral(value)

    def parse_string_literal(self) -> StringLiteral:
        value = self.current_token.literal
        self.expect(STRING)
        return StringLiteral(value)

    def is_at_end(self):
        return self.current_token is None or self.current_token.type == EOF
