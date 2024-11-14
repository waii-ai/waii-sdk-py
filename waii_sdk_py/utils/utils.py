import asyncio
import functools
import inspect
from typing import TypeVar, Callable, Awaitable, Any

from typing_extensions import ParamSpec

T = TypeVar('T')
P = ParamSpec('P')
def to_async(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    """Decorator to convert a sync method to async"""
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await asyncio.get_event_loop().run_in_executor(
            None, functools.partial(func, *args, **kwargs)
        )
    return wrapper


def wrap_methods_with_async(source_class, target_class):
    for name, method in inspect.getmembers(source_class, predicate=callable):
        if not name.startswith('_') and inspect.isroutine(method):
            async_method = to_async(getattr(source_class, name))
            setattr(target_class, name, async_method)
