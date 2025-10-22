from collections.abc import Callable
from typing import Any

import wrapt

from liblaf.grapes import pretty

from ._base import BaseTimer
from ._utils import set_timer


def timed_callable[**P, T](func: Callable[P, T], timer: BaseTimer) -> Callable[P, T]:
    if timer.name is None:
        timer.name = pretty.pretty_func(func)

    @wrapt.decorator
    def wrapper(
        wrapped: Callable[P, T],
        _instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> T:
        __tracebackhide__ = True
        timer.start()
        try:
            return wrapped(*args, **kwargs)
        finally:
            timer.stop()

    func: Callable[P, T] = wrapper(func)
    set_timer(func, timer)
    return func
