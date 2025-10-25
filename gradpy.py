import time
from typing import Union, Callable

class Grad:
    def __init__(self, caller_locals:dict, caller_globals:dict):
        self.locals, self.globals = {}, {}
        self.update(caller_locals, caller_globals)
    def update(self, caller_locals:dict, caller_globals:dict):
        if not isinstance(caller_locals, dict):
            raise TypeError("Arg 'caller_locals' must be a dict, not '%s'."%type(caller_locals).__name__)
        if not isinstance(caller_globals, dict):
            raise TypeError("Arg 'caller_globals' must be a dict, not '%s'."%type(caller_globals).__name__)
        self.locals, self.globals = caller_locals, caller_globals
    def __str__(self):
        return 'Grad(locals=%s, globals=%s)'%(self.locals, self.globals)
    def From(self, var:str, value:any, use_global:bool=False):
        if not isinstance(var, str):
            raise TypeError("Arg 'var' must be a str, not '%s'."%type(var).__name__)
        if var in self.locals and not use_global:
            self.locals[var] = value
        elif var in self.globals:
            self.globals[var] = value
        else:
            raise NameError("Arg 'var' not found. You may need to update() your vars.")
    def To(self, var:str, value:Union[int, float], func:Callable[[Union[int, float]], Union[int, float]], duration:Union[int, float], use_global:bool=False):
        if not isinstance(var, str):
            raise TypeError("Arg 'var' must be a str, not '%s'."%type(var).__name__)
        if var in self.locals and not use_global:
            v = self.locals[var]
            if not isinstance(v, (int, float)):
                raise ValueError("Arg 'var' must be int or float, not '%s'."%type(v).__name__)
        elif var in self.globals:
            v = self.globals[var]
            if not isinstance(v, (int, float)):
                raise ValueError("Arg 'var' must be int or float, not '%s'."%type(v).__name__)
        else:
            raise NameError("Arg 'var' not found. You may need to update() your vars.")
        if not isinstance(value, (int, float)):
            raise TypeError("Arg 'value' must be int or float, not '%s'."%type(value).__name__)
        if not isinstance(func, Callable):
            raise TypeError("Arg 'func' must be a callable, not '%s'."%type(func).__name__)
        if not hasattr(func, '__code__'):
            raise ValueError("Arg 'func': Not supported c func '%s'."%func.__name__)
        if not hasattr(func.__code__, 'co_argcount'):
            raise ValueError("Arg 'func': Not supported c func '%s'."%func.__name__)
        if func.__code__.co_argcount != 1:
            raise ValueError("Arg count of arg 'func' must be exactly 1, not '%i'."%func.__code__.co_argcount)
        if not isinstance(func(0), (int, float)):
            raise ValueError("Return of arg 'func' must be int or float, not '%s'."%type(func(0)).__name__)
        if not isinstance(duration, (int, float)):
            raise TypeError("Arg 'duration' must be int or float, not '%s'."%type(duration).__name__)
        if duration < 0:
            raise ValueError("Arg 'duration' must be >= 0, not '%s'."%duration)
        try:
            if duration > 0:
                t = time.time()
                while time.time()-t < duration:
                    self.From(var, v+(value-v)*func((time.time()-t)/duration), use_global)
                    time.sleep(0.01)
            self.From(var, v+(value-v)*func(1), use_global)
        except ArithmeticError:
            raise ValueError("Return of arg 'func' must be int or float.")
