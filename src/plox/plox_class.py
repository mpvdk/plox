from typing import Any
from plox.plox_callable import PloxCallable
from plox.plox_function import PloxFunction


class PloxClass(PloxCallable):
    def __init__(self, name: str, methods: dict[str, PloxFunction]):
        super().__init__()
        self.name: str = name
        self.methods: dict[str, PloxFunction] = methods

    def arity(self) -> int:
        return 0

    def call(self, interpreter, arguments: list[Any]):
        # importing PloxInstance here to prevent circular imports
        from plox.plox_instance import PloxInstance
        instance: PloxInstance = PloxInstance(self)
        return instance
    
    def find_method(self, identifier: str):
        method: PloxFunction | None = self.methods.get(identifier)
        if method is not None:
            return method

    def __str__(self):
        return f"<class {self.name}>"

    def to_string(self):
        return f"<class {self.name}>"
