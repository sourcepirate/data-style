"""urlfetcher.py

Fetches the plain HTML data from the web. To be parsed by bs4
Not support for javascript.

"""

from .base import Fetcher
from data.requests import urlfetch

class UrlFetcher(Fetcher):

    async def on_fetch(self, url, loop=None, **extra):
        """on data fetch using aiohttp """
        result = await urlfetch(url, loop=loop, **extra)
        return result