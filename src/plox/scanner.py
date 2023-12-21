from typing import Any, Callable
from plox.token import Token
from plox.token_type import TokenType

class Scanner:
    """
    Class for scanner instance.
    Contains all data and methods required for lexical analysis.
    """

    keywords = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
    }

    def __init__(self, source: str, on_lexical_error: Callable, interactive: bool):
        self.source = source
        self.on_lexical_error = on_lexical_error
        self.interactive = interactive
        self.block_comment_nest_lvl = 0
        self.start_current_lexeme = 0
        self.current_pos = 0
        self.current_line = 1
        self.tokens: list[Token] = []

    def scan_tokens(self) -> list:
        """
        Scan all tokens from self.source
        (Mostly delegates to self._scan_token)
        """
        while not self._eof_reached():
           self.start_current_lexeme = self.current_pos
           self._scan_token()

        self.tokens.append(Token(
            token_type = TokenType.EOF, 
            lexeme = "", 
            literal = None, 
            line = self.current_line
        ))

        return self.tokens
        
    def _scan_token(self):
        """
        Scan for the next token
        """
        char = self._advance()
        match char:
            # whitespace
            case ' ': pass
            case '\r': pass
            case '\t': pass
            case '\n': 
                self.current_line += 1
            # single-char lexemes
            case '(': self._add_token(TokenType.LEFT_PAREN)
            case ')': self._add_token(TokenType.RIGHT_PAREN)
            case '{': self._add_token(TokenType.LEFT_BRACE)
            case '}': self._add_token(TokenType.RIGHT_BRACE)
            case ',': self._add_token(TokenType.COMMA)
            case '.': self._add_token(TokenType.DOT)
            case '-': self._add_token(TokenType.MINUS)
            case '+': self._add_token(TokenType.PLUS)
            case ';': self._add_token(TokenType.SEMICOLON)
            case '*': self._add_token(TokenType.STAR)
            # one- and two- char lexemes
            case '!': self._add_token(TokenType.BANG_EQUAL if self._match('=') else TokenType.BANG)
            case '=': self._add_token(TokenType.EQUAL_EQUAL if self._match('=') else TokenType.EQUAL)
            case '<': self._add_token(TokenType.LESS_EQUAL if self._match('=') else TokenType.LESS)
            case '>': self._add_token(TokenType.GREATER_EQUAL if self._match('=') else TokenType.GREATER)
            # (block) comment or slash
            case '/': 
                if self._match('/'):
                    # comment ( // )
                    while self._peek() != '\n' and not self._eof_reached():
                        self._advance()
                    self._add_token(TokenType.COMMENT)
                elif self._match('*'):
                    # block comment ( /* ... */ )
                    while (self._peek() != '*' and self._peek(1) != '/') or self.block_comment_nest_lvl > 0:
                        if self._peek() == '\n':
                            self.current_line += 1
                        if self._peek() == '/' and self._peek(1) == '*':
                            # nested block comment begins
                            self.block_comment_nest_lvl += 1
                        if self._peek() == '*' and self._peek(1) == '/':
                            # nested block comment ends
                            self.block_comment_nest_lvl -= 1

                        self._advance()

                    # advance twice to consume close of block comment */
                    self._advance()
                    self._advance()

                    self._add_token(TokenType.COMMENT)
                else:
                    # just slash
                    self._add_token(TokenType.SLASH)
            # multi-char lexemes
            case '"': 
                self._string()
            case _ if char.isdecimal(): 
                self._number()
            case _ if char.isalpha() or char == '_': 
                self._identifier_or_keyword()
            # error error
            case _: 
                self.on_lexical_error(self.current_line, f"Unexpected character: {char}")

    def _current_lexeme(self) -> str:
       return self.source[self.start_current_lexeme : self.current_pos]

    def _identifier_or_keyword(self):
        while self._peek().isalnum():
            self._advance()

        lexeme = self._current_lexeme()
        token_type = self.keywords.get(lexeme, TokenType.IDENTIFIER)    

        self._add_token(token_type)

    def _string(self):
        """
        Scan until end of string literal
        Add STRING token if terminated
        """
        while self._peek() != '"' and not self._eof_reached():
            if self._peek() == '\n':
                self.current_line += 1
            self._advance()

        if self._eof_reached():
            self.on_lexical_error(self.current_line, f"Unterminated string")
            return
            
        self._advance() # move passed the closing "

        # trim quotes
        val = self.source[self.start_current_lexeme + 1 : self.current_pos - 1]
        self._add_token(TokenType.STRING, val)

    def _number(self):
        is_float = False

        while self._peek().isdecimal():
           self._advance()

        if self._peek() == '.' and self._peek(1).isdecimal():
            is_float = True
            self._advance()

            while self._peek().isdecimal():
                self._advance()

        val = float(self._current_lexeme()) if is_float else  int(self._current_lexeme())

        self._add_token(TokenType.NUMBER, val)

    def _eof_reached(self) -> bool:
        return self.current_pos >= len(self.source)

    def _peek(self, skip: int = 0) -> str:
        """
        Read and return first upcoming character
        """
        if self._eof_reached():
            return '\0'
        return self.source[self.current_pos + skip]

    def _match(self, expected: str) -> bool:
        """
        Check if the next character matches expected.
        If it does, move current_pos forward
        """
        if self._eof_reached():
            return False
        if self.source[self.current_pos] != expected:
            return False

        self.current_pos += 1
        return True

    def _advance(self) -> str:
        """ 
        Read & return current char and advance current_pos
        """
        char = self.source[self.current_pos]
        self.current_pos += 1
        return char

    def _add_token(self, token_type: TokenType, literal: Any = None):
        """
        Grab current lexeme and use to construct new Token and add to self.tokens
        """
        lexeme = self._current_lexeme()
        self.tokens.append(Token(token_type, lexeme, literal, self.current_line))
