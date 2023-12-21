from abc import ABC, abstractmethod
from enum import NAMED_FLAGS
from typing import Any
from plox.token import Token

class ExpressionVisitor(ABC):
    """
    Vistor for the Expression class
    """

    @abstractmethod
    def visit_binary_expr(self, expr):
        raise NotImplementedError

    @abstractmethod
    def visit_grouping_expr(self, expr):
        raise NotImplementedError

    @abstractmethod
    def visit_literal_expr(self, expr):
        raise NotImplementedError

    @abstractmethod
    def visit_unary_expr(self, expr):
        raise NotImplementedError

    @abstractmethod
    def visit_variable_expr(self, expr):
        raise NotImplementedError


class Expression(ABC):
    """
    Abstract Base Class for expressions
    """

    @abstractmethod
    def accept(self, visitor: ExpressionVisitor):
        raise NotImplementedError


class AssignExpr(Expression):
    def __init__(self, name: Token, value: Expression):
        self.name = name
        self.value = value

    def accept(self, visitor: ExpressionVisitor):
        """ Call the visitor """
        return visitor.visit_assign_expr(self)


class BinaryExpr(Expression):
    def __init__(self, left: Expression, operator: Token, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor: ExpressionVisitor):
        """ Call the visitor """
        return visitor.visit_binary_expr(self)


class GroupingExpr(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor: ExpressionVisitor):
        """ Call the visitor """
        return visitor.visit_grouping_expr(self)


class LiteralExpr(Expression):
    def __init__(self, value: Any):
        self.value = value

    def accept(self, visitor: ExpressionVisitor):
        """ Call the visitor """
        return visitor.visit_literal_expr(self)


class UnaryExpr(Expression):
    def __init__(self, operator: Token, right: Expression):
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExpressionVisitor):
        """ Call the visitor """
        return visitor.visit_unary_expr(self)


class VariableExpr(Expression):
    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor: ExpressionVisitor):
        """ Call the visitor """
        return visitor.visit_variable_expr(self)
