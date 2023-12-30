from typing import Any
from plox.expression import FunctionExpr
from plox.plox_callable import PloxCallable
from plox.plox_return import PloxReturn
from plox.environment import Environment
#from plox.interpreter import Interpreter
# can't import Interpreter due to some circular import error
# TODO learn what the problem is and fix

class PloxFunction(PloxCallable):
    def __init__(self, name: str | None, declaration: FunctionExpr, closure: Environment):
        super().__init__()
        self.name = name
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, arguments: list[Any]):
        environment: Environment = Environment(self.closure)

        for param_token, arg in zip(self.declaration.params, arguments):
            environment.define(param_token.lexeme, arg)

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except PloxReturn as plox_return:
            return plox_return.value


    def arity(self) -> int:
        return len(self.declaration.params)

    def to_string(self) -> str:
        if self.name:
            return f"<fn {self.name}>"
        else:
            return "<fn>"

    def __str__(self) -> str:
        if self.name:
            return f"<fn {self.name}>"
        else:
            return "<fn>"
