from typing import List
import unittest

from src.lexer import (
    AND,
    ASSIGN,
    BANG,
    COLON,
    COMMA,
    GT_EQ,
    LT_EQ,
    NIL,
    PLUS_ASSIGN,
    MINUS_ASSIGN,
    STAR_ASSIGN,
    SLASH_ASSIGN,
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
    OR,
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
    THEN,
    TRUE,
    Token,
)

from src.node import (
    AssignmentExpression,
    BinaryExpression,
    BlockStatement,
    BoolLiteral,
    Expression,
    ExpressionStatement,
    FloatLiteral,
    Identifier,
    IfStatement,
    IntegerLiteral,
    LogicalExpression,
    NullLiteral,
    Program,
    Statement,
    StringLiteral,
    VariableDeclaration,
    VariableStatement,
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
            "true\\n"
            "false\\n"
            "nil\\n"
        )

        tokens = tokens_from_string(input)
        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = Program(
            [
                make_expression_statement(make_integer_literal(42)),
                make_expression_statement(make_float_literal(3.14)),
                make_expression_statement(make_string_literal("flareon")),
                make_expression_statement(make_bool_literal(True)),
                make_expression_statement(make_bool_literal(False)),
                make_expression_statement(make_null_literal()),
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
            "IDENT=foo + IDENT=bar\\n"
            "IDENT=foo == IDENT=bar\\n"
            "IDENT=foo != IDENT=bar\\n"
            "IDENT=foo is IDENT=bar\\n"
            "IDENT=foo not IDENT=bar\\n"
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
            make_expression_statement(make_binary_expression(
                PLUS,
                make_identifier("foo"),
                make_identifier("bar")
            )),
            make_expression_statement(make_binary_expression(
                EQ,
                make_identifier("foo"),
                make_identifier("bar")
            )),
            make_expression_statement(make_binary_expression(
                NOT_EQ,
                make_identifier("foo"),
                make_identifier("bar")
            )),
            make_expression_statement(make_binary_expression(
                EQ,
                make_identifier("foo"),
                make_identifier("bar")
            )),
            make_expression_statement(make_binary_expression(
                NOT_EQ,
                make_identifier("foo"),
                make_identifier("bar")
            )),
        ])

        self.assertEqual(str(ast), str(expected_ast))

    def test_parse_logical_expression(self):
        input = (
            "INT=5 == INT=5 and INT=5 < INT=10\\n"
            "INT=5 == INT=5 or INT=5 < INT=10\\n"
            "( INT=5 == INT=5 && INT=5 < INT=10 ) and INT=5 > INT=1\\n"
            "( INT=5 == INT=5 and INT=5 < INT=10 ) or INT=5 > INT=1\\n"
            "( INT=5 == INT=5 || INT=5 < INT=10 ) or INT=5 > INT=1\\n"
            "( INT=5 == INT=5 or INT=5 < INT=10 ) and INT=5 > INT=1\\n"
        )

        tokens = tokens_from_string(input)
        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = Program([
            make_expression_statement(make_logical_expression(
                "and",
                make_binary_expression(
                    EQ,
                    make_integer_literal(5),
                    make_integer_literal(5)
                ),
                make_binary_expression(
                    LT,
                    make_integer_literal(5),
                    make_integer_literal(10)
                ),
            )),
            make_expression_statement(make_logical_expression(
                "or",
                make_binary_expression(
                    EQ,
                    make_integer_literal(5),
                    make_integer_literal(5)
                ),
                make_binary_expression(
                    LT,
                    make_integer_literal(5),
                    make_integer_literal(10)
                ),
            )),
            make_expression_statement(make_logical_expression(
                "and",
                make_logical_expression(
                    "and",
                    make_binary_expression(
                        EQ,
                        make_integer_literal(5),
                        make_integer_literal(5)
                    ),
                    make_binary_expression(
                        LT,
                        make_integer_literal(5),
                        make_integer_literal(10)
                    ),
                ),
                make_binary_expression(
                    GT,
                    make_integer_literal(5),
                    make_integer_literal(1)
                ),
            )),
            make_expression_statement(make_logical_expression(
                "or",
                make_logical_expression(
                    "and",
                    make_binary_expression(
                        EQ,
                        make_integer_literal(5),
                        make_integer_literal(5)
                    ),
                    make_binary_expression(
                        LT,
                        make_integer_literal(5),
                        make_integer_literal(10)
                    ),
                ),
                make_binary_expression(
                    GT,
                    make_integer_literal(5),
                    make_integer_literal(1)
                ),
            )),
            make_expression_statement(make_logical_expression(
                "or",
                make_logical_expression(
                    "or",
                    make_binary_expression(
                        EQ,
                        make_integer_literal(5),
                        make_integer_literal(5)
                    ),
                    make_binary_expression(
                        LT,
                        make_integer_literal(5),
                        make_integer_literal(10)
                    ),
                ),
                make_binary_expression(
                    GT,
                    make_integer_literal(5),
                    make_integer_literal(1)
                ),
            )),
            make_expression_statement(make_logical_expression(
                "and",
                make_logical_expression(
                    "or",
                    make_binary_expression(
                        EQ,
                        make_integer_literal(5),
                        make_integer_literal(5)
                    ),
                    make_binary_expression(
                        LT,
                        make_integer_literal(5),
                        make_integer_literal(10)
                    ),
                ),
                make_binary_expression(
                    GT,
                    make_integer_literal(5),
                    make_integer_literal(1)
                ),
            )),
        ])

        self.assertEqual(str(ast), str(expected_ast))

    def test_parse_assignment_expression(self):
        input = (
            "IDENT=foo = STRING=bar\\n"
            "IDENT=foo += STRING=bar\\n"
            "IDENT=foo = IDENT=bar\\n"
            "IDENT=foo = IDENT=bar = IDENT=baz\\n"
            "IDENT=foo = IDENT=bar = STRING=baz\\n"
            "IDENT=foo = INT=40 + INT=2\\n"
        )

        tokens = tokens_from_string(input)
        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = Program([
            make_expression_statement(make_assignment_expression(
                ASSIGN,
                make_identifier("foo"),
                make_string_literal("bar")
            )),
            make_expression_statement(make_assignment_expression(
                PLUS_ASSIGN,
                make_identifier("foo"),
                make_string_literal("bar")
            )),
            make_expression_statement(make_assignment_expression(
                ASSIGN,
                make_identifier("foo"),
                make_identifier("bar")
            )),
            make_expression_statement(make_assignment_expression(
                ASSIGN,
                make_identifier("foo"),
                make_assignment_expression(
                    ASSIGN,
                    make_identifier("bar"),
                    make_identifier("baz")
                )
            )),
            make_expression_statement(make_assignment_expression(
                ASSIGN,
                make_identifier("foo"),
                make_assignment_expression(
                    ASSIGN,
                    make_identifier("bar"),
                    make_string_literal("baz")
                )
            )),
            make_expression_statement(make_assignment_expression(
                ASSIGN,
                make_identifier("foo"),
                make_binary_expression(
                    PLUS,
                    make_integer_literal(40),
                    make_integer_literal(2),
                )
            )),
        ])

        self.assertEqual(str(ast), str(expected_ast))

    def test_parse_variable_declarations(self):
        input = (
            "let IDENT=x = INT=42\\n"
            "let IDENT=foo = IDENT=bar\\n"
            "let IDENT=x , IDENT=y\\n"
            "let IDENT=x , IDENT=y = INT=42\\n"
            "let IDENT=x = INT=40 + INT=2\\n"
            "let IDENT=x = IDENT=y = INT=42\\n"
        )

        tokens = tokens_from_string(input)
        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = Program([
            make_variable_statement([make_variable_declaration(
                make_identifier("x"),
                make_integer_literal(42),
            )]),
            make_variable_statement([make_variable_declaration(
                make_identifier("foo"),
                make_identifier("bar"),
            )]),
            make_variable_statement([
                make_variable_declaration(make_identifier("x"), None),
                make_variable_declaration(make_identifier("y"), None),
            ]),
            make_variable_statement([
                make_variable_declaration(make_identifier("x"), None),
                make_variable_declaration(
                    make_identifier("y"),
                    make_integer_literal(42),
                )
            ]),
            make_variable_statement([make_variable_declaration(
                make_identifier("x"),
                make_binary_expression(
                    PLUS,
                    make_integer_literal(40),
                    make_integer_literal(2),
                )
            )]),
            make_variable_statement([make_variable_declaration(
                make_identifier("x"),
                make_assignment_expression(
                    ASSIGN,
                    make_identifier("y"),
                    make_integer_literal(42),
                )
            )]),
        ])

        self.assertEqual(str(ast), str(expected_ast))

    def test_parse_if_statements(self):
        input = (
            "let IDENT=pokemon\\n"
            "let IDENT=level\\n"
            "let IDENT=evo_cond\\n"
            "if ( IDENT=level >= INT=15 is true ) then\\n"
            "   IDENT=pokemon = STRING=ivysaur\\n"
            "else\\n"
            "   IDENT=pokemon = STRING=bulbasaur\\n"
            "if ( IDENT=eevee != nil ) then\\n"
            "   if ( IDENT=evo_cond == STRING=solar_stone ) then\\n"
            "       IDENT=eevee = STRING=leafeon\\n"
            "   if IDENT=evo_cond == STRING=friendship_plus_exchange then IDENT=eevee = STRING=sylveon\\n"
            "   if ( IDENT=evo_cond == STRING=friendship_at_night ) then IDENT=eevee = STRING=umbreon else IDENT=eevee = STRING=espeon\\n"
            "else IDENT=eevee = STRING=MissingNo\\n"
        )

        tokens = tokens_from_string(input)
        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = Program([
            make_variable_statement([
                make_variable_declaration(make_identifier("pokemon"), None)
            ]),
            make_variable_statement([
                make_variable_declaration(make_identifier("level"), None)
            ]),
            make_variable_statement([
                make_variable_declaration(make_identifier("evo_cond"), None)
            ]),
            make_if_statement(
                make_binary_expression(
                    EQ,
                    make_binary_expression(
                        GT_EQ,
                        make_identifier("level"),
                        make_integer_literal(15)
                    ),
                    make_bool_literal(True),
                ),
                make_block_statement([make_expression_statement(make_assignment_expression(
                    ASSIGN,
                    make_identifier("pokemon"),
                    make_string_literal("ivysaur")
                ))]),
                make_block_statement([make_expression_statement(make_assignment_expression(
                    ASSIGN,
                    make_identifier("pokemon"),
                    make_string_literal("bulbasaur")
                ))]),
            ),
            make_if_statement(
                make_binary_expression(
                    NOT_EQ,
                    make_identifier("eevee"),
                    make_null_literal(),
                ),
                make_block_statement([
                    make_if_statement(
                        make_binary_expression(
                            EQ,
                            make_identifier("evo_cond"),
                            make_string_literal("solar_stone")
                        ),
                        make_block_statement([make_expression_statement(make_assignment_expression(
                            ASSIGN,
                            make_identifier("eevee"),
                            make_string_literal("leafeon")
                        ))]),
                        None
                    ),
                    make_if_statement(
                        make_binary_expression(
                            EQ,
                            make_identifier("evo_cond"),
                            make_string_literal("friendship_plus_exchange")
                        ),
                        make_expression_statement(make_assignment_expression(
                            ASSIGN,
                            make_identifier("eevee"),
                            make_string_literal("sylveon")
                        )),
                        None
                    ),
                    make_if_statement(
                        make_binary_expression(
                            EQ,
                            make_identifier("evo_cond"),
                            make_string_literal("friendship_at_night")
                        ),
                        make_expression_statement(make_assignment_expression(
                            ASSIGN,
                            make_identifier("eevee"),
                            make_string_literal("umbreon")
                        )),
                        make_expression_statement(make_assignment_expression(
                            ASSIGN,
                            make_identifier("eevee"),
                            make_string_literal("espeon")
                        )),
                    ),
                ]),
                make_expression_statement(make_assignment_expression(
                    ASSIGN,
                    make_identifier("eevee"),
                    make_string_literal("MissingNo")
                )),
            ),
        ])

        self.assertEqual(str(ast), str(expected_ast))


