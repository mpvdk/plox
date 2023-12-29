import time
from plox.plox_callable import PloxCallable

class Clock(PloxCallable):
    def call(self, interpreter, arguments):
        """
        Return the time in seconds since the epoch as a floating point number
        """
        return time.time()

    def arity(self) -> int:
        """
        Return number of arguments
        """
        return 0

    def to_string(self):
        return "<native fn>"

    def __str__(self):
        return "<native fn>"

