import unittest

from src.lexer import (
    DEDENT,
    FLOAT,
    INDENT,
    INT,
    STRING,
    Token,
)

from src.node import (
    ExpressionStatement,
    FloatLiteral,
    IntegerLiteral,
    Program,
    BlockStatement,
    StringLiteral,
)
from src.token_parser import Parser


class ParserTestCase(unittest.TestCase):
    maxDiff = None

    def test_parse_program(self):
        tokens = [
            Token(INT, "42", 1, 1),
            Token(FLOAT, "3.14", 2, 1),
            Token(STRING, "Hello World", 3, 1),
        ]

        parser = Parser(tokens)

        ast = parser.parse()

        expected_ast = Program(
            [
                ExpressionStatement(IntegerLiteral(42)),
                ExpressionStatement(FloatLiteral(3.14)),
                ExpressionStatement(StringLiteral("Hello World")),
            ]
        )

        self.assertEqual(str(ast), str(expected_ast))

    def test_parse_block_statement(self):
        tokens = [
            Token(INT, "42", 1, 1),
            Token(INDENT, "", 2, 1),
            Token(FLOAT, "3.14", 2, 3),
            Token(STRING, "hello", 3, 3),
            Token(INDENT, "", 4, 1),
            Token(STRING, "world", 4, 5),
            Token(DEDENT, "", 5, 1),
            Token(DEDENT, "", 5, 1),
            Token(INT, 10, 5, 1),
        ]

        parser = Parser(tokens)

        ast = parser.parse()

        expected_ast = Program(
            [
                ExpressionStatement(IntegerLiteral(42)),
                BlockStatement(
                    [
                        ExpressionStatement(FloatLiteral(3.14)),
                        ExpressionStatement(StringLiteral("hello")),
                        BlockStatement(
                            [
                                ExpressionStatement(StringLiteral("world")),
                            ]
                        ),
                    ]
                ),
                ExpressionStatement(IntegerLiteral(10)),
            ]
        )

        self.assertEqual(str(ast), str(expected_ast))

    def test_parse_expression_statement(self):
        tokens = [
            Token(INT, "42", 1, 1),
            Token(FLOAT, "3.14", 2, 1),
            Token(STRING, "hello", 3, 1),
        ]

        parser = Parser(tokens)

        ast = parser.parse()

        expected_ast = Program(
            [
                ExpressionStatement(IntegerLiteral(42)),
                ExpressionStatement(FloatLiteral(3.14)),
                ExpressionStatement(StringLiteral("hello")),
            ]
        )

        self.assertEqual(str(ast), str(expected_ast))
