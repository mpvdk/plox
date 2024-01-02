from __future__ import annotations
from typing import Any
from plox.plox_class import PloxClass
from plox.plox_runtime_error import PloxRuntimeError
from plox.token import Token


class PloxInstance:
    def __init__(self, plox_class: PloxClass):
        self.plox_class: PloxClass = plox_class
        self.fields: dict = {}

    def get(self, identifier: Token):
        if identifier.lexeme in self.fields:
            return self.fields[identifier.lexeme]

        method: PloxFunction | None = self.plox_class.find_method(identifier.lexeme)
        if method is not None:
            return method

        raise PloxRuntimeError(identifier, f"Undefined property '{identifier.lexeme}'.")

    def set(self, name: Token, value: Any):
        self.fields[name.lexeme] = value

    def __str__(self):
        return f"<instance {self.plox_class.name}>"

    def to_string(self):
        return f"<instance {self.plox_class.name}>"
