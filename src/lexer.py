import re
from typing import List, NamedTuple


class TokenType(str):
    pass


class Token(NamedTuple):
    type: TokenType
    literal: str
    line: int
    column: int


# Define token types
ILLEGAL = TokenType("ILLEGAL")
WHITESPACE = TokenType("WHITESPACE")
COMMENT = TokenType("COMMENT")
CR = TokenType("CR")
INDENT = TokenType("INDENT")
DEDENT = TokenType("DEDENT")
EOF = TokenType("EOF")
IDENT = TokenType("IDENT")
NUMBER = TokenType("NUMBER")
INT = TokenType("INT")
FLOAT = TokenType("FLOAT")
STRING = TokenType("STRING")
ASSIGN = TokenType("=")
PLUS = TokenType("+")
MINUS = TokenType("-")
STAR = TokenType("*")
SLASH = TokenType("/")
PERCENT = TokenType("%")
BANG = TokenType("!")
EQ = TokenType("==")
NOT_EQ = TokenType("!=")
LT = TokenType("<")
GT = TokenType(">")
COMMA = TokenType(",")
SEMI = TokenType(";")
COLON = TokenType(":")
LPAREN = TokenType("(")
RPAREN = TokenType(")")
LBRACE = TokenType("{")
RBRACE = TokenType("}")
LBRACKET = TokenType("[")
RBRACKET = TokenType("]")
FUNCTION = TokenType("FUNCTION")
MODULE = TokenType("MODULE")
IMPORT = TokenType("IMPORT")
LET = TokenType("LET")
TRUE = TokenType("TRUE")
FALSE = TokenType("FALSE")
IF = TokenType("IF")
ELSE = TokenType("ELSE")
RETURN = TokenType("RETURN")

keywords = {
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


def lookup_ident(ident: str) -> TokenType:
    return keywords.get(ident, IDENT)


# Lexer class
# Lazily pulls a token from a stream.
class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        # Stack to keep track of indentation levels
        self.indent_stack = [0]
        self.tokenize()

    def tokenize(self):
        lines = self.source.split("\n")
        for line_num, line in enumerate(lines, start=1):
            column = 1
            indent_level = len(line) - len(line.lstrip())
            indent_string = line[:indent_level]

            if indent_level == self.indent_stack[-1]:
                column += len(indent_string)

            while indent_level < self.indent_stack[-1]:
                self.tokens.append(Token(DEDENT, "", line_num, column))
                self.indent_stack.pop()

            if indent_level > self.indent_stack[-1]:
                self.tokens.append(Token(INDENT, "", line_num, column))
                self.indent_stack.append(indent_level)
                column += len(indent_string)

            self.tokenize_line(line, line_num, column)

        # Add DEDENT tokens for remaining indent levels
        for _ in range(len(self.indent_stack) - 1):
            self.tokens.append(Token(DEDENT, "", len(lines) + 1, 1))

        # Append EOF token at the end
        self.tokens.append(Token(EOF, "", len(lines) + 1, 1))

    def tokenize_line(self, line: str, line_num: int, column: int):
        line = line.lstrip()
        column += len(line) - len(line.lstrip())

        # Define regular expression patterns for token types
        patterns = [
            (r"^[ \t]+", WHITESPACE),
            (r"\#[^\n]*", COMMENT),
            (r"^\n", CR),
            (r"[a-zA-Z_][a-zA-Z0-9_]*", IDENT),
            (r"\d+\.\d+", FLOAT),
            (r"\d+", INT),
            (r"\".*?\"", STRING),
            (r"\=\=", EQ),
            (r"\!\=", NOT_EQ),
            (r"\=", ASSIGN),
            (r"\+", PLUS),
            (r"\-", MINUS),
            (r"\*", STAR),
            (r"\/", SLASH),
            (r"\%", PERCENT),
            (r"\!", BANG),
            (r"\<", LT),
            (r"\>", GT),
            (r"\,", COMMA),
            (r"\;", SEMI),
            (r"\:", COLON),
            (r"\(", LPAREN),
            (r"\)", RPAREN),
            (r"\{", LBRACE),
            (r"\}", RBRACE),
            (r"\[", LBRACKET),
            (r"\]", RBRACKET),
        ]

        while line:
            matched = False
            for pattern, token_type in patterns:
                match = re.match(pattern, line)
                if match:
                    lexeme = match.group(0)

                    if token_type is not WHITESPACE:
                        self.tokens.append(Token(token_type, lexeme, line_num, column))

                    line = line[len(lexeme):]
                    column += len(lexeme)
                    matched = True
                    break

            if not matched:
                self.tokens.append(Token(ILLEGAL, line[0], line_num, column))
                line = line[1:]
                column += 1

        # Decrement the column value for DEDENT tokens
        if self.tokens and self.tokens[-1].type == DEDENT:
            self.tokens[-1] = Token(DEDENT, "", line_num, column - 1)

    def get_tokens(self) -> List[Token]:
        return self.tokens