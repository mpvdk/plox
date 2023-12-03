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

    def __init__(self, source: str, on_error: Callable, interactive: bool):
        self.source = source
        self.on_error = on_error
        self.interactive = interactive
        self.block_com_nest_lvl = 0
        self.start_current_lexeme = 0
        self.current_pos = 0
        self.current_line = 1
        self.tokens = []

    def scan_tokens(self) -> list:
        """
        Scan all tokens from self.source
        (Mostly delegates to self.scan_token)
        """
        while not self.eof_reached():
           self.start_current_lexeme = self.current_pos
           self.scan_token()

        if not self.interactive:
            self.tokens.append(Token(TokenType.EOF, "", None, self.current_line))

        return self.tokens
        
    def scan_token(self):
        """
        Scan for the next token
        """
        char = self.advance()
        match char:
            # whitespace
            case ' ': pass
            case '\r': pass
            case '\t': pass
            case '\n': 
                self.current_line += 1
            # single-char lexemes
            case '(': self.add_token(TokenType.LEFT_PAREN)
            case ')': self.add_token(TokenType.RIGHT_PAREN)
            case '{': self.add_token(TokenType.LEFT_BRACE)
            case '}': self.add_token(TokenType.RIGHT_BRACE)
            case ',': self.add_token(TokenType.COMMA)
            case '.': self.add_token(TokenType.DOT)
            case '-': self.add_token(TokenType.MINUS)
            case '+': self.add_token(TokenType.PLUS)
            case ';': self.add_token(TokenType.SEMICOLON)
            case '*': self.add_token(TokenType.STAR)
            # one- and two- char lexemes
            case '!': self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            case '=': self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            case '<': self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            case '>': self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
            # (block) comment or slash
            case '/': 
                if self.match('/'):
                    # comment ( // )
                    while self.peek() != '\n' and not self.eof_reached():
                        self.advance()
                    
                    self.add_token(TokenType.COMMENT)
                elif self.match('*'):
                    # block comment ( /* ... */ )
                    while not(self.peek() == '*' and self.peek(1) == '/') or self.block_com_nest_lvl > 0:
                        if self.peek() == '\n':
                            self.current_line += 1
                        if self.peek() == '/' and self.peek(1) == '*':
                            # nested block comment begins
                            self.block_com_nest_lvl += 1
                        if self.peek() == '*' and self.peek(1) == '/':
                            # nested block comment ends
                            self.block_com_nest_lvl -= 1

                        self.advance()

                    # advance twice to consume close of block comment */
                    self.advance()
                    self.advance()

                    self.add_token(TokenType.COMMENT)
                else:
                    # just slash
                    self.add_token(TokenType.SLASH)
            # multi-char lexemes
            case '"': 
                self.string()
            case _ if char.isdecimal(): 
                self.number()
            case _ if char.isalpha() or char == '_': 
                self.identifier_or_keyword()
            # error error
            case _: 
                self.on_error(self.current_line, f"Unexpected character: {char}")

    def current_lexeme(self) -> str:
       return self.source[self.start_current_lexeme:self.current_pos]

    def identifier_or_keyword(self):
        while self.peek().isalnum():
            self.advance()

        lexeme = self.current_lexeme()
        token_type = self.keywords.get(lexeme, TokenType.IDENTIFIER)    

        self.add_token(token_type)

    def string(self):
        """
        Scan until end of string literal
        Add STRING token if terminated
        """
        while self.peek() != '"' and not self.eof_reached():
            if self.peek() == '\n':
                self.current_line += 1
            self.advance()

        if self.eof_reached():
            self.on_error(self.current_line, f"Unterminated string")
            return
            
        self.advance() # move passed the closing "

        # trim quotes
        val = self.source[self.start_current_lexeme+1:self.current_pos-1]
        self.add_token(TokenType.STRING, val)

    def number(self):
        while self.peek().isdecimal():
           self.advance()

        if self.peek() == '.' and self.peek(1).isdecimal():
            self.advance()

            while self.peek().isdecimal():
                self.advance()

        self.add_token(TokenType.NUMBER, self.current_lexeme())

    def eof_reached(self) -> bool:
        return self.current_pos >= len(self.source)

    def peek(self, skip: int = 0) -> str:
        """
        Read and return first upcoming character
        """
        if self.eof_reached():
            return '\0'
        return self.source[self.current_pos + skip]

    def match(self, expected: str) -> bool:
        """
        Check if the next character matches expected.
        If it does, move current_pos forward
        """
        if self.eof_reached():
            return False
        if self.source[self.current_pos] != expected:
            return False

        self.current_pos += 1
        return True

    def advance(self) -> str:
        """ 
        Read & return current char and advance current_pos
        """
        char = self.source[self.current_pos]
        self.current_pos += 1
        return char

    def add_token(self, token_type: TokenType, literal: Any = None):
        """
        Grab current lexeme and use to construct new Token and add to self.tokens
        """
        lexeme = self.current_lexeme()
        self.tokens.append(Token(token_type, lexeme, literal, self.current_line))
