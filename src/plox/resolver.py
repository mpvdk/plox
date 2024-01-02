from typing import Callable
from plox.class_type import ClassType
from plox.expression import (
    AssignExpr, 
    BinaryExpr,
    CallExpr, 
    Expression, 
    ExpressionVisitor,
    FunctionExpr,
    GetExpr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    SetExpr,
    ThisExpr,
    UnaryExpr, 
    VariableExpr
)
from plox.function_type import FunctionType
from plox.interpreter import Interpreter
from plox.statement import (
    BlockStmt,
    BreakStmt,
    ClassStmt,
    ExpressionStmt, 
    FunctionStmt, 
    IfStmt, 
    PrintStmt, 
    ReturnStmt, 
    Statement, 
    StatementVisitor,
    VariableStmt, 
    WhileStmt
)
from plox.token import Token


class Resolver(ExpressionVisitor, StatementVisitor):
    def __init__(self, interpreter: Interpreter, on_semantic_error: Callable):
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.on_semantic_error = on_semantic_error
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    # Statement visits

    def visit_block_stmt(self, block_stmt: BlockStmt) -> None:
        self._begin_scope()
        for stmt in block_stmt.statements:
            self._resolve_statement(stmt)
        self._end_scope()
    
    def visit_break_stmt(self, break_stmt: BreakStmt) -> None:
        return None

    def visit_class_stmt(self, class_stmt: ClassStmt) -> None:
        enclosing_class: ClassType = self.current_class
        self.current_class = ClassType.CLASS
        
        self._declare(class_stmt.name)
        self._define(class_stmt.name)

        self._begin_scope()
        self.scopes[-1]["this"] = True

        for method in class_stmt.methods:
            declaration: FunctionType = FunctionType.METHOD
            self._resolve_function(method.function, declaration)

        self._end_scope()
        self.current_class = enclosing_class

    def visit_expression_stmt(self, expression_stmt: ExpressionStmt) -> None:
        self._resolve_expression(expression_stmt.expression)

    def visit_function_stmt(self, function_stmt: FunctionStmt) -> None:
        self._declare(function_stmt.name)
        self._define(function_stmt.name)
        self._resolve_function(function_stmt.function, FunctionType.FUNCTION)

    def visit_if_stmt(self, if_stmt: IfStmt) -> None:
        self._resolve_expression(if_stmt.condition)
        self._resolve_statement(if_stmt.then_block)
        if not if_stmt.else_block == None:
            self._resolve_statement(if_stmt.else_block)

    def visit_print_stmt(self, print_stmt: PrintStmt) -> None:
        if not print_stmt.expression == None:
            self._resolve_expression(print_stmt.expression)

    def visit_return_stmt(self, return_stmt: ReturnStmt) -> None:
        if self.current_function is FunctionType.NONE:
            self.on_semantic_error(return_stmt.keyword, "Can't return from top-level code.")
        if not return_stmt.value == None:
            self._resolve_expression(return_stmt.value)

    def visit_variable_stmt(self, variable_stmt: VariableStmt) -> None:
        self._declare(variable_stmt.name)
        if variable_stmt.initializer is not None:
            self._resolve_expression(variable_stmt.initializer)
        self._define(variable_stmt.name)

    def visit_while_stmt(self, while_stmt: WhileStmt) -> None:
        self._resolve_expression(while_stmt.condition)
        self._resolve_statement(while_stmt.body)

    # Expression visits

    def visit_assign_expr(self, assign_expr: AssignExpr) -> None:
        self._resolve_expression(assign_expr.value)
        self._resolve_local(assign_expr, assign_expr.name)

    def visit_binary_expr(self, binary_expr: BinaryExpr) -> None:
        self._resolve_expression(binary_expr.left)
        self._resolve_expression(binary_expr.right)

    def visit_call_expr(self, call_expr: CallExpr) -> None:
        self._resolve_expression(call_expr.callee)
        for arg in call_expr.arguments:
            self._resolve_expression(arg)

    def visit_function_expr(self, function_expr: FunctionExpr) -> None:
        self._resolve_function(function_expr)

    def visit_grouping_expr(self, grouping_expr: GroupingExpr) -> None:
        self._resolve_expression(grouping_expr.expression)

    def visit_get_expr(self, get_expr: GetExpr) -> None:
        self._resolve_expression(get_expr.object)

    def visit_literal_expr(self, literal_expr: LiteralExpr) -> None:
        return None

    def visit_logical_expr(self, logical_expr: LogicalExpr) -> None:
        self._resolve_expression(logical_expr.left)
        self._resolve_expression(logical_expr.right)

    def visit_set_expr(self, set_expr: SetExpr) -> None:
        self._resolve_expression(set_expr.value)
        self._resolve_expression(set_expr.object)

    def visit_this_expr(self, this_expr: ThisExpr):
        if self.current_class is not ClassType.CLASS:
            self.on_semantic_error(this_expr.keyword, "Can't use 'this' outise of a class.")
        else:
            self._resolve_local(this_expr, this_expr.keyword)

    def visit_unary_expr(self, unary_expr: UnaryExpr) -> None:
        self._resolve_expression(unary_expr.right)

    def visit_variable_expr(self, variable_expr: VariableExpr) -> None:
        if len(self.scopes) > 0 and self.scopes[-1][variable_expr.name.lexeme] == False:
            self.on_semantic_error(variable_expr.name, "Can't read local variable in its own initializer.")
            return

        self._resolve_local(variable_expr, variable_expr.name)

    # Helpers

    def _resolve_statement(self, stmt: Statement) -> None:
        stmt.accept(self)

    def resolve_statements(self, stmts: list[Statement]) -> None:
        for stmt in stmts:
            self._resolve_statement(stmt)

    def _resolve_expression(self, expr: Expression) -> None:
        expr.accept(self)

    def _resolve_local(self, expr: Expression, name: Token) -> None:
        """
        Inform the interpreter about the depth of a given identifier.
        """
        for i, scope in list(enumerate(reversed(self.scopes))):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, i)
                return

    def _resolve_function(self, function_expr: FunctionExpr, type: FunctionType) -> None:
        """
        Resolve all params and the body of a function.
        Used by both function statements and lambdas.
        """
        enclosing_function: FunctionType = self.current_function
        self.current_function = type

        self._begin_scope()

        for param in function_expr.params:
            self._declare(param)
            self._define(param)
        for stmt in function_expr.body:
            self._resolve_statement(stmt)

        self._end_scope()

        self.current_function = enclosing_function

    def _begin_scope(self) -> None:
        """
        Add a new empty scope to the stack of scopes.
        (i.e. 'enter' a new scope)
        """
        self.scopes.append({})

    def _end_scope(self) -> None:
        """
        Pop the last scope off the stack of scopes.
        (i.e. 'exit' a scope)
        """
        self.scopes.pop()

    def _declare(self, name: Token) -> None:
        """
        Add an identifier to the outermost scope.
        Set it to uninitialized (i.e. value False)
        """
        if len(self.scopes) > 0:
            scope: dict[str, bool] = self.scopes[-1]
            if name.lexeme in scope:
                self.on_semantic_error(name, "Already a variable with this name in this scope.")
                return
            scope[name.lexeme] = False

    def _define(self, name: Token) -> None:
        """
        Set value of identifier to True in the outermost
        scope to indicate that it has been resolved.
        """
        if len(self.scopes) > 0:
            self.scopes[-1][name.lexeme] = True 
