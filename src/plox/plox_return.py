from plox.plox_runtime_error import PloxRuntimeError

class PloxReturn(PloxRuntimeError):
   """
   Hacky way to return from function calls
   """

   def __init__(self, value):
      super().__init__(None, None)
      self.value = value
