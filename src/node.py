import json
from typing import List


class NodeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Node):
            return {
                "-__type__": obj.__class__.__name__,
                "-__data__": obj.__dict__,
            }

        return super().default(obj)


class Node:
    pass


class Program(Node):
    """
    <program> ::= <statements>
    """

    def __init__(self, statements: List["Statement"]):
        self.statements = statements

    def __str__(self):
        return f'Program({", ".join(str(statement) for statement in self.statements)})'


class Statement(Node):
    pass


class BlockStatement(Statement):
    """
    <block-statement> ::= "INDENT" <statements> "DEDENT"
    """

    def __init__(self, statements: List["Statement"]):
        self.statements = statements

    def __str__(self):
        return f'BlockStatement({", ".join(str(statement) for statement in self.statements)})'


class ExpressionStatement(Statement):
    """
    <expression-statement> ::= <expression>
    """

    def __init__(self, expression: "Expression"):
        self.expression = expression

    def __str__(self):
        return f'ExpressionStatement({str(self.expression)})'


class VariableStatement(Statement):
    """
    <variable-statement> ::= "LET" <variable-declaration-list>
    """

    def __init__(self, declarations: List["VariableDeclaration"]):
        self.declarations = declarations

    def __str__(self):
        return f'VariableStatement({", ".join(str(declaration) for declaration in self.declarations)})'


class Expression(Node):
    pass


class VariableDeclaration(Expression):
    """
    <variable-declaration> ::= <identifier> ["=" <variable-initializer>]
    """

    def __init__(self, identifier: "Identifier", initializer: "Expression"):
        self.identifier = identifier
        self.initializer = initializer

    def __str__(self):
        return f'VariableDeclaration({self.identifier}, {self.initializer})'


class AssignmentExpression(Expression):
    """
    <assignment-expression> ::= <additive-expression> [<assignment-operator> <assignment-expression>]
    """

    def __init__(self, operator: str, identifier: "Identifier", expression: "Expression"):
        self.operator = operator
        self.identifier = identifier
        self.expression = expression

    def __str__(self):
        return f'AssignmentExpression({self.operator}, {self.identifier}, {self.expression})'


class BinaryExpression(Expression):
    """
    <additive-expression> ::= <multiplicative-expression> {("+" | "-") <multiplicative-expression>}
    <multiplicative-expression> ::= <primary-expression> {("*" | "/" | "%") <primary-expression>}
    """

    def __init__(self, operator: str, left: "Expression", right: "Expression"):
        self.operator = operator
        self.left = left
        self.right = right

    def __str__(self):
        return f'BinaryExpression({self.operator}, {str(self.left)}, {str(self.right)})'


class PrimaryExpression(Expression):
    """
    <primary-expression> ::= <literal> | <grouped-expression> | <identifier>
    """
    pass


class GroupedExpression(Expression):
    """
    <grouped-expression> ::= "(" <expression> ")"
    """

    def __init__(self, expression: "Expression"):
        self.expression = expression

    def __str__(self):
        return f'GroupedExpression({str(self.expression)})'


class Literal(Expression):
    """
    <literal> ::= <integer-literal> | <float-literal> | <string-literal>
    """
    pass


class IntegerLiteral(Literal):
    """
    <integer-literal> ::= INT
    """

    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        return f'IntegerLiteral({self.value})'


class FloatLiteral(Literal):
    """
    <float-literal> ::= FLOAT
    """

    def __init__(self, value: float):
        self.value = value

    def __str__(self):
        return f'FloatLiteral({self.value})'


class StringLiteral(Literal):
    """
    <string-literal> ::= STRING
    """

    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return f'StringLiteral("{self.value}")'


class Identifier(Expression):
    """
    <identifier> ::= IDENT
    """

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f'Identifier({self.name})'
