from __future__ import annotations
from abc import ABC, abstractmethod
from plox.token import Token
from plox.expression import Expression, FunctionExpr, VariableExpr

class StatementVisitor(ABC):
    """
    Visitor for the Statement class
    """

    @abstractmethod
    def visit_block_stmt(self, block_stmt: BlockStmt):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def visit_break_stmt():
        raise NotImplementedError

    @abstractmethod
    def visit_class_stmt(self, class_stmt: ClassStmt):
        raise NotImplementedError

    @abstractmethod
    def visit_expression_stmt(self, expression_stmt: ExpressionStmt):
        raise NotImplementedError
    
    @abstractmethod
    def visit_function_stmt(self, function_stmt: FunctionStmt):
        raise NotImplementedError
    
    @abstractmethod
    def visit_if_stmt(self, if_stmt: IfStmt):
        raise NotImplementedError
    
    @abstractmethod
    def visit_print_stmt(self, print_stmt: PrintStmt):
        raise NotImplementedError

    @abstractmethod
    def visit_return_stmt(self, return_stmt: ReturnStmt):
        raise NotImplementedError

    @abstractmethod
    def visit_variable_stmt(self, variable_stmt: VariableStmt):
        raise NotImplementedError

    @abstractmethod
    def visit_while_stmt(self, while_stmt: WhileStmt):
        raise NotImplementedError


class Statement(ABC):
    """
    Abstract base class for statements
    """

    @abstractmethod
    def accept(self, visitor: StatementVisitor):
        raise NotImplementedError


class BlockStmt(Statement):
    def __init__(self, statements: list[Statement]):
        self.statements: list[Statement] = statements

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_block_stmt(self)


class ClassStmt(Statement):
    def __init__(self, name: Token, superclass: VariableExpr | None, methods: list[FunctionStmt]):
        self.name: Token = name
        self.superclass: VariableExpr | None = superclass
        self.methods: list[FunctionStmt] = methods

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_class_stmt(self)


class BreakStmt(Statement):
    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_break_stmt()


class ExpressionStmt(Statement):
    def __init__(self, expression: Expression):
        self.expression: Expression = expression

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_expression_stmt(self)


class FunctionStmt(Statement):
    def __init__(self, name: Token, function: FunctionExpr):
        self.name: Token = name
        self.function: FunctionExpr = function

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_function_stmt(self)


class IfStmt(Statement):
    def __init__(self, condition: Expression, then_block: Statement, else_block: Statement | None):
        self.condition: Expression = condition
        self.then_block: Statement = then_block
        self.else_block: Statement | None = else_block

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_if_stmt(self)


class PrintStmt(Statement):
    def __init__(self, expression: Expression):
        self.expression: Expression = expression

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_print_stmt(self)


class ReturnStmt(Statement):
    def __init__(self, keyword: Token, value: Expression | None):
        self.keyword: Token = keyword
        self.value: Expression | None = value

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_return_stmt(self)


class VariableStmt(Statement):
    def __init__(self, name: Token, initializer: Expression | None):
        self.name: Token = name
        self.initializer: Expression | None = initializer

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_variable_stmt(self)


class WhileStmt(Statement):
    def __init__(self, condition: Expression, body: Statement):
        self.condition: Expression = condition
        self.body: Statement = body

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_while_stmt(self)
