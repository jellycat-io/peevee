from lexer import Lexer

source = """
fn function_name:
    if x > 10:
        return true
    return false
"""

lexer = Lexer(source)
for token in lexer.get_tokens():
    print(token)
