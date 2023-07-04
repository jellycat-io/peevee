import json
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

from lexer import Lexer
from node import NodeEncoder
from token_parser import Parser

source = """
42
    3.14
    "Hello World"
        "toto"
10
"""

lexer = Lexer(source)
for token in lexer.get_tokens():
    print(token)
parser = Parser(lexer.tokens)
ast = parser.parse()
ast = json.dumps(ast, cls=NodeEncoder, indent=2)

print(highlight(ast, JsonLexer(), TerminalFormatter()))
