"""asynchronous networking"""

import aiohttp

DEFAULT_HEADERS = {'User-Agent': 'Mozilla/5.0'}


async def fetch(url="", headers={}, params={}, payload={}, method="GET", loop=None):
    """fetch content from the url"""
    if not url:
        return
    headers.update(DEFAULT_HEADERS)
    async with aiohttp.ClientSession(loop=loop, headers=headers) as session:
        _method = getattr(session, method.lower())
        async with _method(url, params=params, data=payload, allow_redirects=True) as resp:
            result = await resp.text(encoding='ISO-8859-1')
            return result

