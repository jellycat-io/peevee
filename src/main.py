import json
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

from lexer import Lexer
from node import NodeEncoder
from token_parser import Parser

source = """
let pokemon
let level
let evo_cond

if (level > 16 == true) then
    pokemon = "ivysaur"
else
    pokemon = "bulbasaur"

if eevee != nil then
    if evo_cond == "solar_stone" then
        eevee = "leafeon"
    if evo_cond == "friendship_with_exchange" then eevee = "sylveon"
    if evo_cond == "friendship_at_night" then eevee = "umbreon" else eevee = "espeon"
else eevee = "missingno"
"""

lexer = Lexer(source)
for token in lexer.get_tokens():
    print(token)
parser = Parser(lexer.tokens)
ast = parser.parse()

# print(str(ast))

ast = json.dumps(ast, cls=NodeEncoder, indent=2)
print(highlight(ast, JsonLexer(), TerminalFormatter()))

with open("output.eve.json", "w") as file:
    file.write(ast)
