"""asynchronous networking"""

import aiohttp

DEFAULT_HEADERS = {'User-Agent': 'Mozilla/5.0'}


async def fetch(url="", headers=DEFAULT_HEADERS, params={}, payload={}, method="GET", loop=None):
    """fetch content from the url"""
    if not url:
    	return
    async with aiohttp.ClientSession(loop=loop, headers=headers) as session:
        _method = getattr(session, method.lower())
        async with _method(url, params=params, data=payload) as resp:
            ctype = resp.headers.get('Content-Type', 'text/html')
            return await resp.text(encoding='ISO-8859-1')

