from typing import Callable
from plox.token_type import TokenType
from plox.token import Token
from plox.statement import IfStmt, Statement
from plox.expression import (
    AssignExpr,
    BinaryExpr,
    Expression,
    GroupingExpr,
    LiteralExpr,
    UnaryExpr,
    VariableExpr,
)

from plox.statement import (
    BlockStmt,
    ExpressionStmt,
    PrintStmt,
    VariableStmt
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
        try:
            if self._match(TokenType.CLASS):
                return None
            if self._match(TokenType.FUN):
                return None
            if self._match(TokenType.VAR):
                return self._var_declaration()
            return self._statement()
        except:
            self._synchronize()
            return None

    def _statement(self) -> Statement:
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.PRINT):
            return self._print_statement()
        if self._match(TokenType.LEFT_BRACE):
            return BlockStmt(self._block_statement())
        return self._expression_statement()

    def _expression(self) -> Expression:
        return self._assignment()

    # Statements

    def _if_statement(self) -> IfStmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expression = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")

        then_block: Statement = self._statement()
        else_block: Statement | None = None
        if self._match(TokenType.ELSE):
            else_block = self._statement()

        return IfStmt(condition, then_block, else_block)

    def _print_statement(self) -> Statement:
        value: Expression = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value")
        return PrintStmt(value)

    def _block_statement(self) -> list[Statement]:
        statements: list[Statement] = []

        while not (self._check(TokenType.RIGHT_BRACE) or self._at_end_of_token_list()):
            statements.append(self._declaration())

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block")
        return statements

    def _expression_statement(self) -> Statement:
        expr: Expression = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value")
        return ExpressionStmt(expr)

    # Declarations

    def _var_declaration(self) -> Statement:
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name")

        initializer: Expression | None = None

        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration")

        return VariableStmt(name, initializer)

    # Expressions

    def _assignment(self) -> Expression:
        expr: Expression = self._equality()

        if self._match(TokenType.EQUAL):
            equals: Token = self._previous()
            value: Expression = self._assignment()

            if isinstance(expr, VariableExpr):
                name: Token = expr.name
                return AssignExpr(name, value)

            self.on_syntax_error(equals, "Invalid assignment target.")

        return expr

    def _equality(self) -> Expression:
        expr: Expression = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self._previous()
            right = self._comparison()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _comparison(self) -> Expression:
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
        expr: Expression = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self._previous()
            right: Expression = self._factor()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _factor(self) -> Expression:
        expr: Expression = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self._previous()
            right: Expression = self._unary()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _unary(self) -> Expression:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self._previous()
            right: Expression = self._unary()
            return UnaryExpr(operator, right)

        return self._primary()

    def _primary(self):
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

        self._error(self._peek(), "Expected expression.")

    # Utilities

    def _check(self, token_type: TokenType) -> bool:
        """
        Determine if first upcoming token matches an expectation.
        """
        if self._at_end_of_token_list():
            return False
        return self._peek().token_type == token_type

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

    def _error(self, token: Token, message: str) -> None:
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
