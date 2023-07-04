import unittest

from src.lexer import (
    DEDENT,
    EOF,
    FLOAT,
    INDENT,
    INT,
    LPAREN,
    MINUS,
    PERCENT,
    PLUS,
    RPAREN,
    SLASH,
    STAR,
    STRING,
    Token,
)

from src.node import (
    BinaryExpression,
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
            Token(type=INT, literal='42', line=1, column=1),
            Token(type=FLOAT, literal='3.14', line=2, column=1),
            Token(type=STRING, literal='flareon', line=3, column=1),
            Token(type=EOF, literal='', line=4, column=1),
        ]

        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = Program(
            [
                ExpressionStatement(IntegerLiteral(42)),
                ExpressionStatement(FloatLiteral(3.14)),
                ExpressionStatement(StringLiteral("flareon")),
            ]
        )

        self.assertEqual(str(ast), str(expected_ast))

    def test_parse_block_statement(self):
        tokens = [
            Token(type=INT, literal='42', line=2, column=1),
            Token(type=INDENT, literal='', line=3, column=1),
            Token(type=FLOAT, literal='3.14', line=3, column=5),
            Token(type=STRING, literal='flareon', line=4, column=5),
            Token(type=INDENT, literal='', line=5, column=1),
            Token(type=STRING, literal='leafeon', line=5, column=9),
            Token(type=DEDENT, literal='', line=6, column=1),
            Token(type=DEDENT, literal='', line=6, column=1),
            Token(type=INT, literal='42', line=6, column=1),
            Token(type=EOF, literal='', line=7, column=1),
        ]

        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = Program(
            [
                ExpressionStatement(IntegerLiteral(42)),
                BlockStatement(
                    [
                        ExpressionStatement(FloatLiteral(3.14)),
                        ExpressionStatement(StringLiteral("flareon")),
                        BlockStatement(
                            [
                                ExpressionStatement(StringLiteral("leafeon")),
                            ]
                        ),
                    ]
                ),
                ExpressionStatement(IntegerLiteral(42)),
            ]
        )

        self.assertEqual(str(ast), str(expected_ast))

    def test_parse_literal(self):
        tokens = [
            Token(type=INT, literal='42', line=1, column=1),
            Token(type=FLOAT, literal='3.14', line=2, column=1),
            Token(type=STRING, literal='flareon', line=3, column=1),
            Token(type=EOF, literal='', line=4, column=1),
        ]

        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = Program(
            [
                ExpressionStatement(IntegerLiteral(42)),
                ExpressionStatement(FloatLiteral(3.14)),
                ExpressionStatement(StringLiteral("flareon")),
            ]
        )

        self.assertEqual(str(ast), str(expected_ast))

    def test_parse_binary_expression(self):
        tokens = [
            Token(type=INT, literal='5', line=2, column=1),
            Token(type=PLUS, literal='+', line=2, column=3),
            Token(type=INT, literal='5', line=2, column=5),
            Token(type=INT, literal='5', line=3, column=1),
            Token(type=MINUS, literal='-', line=3, column=3),
            Token(type=INT, literal='5', line=3, column=5),
            Token(type=INT, literal='5', line=4, column=1),
            Token(type=STAR, literal='*', line=4, column=3),
            Token(type=INT, literal='5', line=4, column=5),
            Token(type=INT, literal='5', line=5, column=1),
            Token(type=SLASH, literal='/', line=5, column=3),
            Token(type=INT, literal='5', line=5, column=5),
            Token(type=INT, literal='5', line=6, column=1),
            Token(type=PLUS, literal='+', line=6, column=3),
            Token(type=INT, literal='5', line=6, column=5),
            Token(type=STAR, literal='*', line=6, column=7),
            Token(type=INT, literal='5', line=6, column=9),
            Token(type=INT, literal='5', line=7, column=1),
            Token(type=STAR, literal='*', line=7, column=3),
            Token(type=INT, literal='5', line=7, column=5),
            Token(type=PLUS, literal='+', line=7, column=7),
            Token(type=INT, literal='5', line=7, column=9),
            Token(type=LPAREN, literal='(', line=8, column=1),
            Token(type=INT, literal='5', line=8, column=2),
            Token(type=PLUS, literal='+', line=8, column=4),
            Token(type=INT, literal='5', line=8, column=6),
            Token(type=RPAREN, literal=')', line=8, column=7),
            Token(type=STAR, literal='*', line=8, column=9),
            Token(type=INT, literal='5', line=8, column=11),
            Token(type=INT, literal='5', line=9, column=1),
            Token(type=PERCENT, literal='%', line=9, column=3),
            Token(type=INT, literal='5', line=9, column=5),
            Token(type=EOF, literal='', line=10, column=1),
        ]

        parser = Parser(tokens)

        ast = parser.parse()

        expected_ast = Program(
            [
                BinaryExpression(
                    "+",
                    IntegerLiteral(5),
                    IntegerLiteral(5),
                ),
                BinaryExpression(
                    "-",
                    IntegerLiteral(5),
                    IntegerLiteral(5),
                ),
                BinaryExpression(
                    "*",
                    IntegerLiteral(5),
                    IntegerLiteral(5),
                ),
                BinaryExpression(
                    "/",
                    IntegerLiteral(5),
                    IntegerLiteral(5),
                ),
                BinaryExpression(
                    "+",
                    IntegerLiteral(5),
                    BinaryExpression(
                        "*",
                        IntegerLiteral(5),
                        IntegerLiteral(5),
                    ),
                ),
                BinaryExpression(
                    "+",
                    BinaryExpression(
                        "*",
                        IntegerLiteral(5),
                        IntegerLiteral(5),
                    ),
                    IntegerLiteral(5),
                ),
                BinaryExpression(
                    "*",
                    BinaryExpression(
                        "+",
                        IntegerLiteral(5),
                        IntegerLiteral(5),
                    ),
                    IntegerLiteral(5),
                ),
                BinaryExpression(
                    "%",
                    IntegerLiteral(5),
                    IntegerLiteral(5),
                ),
            ]
        )

        self.assertEqual(str(ast), str(expected_ast))
