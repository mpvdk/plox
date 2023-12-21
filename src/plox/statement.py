from abc import ABC, abstractmethod
from plox.token import Token
from plox.expression import Expression

class StatementVisitor(ABC):
    """
    Visitor for the Statement class
    """

    @abstractmethod
    def visit_block_stmt(self, block_stmt):
        raise NotImplementedError

    @abstractmethod
    def visit_expression_stmt(self, expression_stmt):
        raise NotImplementedError
    
    @abstractmethod
    def visit_print_stmt(self, print_stmt):
        raise NotImplementedError

    @abstractmethod
    def visit_variable_stmt(self, variable_stmt):
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


class ExpressionStmt(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_expression_stmt(self)


class PrintStmt(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_print_stmt(self)


class VariableStmt(Statement):
    def __init__(self, name: Token, initializer: Expression | None):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_variable_stmt(self)
