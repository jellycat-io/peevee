import json
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

from lexer import Lexer
from node import NodeEncoder
from token_parser import Parser

source = """
foo = "bar"
    3.14 % 2
    "flareon"
        "sylveon"
    "leafeon"
answer = 42
"""

lexer = Lexer(source)
for token in lexer.get_tokens():
    print(token)
parser = Parser(lexer.tokens)
ast = parser.parse()

# print(str(ast))

ast = json.dumps(ast, cls=NodeEncoder, indent=2)
print(highlight(ast, JsonLexer(), TerminalFormatter()))
