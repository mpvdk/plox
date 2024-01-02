from typing import Any
from plox.expression import FunctionExpr
from plox.plox_callable import PloxCallable
from plox.plox_return import PloxReturn
from plox.environment import Environment
#from plox.plox_instance import PloxInstance
#from plox.interpreter import Interpreter
#can't import because of circular import
#TODO: fix (it's annoying...)

class PloxFunction(PloxCallable):
    def __init__(self, name: str | None, declaration: FunctionExpr, closure: Environment):
        super().__init__()
        self.name = name
        self.declaration = declaration
        self.closure = closure

    def arity(self) -> int:
        return len(self.declaration.params)

    # instance is a PloxInstance but circular import issues...
    def bind(self, instance):
        environment: Environment = Environment(self.closure)
        environment.define("this", instance)
        return PloxFunction(self.name, self.declaration, environment)

    def call(self, interpreter, arguments: list[Any]):
        environment: Environment = Environment(self.closure)

        for param_token, arg in zip(self.declaration.params, arguments):
            environment.define(param_token.lexeme, arg)

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except PloxReturn as plox_return:
            return plox_return.value

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
