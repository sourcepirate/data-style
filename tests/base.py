"""Asynchronous tests for python"""
import asyncio
import inspect
from unittest.mock import Mock


def async_test(func):
    """tests the asynchrounous function on its own event loop"""

    def wrapper(*args, **kwargs):
        """inner function"""

        future = func(*args, **kwargs)
        if inspect.iscoroutine(future):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(future)

    return wrapper


class AsyncMock(Mock):
    """Async mock class with awaitable"""

    def __call__(self, *args, **kwargs):
        sup = super(AsyncMock, self)

        async def coro():
            return sup.__call__(*args, **kwargs)

        return coro()

    def __await__(self):
        return self().__await__()
