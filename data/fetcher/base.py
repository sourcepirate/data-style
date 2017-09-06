"""All fetcher based base class"""

import shutil
import asyncio
import inspect
from data.requests import url_concat

class Fetcher(object):
    
    """Fetcher class acts as a middleware between
    between the fetching function on outgoing request
    all the intermidiate actions can be completed
    with in fetcher"""

    async def fetch(self, url, params={}, loop=None, **extra):
        """fetches the result from fetcher and gives it"""

        result = {}
        parsed_url = url_concat(url, **params)
        if inspect.iscoroutinefunction(self.on_fetch):
            result = await self.on_fetch(parsed_url, loop=None, **extra)
        else:
            loop = loop or asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.on_fetch, parsed_url, **extra)
        return result

    async def on_fetch(self, url, loop=None, **extra):
        """on_fetch base impl"""
        raise NotImplementedError