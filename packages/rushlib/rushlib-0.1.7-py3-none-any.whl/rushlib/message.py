from typing import TypeVar, Generic

from rushlib.text import Error

T = TypeVar('T')

class Message(Generic[T]):
    def __init__(self, var: T, msg: Exception | str | Error = None):
        self.var: T = var

        if isinstance(msg, Error):
            tmp = msg
        elif isinstance(msg, (self, Exception)):
            tmp = Error(msg)
        else:
            raise TypeError(msg)

        self.msg: Error = tmp

    def __iter__(self):
        yield self.var
        yield self.msg