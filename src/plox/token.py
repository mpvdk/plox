from plox.token_type import TokenType
from typing import Any

class Token:
    """
    Class representing a parsed lox token
    """

    def __init__(self, token_type: TokenType, lexeme: str, literal: Any, line: int):
        """
        Create a new token
        """
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def to_string(self) -> str:
        return f"Type:    {self.token_type}\nLexeme:  {self.lexeme}\nLiteral: {self.literal}"
