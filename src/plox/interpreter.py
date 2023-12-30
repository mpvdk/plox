from math import ceil
from typing import Any, Callable

from plox.plox_return import PloxReturn
from plox.environment import Environment
from plox.expression import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    Expression,
    ExpressionVisitor,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    UnaryExpr,
    VariableExpr,
)
from plox.plox_callable import PloxCallable
from plox.plox_function import PloxFunction
from plox.plox_runtime_error import PloxRuntimeError
from plox.statement import (
    BlockStmt,
    ExpressionStmt,
    FunctionStmt,
    IfStmt,
    PrintStmt,
    ReturnStmt,
    Statement,
    StatementVisitor,
    VariableStmt,
    WhileStmt,
)
from plox.token import Token
from plox.token_type import TokenType

class BreakException(Exception):
    pass

class Interpreter(ExpressionVisitor, StatementVisitor):
    """
    Class representing the interpreter.
    """

    def __init__(self, on_runtime_error: Callable):
        self.on_runtime_error = on_runtime_error
        self.global_env = Environment()
        self.current_env = self.global_env
        # Used to determine if we should print result of expression statement
        # Answer is "no" by default (hence "False")
        self.single_statement: bool = False

    def interpret(self, statements: list[Statement]):
        self.single_statement = len(statements) == 1
        try:
            for statement in statements:
                self._execute(statement)
        except PloxRuntimeError as err:
            self.on_runtime_error(err)

    # Statement visits

    def visit_block_stmt(self, block_stmt: BlockStmt) -> None:
        new_env = Environment(self.current_env)
        self.execute_block(block_stmt.statements, new_env)

    @staticmethod
    def visit_break_stmt() -> None:
        raise BreakException

    def visit_expression_stmt(self, expression_stmt: ExpressionStmt) -> None:
        res = self._evaluate(expression_stmt.expression)
        if self.single_statement:
            print(res)

    def visit_function_stmt(self, function_stmt: FunctionStmt) -> None:
        fn = PloxFunction(function_stmt, self.current_env)
        self.current_env.define(function_stmt.name.lexeme, fn)

    def visit_if_stmt(self, if_stmt: IfStmt) -> None:
        if self._to_bool(self._evaluate(if_stmt.condition)):
            self._execute(if_stmt.then_block)
        elif if_stmt.else_block != None:
            self._execute(if_stmt.else_block)

    def visit_print_stmt(self, print_stmt: PrintStmt) -> None:
        value = self._evaluate(print_stmt.expression)
        print(self._stringify(value))

    def visit_return_stmt(self, return_stmt: ReturnStmt) -> None:
        value = None
        if return_stmt.value != None:
            value = self._evaluate(return_stmt.value)
        raise PloxReturn(value)

    def visit_variable_stmt(self, variable_stmt: VariableStmt) -> None:
        value = None
        if not variable_stmt.initializer == None:
            value = self._evaluate(variable_stmt.initializer)

        self.current_env.define(variable_stmt.name.lexeme, value)

    def visit_while_stmt(self, while_stmt: WhileStmt) -> None:
        try:
            while self._to_bool(self._evaluate(while_stmt.condition)):
                self._execute(while_stmt.body)
        except BreakException:
            # Do nothing - just break out of loop
            pass

    # Expression visits

    def visit_assign_expr(self, expr: AssignExpr) -> Any:
        value = self._evaluate(expr.value)
        self.current_env.assign(expr.name, value)
        return value

    def visit_call_expr(self, expr: CallExpr) -> Any:
        callee = self._evaluate(expr.callee)

        arguments = [self._evaluate(arg) for arg in expr.arguments]

        if not isinstance(callee, PloxCallable):
            raise PloxRuntimeError(expr.paren, "Can only call functions and classes.")

        if not len(arguments) == callee.arity():
            raise PloxRuntimeError(expr.paren, f"Expected {callee.arity()} arguments, but got {len(arguments)}.")

        return callee.call(self, arguments)

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

    @staticmethod
    def visit_literal_expr( expr: LiteralExpr):
        return expr.value

    def visit_logical_expr(self, expr: LogicalExpr):
        left = self._evaluate(expr.left)

        if expr.operator.token_type == TokenType.OR:
            if self._to_bool(left):
                return left

        if expr.operator.token_type == TokenType.AND:
            if not self._to_bool(left):
                return left

        return self._evaluate(expr.right)

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

    def execute_block(self, statements: list[Statement], new_env: Environment):
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
