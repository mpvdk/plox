from typing import Any
from plox.token_type import TokenType

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
        return f"{self.token_type} {self.lexeme} {self.literal}"
