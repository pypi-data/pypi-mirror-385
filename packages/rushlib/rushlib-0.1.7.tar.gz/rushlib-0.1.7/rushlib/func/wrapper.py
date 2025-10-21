from typing import Callable
from functools import wraps


class WrapperFunc:
    def __init__(self, _f, *args, **kwargs):
        self._f = _f
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func: Callable):
        @wraps(self._f)
        def make_wrapper(*args, **kwargs):
            return self._f(*[*self.args, *args], **{**self.kwargs, **kwargs})

        return make_wrapper
