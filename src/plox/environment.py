from __future__ import annotations
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
        elif self.enclosing is not None:
            self.enclosing.assign(name, value)
            return value

        raise PloxRuntimeError(name, f"Undefined variable {name.lexeme}")

    def assign_at(self, distance: int, name: Token, value: Any):
        self._ancestor(distance).values[name.lexeme] = value

    def define(self, name: str, value: Any = None):
        if value is not None:
            val_info: ValueInfo = {"value": value, "initialized": True}
            self.values[name] = val_info
        else:
            val_info: ValueInfo = {"value": value, "initialized": False}
            self.values[name] = val_info

    def get(self, name: Token):
        if name.lexeme in self.values:
            if self.values[name.lexeme]['initialized'] == True:
                val_info: ValueInfo = self.values[name.lexeme]
                return val_info['value']
            else:
                raise PloxRuntimeError(name, f"{name.lexeme} not initialized")
        elif self.enclosing is not None:
            val_info: ValueInfo = self.enclosing.get(name)
            return val_info['value']

        raise PloxRuntimeError(name, f"Undefined variable {name.lexeme}")

    def get_at(self, distance: int, name: str):
        val_info: ValueInfo | None = self._ancestor(distance).values.get(name)
        if val_info is not None:
            return val_info['value']

    def _ancestor(self, distance: int) -> Environment:
        env: Environment = self
        for _ in range(distance):
            env = env.enclosing
        return env
