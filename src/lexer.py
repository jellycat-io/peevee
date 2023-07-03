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
        self.indent_levels = [0]
        self.tokenize()

    def tokenize(self):
        # Define regular expression patterns for token types
        patterns = [
            (r"^[ \t]+", INDENT),
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

        # Tokenize the source code
        pos = 0
        line = 1
        column = 1

        while pos < len(self.source):
            # Handle line start (indentation)
            if column == 1:
                indent_match = re.match(r"^[ \t]*", self.source[pos:])
                if indent_match:
                    indent = indent_match.group(0)
                    indent_len = len(indent)
                    if indent_len > self.indent_levels[-1]:
                        self.tokens.append(
                            Token(
                                type=INDENT,
                                literal=indent,
                                line=line,
                                column=column,
                            )
                        )
                        self.indent_levels.append(indent_len)
                    elif indent_len < self.indent_levels[-1]:
                        while indent_len < self.indent_levels[-1]:
                            self.indent_levels.pop()
                            self.tokens.append(
                                Token(
                                    type=DEDENT,
                                    literal="",
                                    line=line,
                                    column=column,
                                )
                            )
                    column += indent_len
                    pos += indent_len

            matched = False
            for pattern, token_type in patterns:
                match = re.match(pattern, self.source[pos:])
                if match:
                    lexeme = match.group(0)

                    if token_type == CR:
                        line += 1
                        column = 1
                        pos += 1
                        matched = True
                        break

                    column += len(lexeme)

                    if token_type == IDENT:
                        token_type = lookup_ident(lexeme)

                    # Skip spaces and tabs within a line
                    if lexeme.isspace() and lexeme != "\n":
                        pos += len(lexeme)
                        matched = True
                        break

                    self.tokens.append(
                        Token(
                            type=token_type,
                            literal=lexeme,
                            line=line,
                            column=column,
                        )
                    )
                    pos += len(lexeme)
                    matched = True
                    break

            if not matched and pos < len(self.source):
                # No pattern matched, character is illegal
                print(f"[{line}:{column}] Unexpected token {self.source[pos]}")
                self.tokens.append(
                    Token(
                        type=ILLEGAL,
                        literal=self.source[pos],
                        line=line,
                        column=column,
                    )
                )
                pos += 1
                column += 1

        # Add DEDENT tokens for remaining indent levels
        while len(self.indent_levels) > 1:
            self.indent_levels.pop()
            self.tokens.append(
                Token(
                    type=DEDENT,
                    literal="",
                    line=line,
                    column=column,
                )
            )

        # Append EOF token at the end
        self.tokens.append(
            Token(
                type=EOF,
                literal="",
                line=line,
                column=column,
            )
        )

    def get_tokens(self) -> List[Token]:
        return self.tokens
