from typing import Any
from plox.plox_callable import PloxCallable
from plox.plox_function import PloxFunction


class PloxClass(PloxCallable):
    def __init__(self, name: str, superclass: "PloxClass | None", methods: dict[str, PloxFunction]):
        super().__init__()
        self.name: str = name
        self.superclass: PloxClass | None = superclass
        self.methods: dict[str, PloxFunction] = methods

    def arity(self) -> int:
        initializer: PloxFunction | None = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def call(self, interpreter, arguments: list[Any]):
        # importing PloxInstance here to prevent circular imports
        from plox.plox_instance import PloxInstance
        instance: PloxInstance = PloxInstance(self)

        initializer: PloxFunction | None = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)

        return instance
    
    def find_method(self, identifier: str) -> PloxFunction | None:
        return self.methods.get(identifier)

    def __str__(self):
        return f"<class {self.name}>"

    def to_string(self):
        return f"<class {self.name}>"
