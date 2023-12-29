from typing import Any
from plox.plox_callable import PloxCallable
from plox.statement import FunctionStmt
from plox.environment import Environment
#from plox.interpreter import Interpreter
# can't import Interpreter due to some circular import error
# TODO learn what the problem is and fix

class PloxFunction(PloxCallable):
    def __init__(self, declaration: FunctionStmt):
        super().__init__()
        self.declaration = declaration

    def call(self, interpreter, arguments: list[Any]):
        environment: Environment = Environment(interpreter.global_env)

        for param_token, arg in zip(self.declaration.params, arguments):
            environment.define(param_token.lexeme, arg)

        interpreter.execute_block(self.declaration.body, environment)


    def arity(self) -> int:
        return len(self.declaration.params)

    def to_string(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
