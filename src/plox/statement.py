from abc import ABC, abstractmethod
from plox.token import Token
from plox.expression import Expression, FunctionExpr

class StatementVisitor(ABC):
    """
    Visitor for the Statement class
    """

    @abstractmethod
    def visit_block_stmt(self, block_stmt):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def visit_break_stmt():
        raise NotImplementedError

    @abstractmethod
    def visit_expression_stmt(self, expression_stmt):
        raise NotImplementedError
    
    @abstractmethod
    def visit_function_stmt(self, function_stmt):
        raise NotImplementedError
    
    @abstractmethod
    def visit_if_stmt(self, if_stmt):
        raise NotImplementedError
    
    @abstractmethod
    def visit_print_stmt(self, print_stmt):
        raise NotImplementedError

    @abstractmethod
    def visit_return_stmt(self, return_stmt):
        raise NotImplementedError

    @abstractmethod
    def visit_variable_stmt(self, variable_stmt):
        raise NotImplementedError

    @abstractmethod
    def visit_while_stmt(self, while_stmt):
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


class BreakStmt(Statement):
    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_break_stmt()


class ExpressionStmt(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_expression_stmt(self)


class FunctionStmt(Statement):
    def __init__(self, name: Token, function: FunctionExpr):
        self.name = name
        self.function = function

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_function_stmt(self)


class IfStmt(Statement):
    def __init__(self, condition: Expression, then_block: Statement, else_block: Statement | None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_if_stmt(self)


class PrintStmt(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_print_stmt(self)


class ReturnStmt(Statement):
    def __init__(self, keyword: Token, value: Expression | None):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_return_stmt(self)


class VariableStmt(Statement):
    def __init__(self, name: Token, initializer: Expression | None):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_variable_stmt(self)


class WhileStmt(Statement):
    def __init__(self, condition: Expression, body: Statement):
        self.condition = condition
        self.body = body

    def accept(self, visitor: StatementVisitor):
        """ Call the visitor """
        return visitor.visit_while_stmt(self)

