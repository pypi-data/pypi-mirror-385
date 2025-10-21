import datetime
import functools
from collections.abc import Callable, Iterable, Mapping
from typing import Any, Literal, Protocol, TypedDict, overload

import cytoolz as toolz
import joblib
import wrapt

from liblaf.grapes.conf import config

from ._wrapt import wrapt_setattr


class MemorizedFunc[**P, T](Protocol):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T: ...


class Metadata(TypedDict): ...


@overload
def cache[**P, T](
    func: Callable[P, T],
    /,
    *,
    memory: joblib.Memory | None = ...,
    # memory.cache() params
    ignore: list[str] | None = ...,
    verbose: int | None = ...,
    mmap_mode: Literal["r+", "r", "w+", "c"] | None = ...,
    cache_validation_callback: Callable[[Metadata], bool] | None = ...,
    # memory.reduce_size() params
    bytes_limit: int | str | None = ...,
    items_limit: int | None = ...,
    age_limit: datetime.timedelta | None = ...,
) -> MemorizedFunc[P, T]: ...
@overload
def cache[**P, T](
    *,
    memory: joblib.Memory | None = None,
    # memory.cache() params
    ignore: list[str] | None = ...,
    verbose: int | None = ...,
    mmap_mode: Literal["r+", "r", "w+", "c"] | None = ...,
    cache_validation_callback: Callable[[Metadata], bool] | None = ...,
    # memory.reduce_size() params
    bytes_limit: int | str | None = ...,
    items_limit: int | None = ...,
    age_limit: datetime.timedelta | None = ...,
) -> Callable[[Callable[P, T]], MemorizedFunc[P, T]]: ...
def cache(func: Callable | None = None, /, **kwargs: Any) -> Any:
    if func is None:
        return functools.partial(cache, **kwargs)
    memory: joblib.Memory | None = kwargs.pop("memory", None)
    if memory is None:
        memory = new_memory()
    cache_kwargs: dict[str, Any] = _filter_keys(
        kwargs, ("ignore", "verbose", "mmap_mode", "cache_validation_callback")
    )
    reduce_size_kwargs: dict[str, Any] = _filter_keys(
        kwargs, ("bytes_limit", "items_limit", "age_limit")
    )
    reduce_size_kwargs.setdefault("bytes_limit", config.joblib.memory.bytes_limit)

    @wrapt.function_wrapper
    def wrapper[**P, T](
        wrapped: Callable[P, T], _instance: Any, args: tuple, kwargs: dict[str, Any]
    ) -> T:
        result: Any = wrapped(*args, **kwargs)
        memory.reduce_size(**reduce_size_kwargs)
        return result

    func = memory.cache(func, **cache_kwargs)
    func = wrapper(func)
    wrapt_setattr(func, "memory", memory)
    return func


@functools.cache
def new_memory() -> joblib.Memory:
    return joblib.Memory(location=config.joblib.memory.location)


def _filter_keys[KT, VT](mapping: Mapping[KT, VT], keys: Iterable[KT]) -> dict[KT, VT]:
    return toolz.keyfilter(lambda k: k in keys, mapping)
