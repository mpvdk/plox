from plox.token import Token

class PloxRuntimeError(Exception):
    def __init__(self, token: Token | None, message: str | None):
        super().__init__(message)
        self.token = token
        self.message = message
