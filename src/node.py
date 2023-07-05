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
    <program> ::= statements EOF
    """

    def __init__(self, statements: List["Statement"]):
        self.statements = statements

    def __str__(self):
        return f'Program({", ".join(str(statement) for statement in self.statements)})'


class Statement(Node):
    pass


class BlockStatement(Statement):
    """
    <block_statement> ::= INDENT statements DEDENT
    """

    def __init__(self, statements: List["Statement"]):
        self.statements = statements

    def __str__(self):
        return f'BlockStatement({", ".join(str(statement) for statement in self.statements)})'


class VariableStatement(Statement):
    """
    <variable_statement> ::= LET variable_declaration_list
    """

    def __init__(self, declarations: List["VariableDeclaration"]):
        self.declarations = declarations

    def __str__(self):
        return f'VariableStatement({", ".join(str(declaration) for declaration in self.declarations)})'


class VariableDeclaration(Node):
    """
    <variable_declaration> ::= identifier [ ASSIGN assignment_expression ]
    """

    def __init__(self, identifier: "Identifier", initializer: "Expression" = None):
        self.identifier = identifier
        self.initializer = initializer

    def __str__(self):
        if self.initializer:
            return f'VariableDeclaration({str(self.identifier)}, {str(self.initializer)})'
        else:
            return f'VariableDeclaration({str(self.identifier)})'


class IfStatement(Statement):
    """
    <if_statement> ::= IF expression THEN statement [ ELSE statement ]
    """

    def __init__(self, condition: "Expression", consequent: "Statement", alternate: "Statement" = None):
        self.condition = condition
        self.consequent = consequent
        self.alternate = alternate

    def __str__(self):
        if self.alternate:
            return f'IfStatement({str(self.condition)}, {str(self.consequent)}, {str(self.alternate)})'
        else:
            return f'IfStatement({str(self.condition)}, {str(self.consequent)})'


class ExpressionStatement(Statement):
    """
    <expression_statement> ::= expression
    """

    def __init__(self, expression: "Expression"):
        self.expression = expression

    def __str__(self):
        return f'ExpressionStatement({str(self.expression)})'


class Expression(Node):
    pass


class AssignmentExpression(Expression):
    """
    <assignment_expression> ::= <equality_expression> [ <assignment_operator> <assignment_expression> ]
    """

    def __init__(self, operator: str, left: "Expression", right: "AssignmentExpression"):
        self.operator = operator
        self.left = left
        self.right = right

    def __str__(self):
        return f'AssignmentExpression({self.operator}, {str(self.left)}, {str(self.right)})'


class BinaryExpression(Expression):
    """
    <equality_expression> ::= <relational_expression> <equality_operator> <relational_expression>
    <relational_expression> ::= <additive_expression> <relational_operator> <additive_expression>
    <additive_expression> ::= <multiplicative_expression> <additive_operator> <multiplicative_expression>
    <multiplicative_expression> ::= <primary_expression> <multiplicative_operator> <primary_expression>
    """

    def __init__(self, operator: str, left: "Expression", right: "Expression"):
        self.operator = operator
        self.left = left
        self.right = right

    def __str__(self):
        return f'BinaryExpression({self.operator}, {str(self.left)}, {str(self.right)})'


class PrimaryExpression(Expression):
    """
    <primary_expression> ::= <literal> | <grouped_expression> | <left_hand_side_expression>
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f'PrimaryExpression({str(self.value)})'


class GroupedExpression(Expression):
    """
    <grouped_expression> ::= LPAREN expression RPAREN
    """

    def __init__(self, expression: "Expression"):
        self.expression = expression

    def __str__(self):
        return f'GroupedExpression({str(self.expression)})'


class Literal(Expression):
    pass


class IntegerLiteral(Literal):
    """
    <literal> ::= INT
    """

    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        return f'IntegerLiteral({str(self.value)})'


class FloatLiteral(Literal):
    """
    <literal> ::= FLOAT
    """

    def __init__(self, value: float):
        self.value = value

    def __str__(self):
        return f'FloatLiteral({str(self.value)})'


class StringLiteral(Literal):
    """
    <literal> ::= STRING
    """

    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return f'StringLiteral({str(self.value)})'


class Identifier(Expression):
    """
    <left_hand_side_expression> ::= IDENT
    """

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f'Identifier({str(self.name)})'