def make_block_statement(statements: List[Statement]) -> BlockStatement:
    return BlockStatement(statements)


def make_expression_statement(expression: Expression) -> ExpressionStatement:
    return ExpressionStatement(expression)


def make_variable_statement(declarations: List[VariableDeclaration]) -> VariableStatement:
    return VariableStatement(declarations)


def make_if_statement(condition: Expression, consequent: Statement, alternative: Statement) -> IfStatement:
    return IfStatement(condition, consequent, alternative)


def make_assignment_expression(operator: str, identifier: Identifier, expression: Expression) -> AssignmentExpression:
    return AssignmentExpression(operator, identifier, expression)


def make_variable_declaration(identifier: Identifier, initializer: Expression) -> VariableDeclaration:
    return VariableDeclaration(identifier, initializer)


def make_binary_expression(operator: str, left: Expression, right: Expression) -> BinaryExpression:
    return BinaryExpression(operator, left, right)


def make_logical_expression(operator: str, left: Expression, right: Expression) -> LogicalExpression:
    return LogicalExpression(operator, left, right)


def make_integer_literal(value: int) -> IntegerLiteral:
    return IntegerLiteral(value)


def make_float_literal(value: float) -> FloatLiteral:
    return FloatLiteral(value)


def make_string_literal(value: str) -> StringLiteral:
    return StringLiteral(value)


