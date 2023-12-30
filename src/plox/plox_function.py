from typing import Any
from plox.plox_callable import PloxCallable
from plox.plox_return import PloxReturn
from plox.statement import FunctionStmt
from plox.environment import Environment
#from plox.interpreter import Interpreter
# can't import Interpreter due to some circular import error
# TODO learn what the problem is and fix

class PloxFunction(PloxCallable):
    def __init__(self, declaration: FunctionStmt, closure: Environment):
        super().__init__()
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
        return f"<fn {self.declaration.name.lexeme}>"

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
