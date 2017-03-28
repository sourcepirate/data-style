"""Asynchronous tests for python"""
import asyncio
from functools import wraps

def async_test(func):
    """tests the asynchrounous function on its own event loop"""
    @wraps
    def wrapper(*args, **kwargs):
        """inner function"""
        coro = asyncio.coroutine(func)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper
