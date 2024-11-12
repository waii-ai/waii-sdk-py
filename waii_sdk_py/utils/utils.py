import asyncio
import functools
from typing import TypeVar, Callable, Awaitable

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