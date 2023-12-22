from typing import Any, TypedDict

from plox.plox_runtime_error import PloxRuntimeError
from plox.token import Token


class ValueInfo(TypedDict):
    value: Any
    initialized: bool


class Environment:
    def __init__(self, enclosing: "Environment | None" = None) -> None:
        self.enclosing = enclosing
        self.values: dict[str, ValueInfo] = {}

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme]['value'] = value
            self.values[name.lexeme]['initialized'] = True
            return value
        elif self.enclosing != None:
            self.enclosing.assign(name, value)
            return value

        raise PloxRuntimeError(name, f"Undefined variable {name.lexeme}")

    def define(self, name: str, value: Any = None):
        if value != None:
            val_info: ValueInfo = {"value": value, "initialized": True}
            self.values[name] = val_info
        else:
            val_info: ValueInfo = {"value": value, "initialized": False}
            self.values[name] = val_info

    def get(self, name: Token):
        if name.lexeme in self.values:
            if self.values[name.lexeme]['initialized'] == True:
                return self.values[name.lexeme]['value']
            else:
                raise PloxRuntimeError(name, f"{name.lexeme} not initialized")
        elif self.enclosing != None:
            return self.enclosing.get(name)

        raise PloxRuntimeError(name, f"Undefined variable {name.lexeme}")
