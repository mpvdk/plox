from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from plox.token import Token

class ExpressionVisitor(ABC):
    """
    Vistor for the Expression class
    """

    @abstractmethod
    def visit_assign_expr(self, assign_expr: AssignExpr):
        raise NotImplementedError

    @abstractmethod
    def visit_binary_expr(self, binary_expr: BinaryExpr):
        raise NotImplementedError

    @abstractmethod
    def visit_call_expr(self, call_expr: CallExpr):
        raise NotImplementedError

    @abstractmethod
    def visit_function_expr(self, function_expr: FunctionExpr):
        raise NotImplementedError

    @abstractmethod
    def visit_grouping_expr(self, grouping_expr: GroupingExpr):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def visit_literal_expr(literal_expr: LiteralExpr):
        raise NotImplementedError

    @abstractmethod
    def visit_logical_expr(self, logical_expr: LogicalExpr):
        raise NotImplementedError

    @abstractmethod
    def visit_unary_expr(self, unary_expr: UnaryExpr):
        raise NotImplementedError

    @abstractmethod
    def visit_variable_expr(self, variable_expr: VariableExpr):
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


class CallExpr(Expression):
    def __init__(self, callee: Expression, paren: Token, arguments: list[Expression]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor: ExpressionVisitor):
        """ Call the visitor """
        return visitor.visit_call_expr(self)


class FunctionExpr(Expression):
    def __init__(self, params: list[Token], body: list[Any]):
        self.params = params
        self.body = body

    def accept(self, visitor: ExpressionVisitor):
        """ Call the visitor """
        return visitor.visit_function_expr(self)


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


class LogicalExpr(Expression):
    def __init__(self, left: Expression, operator: Token, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExpressionVisitor):
        """ Call the visitor """
        return visitor.visit_logical_expr(self)


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
