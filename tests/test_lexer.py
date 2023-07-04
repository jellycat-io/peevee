import unittest

from src.lexer import Lexer, Token


class LexerTestCase(unittest.TestCase):
    maxDiff = None

    def test_tokenize(self):
        input = """
42
3.14
    "hello"
    42 + 42
        42
42
"""

        lexer = Lexer(input)

        tokens = lexer.get_tokens()

        expected = [
            Token('INT', "42", 2, 1),
            Token('FLOAT', "3.14", 3, 1),
            Token('INDENT', "", 4, 1),
            Token('STRING', '"hello"', 4, 5),
            Token('INT', "42", 5, 5),
            Token('+', "+", 5, 8),
            Token('INT', "42", 5, 10),
            Token('INDENT', "", 6, 1),
            Token('INT', "42", 6, 9),
            Token('DEDENT', "", 7, 1),
            Token('DEDENT', "", 7, 1),
            Token('INT', "42", 7, 1),
            Token('EOF', "", 9, 1),
        ]

        self.assertEqual(tokens, expected)
