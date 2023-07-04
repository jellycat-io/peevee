import unittest

from src.lexer import (
    ASSIGN,
    BANG,
    COLON,
    COMMA,
    COMMENT,
    COMPLEX_ASSIGN,
    CR,
    DEDENT,
    ELSE,
    EOF,
    EQ,
    FALSE,
    FLOAT,
    FUNCTION,
    GT,
    IDENT,
    IF,
    ILLEGAL,
    IMPORT,
    INDENT,
    INT,
    LBRACE,
    LBRACKET,
    LET,
    LPAREN,
    LT,
    MINUS,
    MODULE,
    NOT_EQ,
    NUMBER,
    PERCENT,
    PLUS,
    RBRACE,
    RBRACKET,
    RETURN,
    RPAREN,
    SEMI,
    SLASH,
    STAR,
    STRING,
    TRUE,
    WHITESPACE,
    Lexer,
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
        input = (
            "INT=42\\n"
            "FLOAT=3.14\\n"
            "STRING=flareon\\n"
        )

        tokens = tokens_from_string(input)
        print(tokens)
        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = Program(
            [
                make_expression_statement(make_integer_literal(42)),
                make_expression_statement(make_float_literal(3.14)),
                make_expression_statement(make_string_literal("flareon")),
            ]
        )

        self.assertEqual(str(ast), str(expected_ast))

    def test_parse_block_statement(self):
        input = (
            "INT=42\\n"
            "   FLOAT=3.14\\n"
            "   STRING=flareon\\n"
            "       STRING=leafeon\\n"
            "INT=42"
        )

        tokens = tokens_from_string(input)
        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = Program([
            make_expression_statement(make_integer_literal(42)),
            make_block_statement([
                make_expression_statement(make_float_literal(3.14)),
                make_expression_statement(make_string_literal("flareon")),
                make_block_statement([
                    make_expression_statement(make_string_literal("leafeon")),
                ]),
            ]),
            make_expression_statement(make_integer_literal(42)),
        ])

        self.assertEqual(str(ast), str(expected_ast))

    def test_parse_literal(self):
        input = (
            "INT=42\\n"
            "FLOAT=3.14\\n"
            "STRING=flareon\\n"
        )

        tokens = tokens_from_string(input)
        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = Program(
            [
                make_expression_statement(make_integer_literal(42)),
                make_expression_statement(make_float_literal(3.14)),
                make_expression_statement(make_string_literal("flareon")),
            ]
        )

        self.assertEqual(str(ast), str(expected_ast))

    def test_parse_binary_expression(self):
        input = (
            "INT=5 + INT=5\\n"
            "INT=5 - INT=5\\n"
            "INT=5 * INT=5\\n"
            "INT=5 / INT=5\\n"
            "INT=5 + INT=5 * INT=5\\n"
            "INT=5 * INT=5 + INT=5\\n"
            "INT=5 * ( INT=5 + INT=5 )\\n"
            "INT=5 % INT=5\\n"
        )

        tokens = tokens_from_string(input)
        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = Program([
            make_expression_statement(make_binary_expression(
                PLUS,
                make_integer_literal(5),
                make_integer_literal(5)
            )),
            make_expression_statement(make_binary_expression(
                MINUS,
                make_integer_literal(5),
                make_integer_literal(5)
            )),
            make_expression_statement(make_binary_expression(
                STAR,
                make_integer_literal(5),
                make_integer_literal(5)
            )),
            make_expression_statement(make_binary_expression(
                SLASH,
                make_integer_literal(5),
                make_integer_literal(5)
            )),
            make_expression_statement(make_binary_expression(
                PLUS,
                make_integer_literal(5),
                make_binary_expression(STAR, make_integer_literal(5), make_integer_literal(5))
            )),
            make_expression_statement(make_binary_expression(
                PLUS,
                make_binary_expression(STAR, make_integer_literal(5), make_integer_literal(5)), make_integer_literal(5)
            )),
            make_expression_statement(make_binary_expression(
                STAR,
                make_integer_literal(5),
                make_binary_expression(PLUS, make_integer_literal(5), make_integer_literal(5))
            )),
            make_expression_statement(make_binary_expression(
                PERCENT,
                make_integer_literal(5),
                make_integer_literal(5)
            )),
        ])

        self.assertEqual(str(ast), str(expected_ast))


def make_block_statement(statements):
    return BlockStatement(statements)


def make_expression_statement(expression):
    return ExpressionStatement(expression)


def make_binary_expression(operator, left, right):
    return BinaryExpression(operator, left, right)


def make_integer_literal(value):
    return IntegerLiteral(value)


def make_float_literal(value):
    return FloatLiteral(value)


def make_string_literal(value):
    return StringLiteral(value)


def tokens_from_string(input_string: str):
    token_map = {
        "INDENT": INDENT,
        "DEDENT": DEDENT,
        "EOF": EOF,
        "IDENT": IDENT,
        "INT": INT,
        "FLOAT": FLOAT,
        "STRING": STRING,
        "=": ASSIGN,
        "+=": COMPLEX_ASSIGN,
        "-=": COMPLEX_ASSIGN,
        "*=": COMPLEX_ASSIGN,
        "/=": COMPLEX_ASSIGN,
        "+": PLUS,
        "-": MINUS,
        "*": STAR,
        "/": SLASH,
        "%": PERCENT,
        "!": BANG,
        "==": EQ,
        "!=": NOT_EQ,
        "<": LT,
        ">": GT,
        ",": COMMA,
        ";": SEMI,
        ":": COLON,
        "(": LPAREN,
        ")": RPAREN,
        "{": LBRACE,
        "}": RBRACE,
        "[": LBRACKET,
        "]": RBRACKET,
        "fn": FUNCTION,
        "module": MODULE,
        "import": IMPORT,
        "let": LET,
        "true": TRUE,
        "false": FALSE,
        "if": IF,
        "else": ELSE,
        "return": RETURN,
    }

    tokens = []
    lines = input_string.split("\\n")
    current_line = 1
    indent_levels = [0]  # Stack to keep track of indent levels

    for line in lines:
        # Compute the indentation level of the current line
        indentation = len(line) - len(line.lstrip())
        current_indent_level = indent_levels[-1]

        # If indentation increases, add an INDENT token
        if indentation > current_indent_level:
            tokens.append(Token(type=INDENT, literal='', line=current_line, column=1))
            indent_levels.append(indentation)

        # If indentation decreases, add DEDENT tokens
        while indentation < current_indent_level:
            tokens.append(Token(type=DEDENT, literal='', line=current_line, column=1))
            indent_levels.pop()
            current_indent_level = indent_levels[-1]

        # Tokenize the rest of the line
        current_column = indentation + 1
        segments = line.lstrip().split()
        for segment in segments:
            print(segment)
            if "=" in segment:
                type_str, literal = segment.split("=")
                token_type = token_map[type_str]
            else:
                token_type = token_map[segment]
                literal = segment

            tokens.append(Token(type=token_type, literal=literal, line=current_line, column=current_column))
            current_column += len(segment) + 1
        current_line += 1

    # Add DEDENT tokens for any remaining indentation levels
    while len(indent_levels) > 1:
        tokens.append(Token(type=DEDENT, literal='', line=current_line, column=1))
        indent_levels.pop()

    tokens.append(Token(type=EOF, literal='', line=current_line, column=1))
    return tokens