def make_bool_literal(value: bool) -> BoolLiteral:
    return BoolLiteral(value)


def make_null_literal() -> NullLiteral:
    return NullLiteral()


def make_identifier(name: str) -> Identifier:
    return Identifier(name)


def tokens_from_string(input_string: str) -> List[Token]:
    token_map = {
        "INDENT": INDENT,
        "DEDENT": DEDENT,
        "EOF": EOF,
        "IDENT": IDENT,
        "INT": INT,
        "FLOAT": FLOAT,
        "STRING": STRING,
        "=": ASSIGN,
        "+=": PLUS_ASSIGN,
        "-=": MINUS_ASSIGN,
        "*=": STAR_ASSIGN,
        "/=": SLASH_ASSIGN,
        "+": PLUS,
        "-": MINUS,
        "*": STAR,
        "/": SLASH,
        "%": PERCENT,
        "!": BANG,
        "==": EQ,
        "!=": NOT_EQ,
        "<": LT,
        "<=": LT_EQ,
        ">": GT,
        ">=": GT_EQ,
        "&&": AND,
        "||": OR,
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
        "is": EQ,
        "not": NOT_EQ,
        "and": AND,
        "or": OR,
        "then": THEN,
        "else": ELSE,
        "return": RETURN,
        "nil": NIL,
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
            if len(segment) > 2 and "=" in segment:
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
