from typing import Callable, NoReturn, Literal
from plox.token_type import TokenType
from plox.token import Token
from plox.expression import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    Expression,
    FunctionExpr,
    GetExpr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    SetExpr,
    UnaryExpr,
    VariableExpr,
)
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
    VariableStmt,
    WhileStmt
)

class ParseError(Exception):
    def __init__(self, token, message):
        self.token = token
        self.message = message
        super().__init__(self.message)


class Parser:
    """
    The main parser class
    """

    def __init__(self, tokens: list[Token], on_syntax_error: Callable):
        self.tokens = tokens
        self.on_syntax_error = on_syntax_error
        self.current = 0
        self.current_loop_depth = 0

    def parse(self) -> list[Statement]:
        """
        Entry point to parsing all tokens
        """
        statements: list[Statement] = []
        while not self._at_end_of_token_list():
            stmt = self._declaration()
            if isinstance(stmt, Statement):
                statements.append(stmt)

        return statements

    def _declaration(self) -> Statement | None:
        """
        Production: declaration.
        """
        try:
            if self._match(TokenType.CLASS):
                return self._class_declaration()
            if self._check(TokenType.FUN) and self._check_next(TokenType.IDENTIFIER):
                self._consume(TokenType.FUN, "")
                return self._function("function")
            if self._match(TokenType.VAR):
                return self._var_declaration()
            return self._statement()
        except:
            self._synchronize()
            return None

    def _statement(self) -> Statement:
        """
        Production: statement.
        """
        if self._match(TokenType.BREAK):
            return self._break_statement()
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.PRINT):
            return self._print_statement()
        if self._match(TokenType.RETURN):
            return self._return_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.LEFT_BRACE):
            return BlockStmt(self._block_statement())
        return self._expression_statement()

    def _expression(self) -> Expression:
        """
        Production: expression.
        """
        return self._assignment()

    # Statements

    def _break_statement(self) -> BreakStmt:
        """
        Production: break statement.
        """
        if self.current_loop_depth == 0:
            self._error(self._previous(), "'break' can only be used inside a loop")
        self._consume(TokenType.SEMICOLON, "Expected ';' after 'break'")
        return BreakStmt()

    def _for_statement(self) -> BlockStmt | WhileStmt:
        """
        Production: for statement.
        """
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'")

        initializer: Statement | None
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition: Expression | None = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after condition.")

        increment: Expression | None = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expted ')' after for clauses.")

        try:
            self.current_loop_depth = self.current_loop_depth + 1

            body: Statement = self._statement()

            if increment is not None:
                body = BlockStmt([body, ExpressionStmt(increment)])

            if condition is None:
                condition = LiteralExpr(True)

            body = WhileStmt(condition, body)

            if initializer is not None:
                body = BlockStmt([initializer, body])

            return body
        finally:
            self.current_loop_depth = self.current_loop_depth - 1


    def _if_statement(self) -> IfStmt:
        """
        Production: if statement.
        """
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expression = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")

        then_block: Statement = self._statement()
        else_block: Statement | None = None
        if self._match(TokenType.ELSE):
            else_block = self._statement()

        return IfStmt(condition, then_block, else_block)

    def _print_statement(self) -> PrintStmt:
        """
        Production: print statement.
        """
        value: Expression = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value")
        return PrintStmt(value)

    def _return_statement(self) -> ReturnStmt:
        """
        Production: return statement.
        """
        keyword: Token = self._previous()
        value: Expression | None = None
        if not self._check(TokenType.SEMICOLON):
            value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after return value")
        return ReturnStmt(keyword, value)
    
    def _while_statement(self) -> WhileStmt:
        """
        Production: while statement.
        """
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'.")
        condition: Expression = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after condition.")
        try:
            self.current_loop_depth = self.current_loop_depth + 1
            body: Statement = self._statement()
            return WhileStmt(condition, body)
        finally:
            self.current_loop_depth = self.current_loop_depth - 1

    def _block_statement(self) -> list[Statement]:
        """
        Production: block statement.

        Returns list[Statement] rather than BlockStmt
        because it is reused for function bodies
        """
        statements: list[Statement] = []

        while not (self._check(TokenType.RIGHT_BRACE) or self._at_end_of_token_list()):
            statements.append(self._declaration())

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block")
        return statements

    def _expression_statement(self) -> ExpressionStmt:
        """
        Production: expression statement.
        """
        expr: Expression = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value")
        return ExpressionStmt(expr)

    # Declarations

    def _class_declaration(self) -> Statement:
        name: Token = self._consume(TokenType.IDENTIFIER, "Expect class name.")
        self._consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")
        
        methods: list[FunctionStmt] = []
        while not self._at_end_of_token_list() and not self._check(TokenType.RIGHT_BRACE):
            methods.append(self._function("method"))

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return ClassStmt(name, methods)

    def _function(self, kind: Literal["function", "method"]) -> FunctionStmt: 
        """
        Production: function declaration.
        """
        name: Token = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        return FunctionStmt(name, self._function_body(kind))

    def _function_body(self, kind: Literal["function", "method"]):
        self._consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind}.")

        parameters: list[Token] = []
        if not self._check(TokenType.RIGHT_PAREN):
            first_param = self._consume(TokenType.IDENTIFIER, "Expect parameter name")
            parameters.append(first_param)
            while self._match(TokenType.COMMA):
                if not len(parameters) >= 255:
                    param = self._consume(TokenType.IDENTIFIER, "Expect parameter name")
                    parameters.append(param)
                else:
                    self._error(self._peek(), "Can't have more than 255 parameters.")

        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
        self._consume(TokenType.LEFT_BRACE, "Expected '{' before function body")
        body: list[Statement] = self._block_statement()

        return FunctionExpr(parameters, body)

    def _var_declaration(self) -> VariableStmt:
        """
        Production: declaration.
        """
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name")

        initializer: Expression | None = None

        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration")

        return VariableStmt(name, initializer)

    # Expressions

    def _assignment(self) -> Expression:
        """
        Production: assignment.
        """
        expr: Expression = self._or()

        if self._match(TokenType.EQUAL):
            equals: Token = self._previous()
            value: Expression = self._assignment()

            if isinstance(expr, VariableExpr):
                # plain variable assignment
                name: Token = expr.name
                return AssignExpr(name, value)
            elif isinstance(expr, GetExpr):
                # object property assignment
                return SetExpr(expr.object, expr.name, value)

            self.on_syntax_error(equals, "Invalid assignment target.")

        return expr

    def _or(self) -> Expression:
        """
        Production: logic or.
        """
        expr: Expression = self._and()

        while self._match(TokenType.OR):
            operator: Token = self._previous()
            right: Expression = self._and()
            expr = LogicalExpr(expr, operator, right)

        return expr


    def _and(self) -> Expression:
        """
        Production: logic and.
        """
        expr: Expression = self._equality()

        while self._match(TokenType.AND):
            operator: Token = self._previous()
            right: Expression = self._equality()
            expr = LogicalExpr(expr, operator, right)

        return expr

    def _equality(self) -> Expression:
        """
        Production: equality.
        """
        expr: Expression = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self._previous()
            right = self._comparison()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _comparison(self) -> Expression:
        """
        Production: comparison.
        """
        expr: Expression = self._term()

        while self._match(
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL,
            ):
            operator : Token= self._previous()
            right: Expression = self._term()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _term(self) -> Expression:
        """
        Production: term.
        """
        expr: Expression = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self._previous()
            right: Expression = self._factor()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _factor(self) -> Expression:
        """
        Production: factor.
        """
        expr: Expression = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self._previous()
            right: Expression = self._unary()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _unary(self) -> Expression:
        """
        Production: unary.
        """
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self._previous()
            right: Expression = self._unary()
            return UnaryExpr(operator, right)

        return self._call()

    def _call(self) -> Expression:
        """
        Production: call.
        """
        expr: Expression = self._primary()

        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                name: Token = self._consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = GetExpr(expr, name)
            else:
                break

        return expr

    def _finish_call(self, callee: Expression) -> CallExpr:
        """
        Helper to call production.
        """
        arguments: list[Expression] = []
        if not self._check(TokenType.RIGHT_PAREN):
            arguments.append(self._expression())
            while self._match(TokenType.COMMA):
                if not len(arguments) >= 255:
                    arguments.append(self._expression())
                else:
                    self._error(self._peek(), "Can't have more than 255 arguments")

        paren: Token = self._consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return CallExpr(callee, paren, arguments)

    def _primary(self) -> Expression:
        """
        Production: primary.
        """
        if self._match(TokenType.FALSE):
            return LiteralExpr(False)

        if self._match(TokenType.TRUE):
            return LiteralExpr(True)

        if self._match(TokenType.NIL):
            return LiteralExpr(None)

        if self._match(TokenType.NUMBER):
            return LiteralExpr(self._previous().literal)

        if self._match(TokenType.STRING):
            return LiteralExpr(self._previous().literal)

        if self._match(TokenType.IDENTIFIER):
            return VariableExpr(self._previous())

        if self._match(TokenType.LEFT_PAREN):
            expr: Expression = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return GroupingExpr(expr)

        if self._match(TokenType.FUN):
            return self._function_body("function")

        self._error(self._peek(), "Expected expression.")

    # Utilities

    def _check(self, token_type: TokenType) -> bool:
        """
        Determine if first upcoming token matches an expectation.
        """
        if self._at_end_of_token_list():
            return False
        return self._peek().token_type == token_type

    def _check_next(self, token_type: TokenType) -> bool:
        """
        Determine if the second upcoming token matches an expectation.
        """
        if self._at_end_of_token_list():
            return False
        if self.tokens[self.current + 1].token_type == TokenType.EOF:
            return False
        return self.tokens[self.current + 1].token_type == token_type

    def _match(self, *args: TokenType) -> bool:
        """
        Determine if first upcoming token(s) match expectation.
        If so, advance the parser.
        """
        for token_type in args:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _consume(self, token_type: TokenType, message: str):
        """
        Determine if first upcoming token matches an expectation.
        If so, advance the parser. Else, error.
        """
        if self._check(token_type):
            return self._advance()
        self._error(self._peek(), message)

    def _peek(self) -> Token:
        """
        Return first upcoming token waiting to be parsed.
        """
        return self.tokens[self.current]

    def _previous(self) -> Token:
        """ 
        Return previous Token.
        """
        return self.tokens[self.current - 1]

    def _advance(self) -> Token:
        """
        Advance self.current and return new token.
        """
        parse_me: Token = self.tokens[self.current]
        if not self._at_end_of_token_list():
            self.current += 1
        return parse_me

    def _at_end_of_token_list(self) -> bool:
        """ 
        Have we parsed all tokens?
        """
        return self.current >= len(self.tokens) - 1

    def _error(self, token: Token, message: str) -> NoReturn:
        """
        Raise parse/syntax error.
        """
        self.on_syntax_error(token, message)
        raise ParseError(token, message)

    def _synchronize(self) -> None:
        """
        Synchronize back to statement boundary if ParseError occurs.
        """
        self._advance()

        while not self._at_end_of_token_list():
            if self._previous().token_type == TokenType.SEMICOLON:
                return

            if self._peek().token_type in [
                TokenType.CLASS,
                TokenType.FOR,
                TokenType.FUN,
                TokenType.IF,
                TokenType.PRINT,
                TokenType.RETURN,
                TokenType.VAR,
                TokenType.WHILE,
            ]:
                return

            self._advance()

