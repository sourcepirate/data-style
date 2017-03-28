"""asynchronous networking"""

import aiohttp

DEFAULT_HEADERS = {'User-Agent': 'Mozilla/5.0'}
MAPPER = {
    'text/html': 'html',
    'application/json': 'json'
}


async def fetch(url, headers=DEFAULT_HEADERS, params={}, payload={}, method="GET", loop=None):
    """fetch content from the url"""
    async with aiohttp.ClientSession(loop=loop, headers=headers) as session:
        _method = getattr(session, method.lower())
        async with _method(url, params=params, data=payload) as resp:
            ctype = resp.headers.get('Content-Type', 'text/html')
            _response = MAPPER.get(ctype, 'html')
            return await getattr(resp, '_response')

