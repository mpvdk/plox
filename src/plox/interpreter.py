from math import ceil
from typing import Any, Callable

from plox.environment import Environment
from plox.expression import (
    AssignExpr,
    BinaryExpr,
    Expression,
    ExpressionVisitor,
    GroupingExpr,
    LiteralExpr,
    UnaryExpr,
    VariableExpr,
)
from plox.plox_runtime_error import PloxRuntimeError
from plox.statement import (
    BlockStmt,
    ExpressionStmt,
    PrintStmt,
    Statement,
    StatementVisitor,
    VariableStmt,
)
from plox.token import Token
from plox.token_type import TokenType

class Interpreter(ExpressionVisitor, StatementVisitor):
    """
    Class representing the interpreter.
    """

    def __init__(self, on_runtime_error: Callable):
        self.on_runtime_error = on_runtime_error
        self.current_env = Environment()

    def interpret(self, statements: list[Statement]):
        try:
            for statement in statements:
                self._execute(statement)
        except PloxRuntimeError as err:
            self.on_runtime_error(err)

    # Statement visits

    def visit_block_stmt(self, block_stmt: BlockStmt) -> None:
        new_block_env = Environment(self.current_env)
        self._execute_block(block_stmt.statements, new_block_env)

    def visit_expression_stmt(self, expression_stmt: ExpressionStmt) -> None:
        res = self._evaluate(expression_stmt.expression)
        print(res)

    def visit_print_stmt(self, print_stmt: PrintStmt) -> None:
        value = self._evaluate(print_stmt.expression)
        print(self._stringify(value))

    def visit_variable_stmt(self, variable_stmt: VariableStmt) -> None:
        value = None
        if not variable_stmt.initializer == None:
            value = self._evaluate(variable_stmt.initializer)

        self.current_env.define(variable_stmt.name.lexeme, value)

    # Expression visits

    def visit_assign_expr(self, expr: AssignExpr):
        value = self._evaluate(expr.value)
        self.current_env.assign(expr.name, value)
        return value

    def visit_binary_expr(self, expr: BinaryExpr):
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)
        operator_token_type = expr.operator.token_type
        
        if operator_token_type in (
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.MINUS,
            TokenType.SLASH,
            TokenType.STAR,
        ):
            self._check_number_operands(expr.operator, left, right)

        match operator_token_type:
            # Arithmetic
            case TokenType.MINUS:
                return left - right
            case TokenType.PLUS:
                return self._binary_plus(expr, left, right)
            case TokenType.SLASH:
                return self._binary_slash(expr, left, right)
            case TokenType.STAR:
                return left * right
            # Equality
            case TokenType.BANG_EQUAL:
                return not self._is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self._is_equal(left, right)
            # Comparison
            case TokenType.GREATER:
                return left > right
            case TokenType.GREATER_EQUAL:
                return left >= right
            case TokenType.LESS:
                return left < right
            case TokenType.LESS_EQUAL:
                return left <= right

        return None

    def visit_grouping_expr(self, expr: GroupingExpr):
        return self._evaluate(expr.expression)

    def visit_literal_expr(self, expr: LiteralExpr):
        return expr.value

    def visit_unary_expr(self, expr: UnaryExpr):
        right = self._evaluate(expr.right)

        match expr.operator:
            case TokenType.MINUS:
                return -float(right)
            case TokenType.BANG:
                return not Interpreter._to_bool(right)

    def visit_variable_expr(self, expr: VariableExpr):
        return self.current_env.get(expr.name)

    # Misc

    def _evaluate(self, expression: Expression):
        return expression.accept(self)

    def _execute(self, statement: Statement):
        statement.accept(self)

    def _execute_block(self, statements: list[Statement], new_env: Environment):
        prev_env: Environment = self.current_env
        self.current_env = new_env

        try:

            for statement in statements:
                self._execute(statement)
        finally:
            self.current_env = prev_env


    @staticmethod
    def _to_bool(value) -> bool:
        """
        In the book this method is called "isTruthy". 
        I prefer "to_bool".
        """
        if value == None:
            return False
        if type(value) == bool:
            return value
        # Everything else is True
        return True

    @staticmethod
    def _check_number_operands(operator: Token, *args: Any):
        """
        Check if all given operands are either float or int.
        Raise error if one is not.
        """
        for operand in args:
            if not isinstance(operand, (float, int)):
                raise PloxRuntimeError(operator, "Operands must be numbers.")

    @staticmethod
    def _is_equal(a: Any, b: Any) -> bool:
        """
        Check if two operands are equal.
        Handle None type as secial case.
        """
        if a is None and b is None:
            return True

        if a is None or b is None:
            return False

        return a == b

    @staticmethod
    def _binary_plus(expr: BinaryExpr, a: Any, b: Any):
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a + b

        if isinstance(a, str) and isinstance(b, str):
            return a + b

        if isinstance(a, str) or isinstance(b, str):
            return str(a) + str(b)

        raise PloxRuntimeError(expr.operator, "Operands must be numbers or strings.")

    @staticmethod
    def _binary_slash(expr: BinaryExpr, left: int | float, right: int | float):
        if int(ceil(right)) == 0:
            raise PloxRuntimeError(expr.operator, "Cannot divide by zero")
        return left / right

    @staticmethod
    def _stringify(obj) -> str:
        if obj == None:
            return "nil"

        if isinstance(obj, float):
            return f"{obj:0.10g}"

        return str(obj)
