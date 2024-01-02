from abc import ABC, abstractmethod
from typing import Any
#from plox.interpreter import Interpreter
#can't import because of circular import
#TODO: fix (it's annoying...)

class PloxCallable(ABC):
    @abstractmethod
    def call(self, interpreter, arguments: list[Any]):
        raise NotImplementedError

    @abstractmethod
    def arity(self) -> int:
        raise NotImplementedError
