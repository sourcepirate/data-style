"""asynchronous networking"""

import aiohttp
import asyncio
import hashlib
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

DEFAULT_HEADERS = {'User-Agent': 'Mozilla/5.0'}


def url_concat(url, **args):
    """Concatenate url and arguments regardless of whether
    url has existing query parameters.
    """
    if args is None:
        return url
    parsed_url = urlparse(url)
    if isinstance(args, dict):
        parsed_query = parse_qsl(parsed_url.query, keep_blank_values=True)
        parsed_query.extend(args.items())
    else:
        err = "'args' parameter should be dict, list or tuple. Not {0}".format(
            type(args))
        raise TypeError(err)
    final_query = urlencode(parsed_query)
    url = urlunparse((
        parsed_url[0],
        parsed_url[1],
        parsed_url[2],
        parsed_url[3],
        final_query,
        parsed_url[5]))
    return url

async def urlfetch(url="", headers={}, params={}, payload={}, method="GET", loop=None):
    """fetch content from the url"""
    if not url:
        return
    headers.update(DEFAULT_HEADERS)
    async with aiohttp.ClientSession(loop=loop, headers=headers) as session:
        _method = getattr(session, method.lower())
        async with _method(url, params=params, data=payload, allow_redirects=True) as resp:
            result = await resp.text(encoding='ISO-8859-1')
            return result