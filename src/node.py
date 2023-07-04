import json


class Node:
    pass


class NodeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Node):
            return {
                "-__type__": obj.__class__.__name__,
                "-__data__": obj.__dict__,
            }

        return super().default(obj)


class Program(Node):
    def __init__(self, statement_list):
        self.statement_list = statement_list

    def __str__(self):
        return "\n".join(str(statement) for statement in self.statement_list)


class Statement(Node):
    pass


class BlockStatement(Statement):
    def __init__(self, statement_list):
        self.statement_list = statement_list

    def __str__(self):
        return "\n\t".join(str(statement) for statement in self.statement_list)


class ExpressionStatement(Statement):
    def __init__(self, expression):
        self.expression = expression

    def __str__(self):
        return str(self.expression)


class Expression(Node):
    pass


class BinaryExpression(Expression):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def __str__(self):
        return "(" + str(self.left) + self.operator + str(self.right) + ")"


class PrimaryExpression(Expression):
    pass


class Literal(PrimaryExpression):
    pass


class IntegerLiteral(Literal):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class FloatLiteral(Literal):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class StringLiteral(Literal):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value
