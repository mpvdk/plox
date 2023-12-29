from abc import ABC, abstractmethod
from typing import Any
#from plox.interpreter import Interpreter
# can't import Interpreter due to some circular import error
# TODO learn what the problem is and fix

class PloxCallable(ABC):
    @abstractmethod
    def call(self, interpreter, arguments: list[Any]):
        raise NotImplementedError

    @abstractmethod
    def arity(self) -> int:
        raise NotImplementedError
