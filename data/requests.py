"""asynchronous networking"""

import aiohttp
import shutil
import asyncio
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
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


def get_page_source(url, desired_capabilities):
    """get the source"""
    driver = webdriver.PhantomJS(desired_capabilities=desired_capabilities)
    driver.get(url)
    return driver.page_source


async def fetch(url="", params={}, loop=None, capabilities={}):
    """fetch content from the url"""
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 ",
        "(KHTML, like Gecko) Chrome/15.0.87")
    dcap.update(capabilities)
    if not url:
        return
    if shutil.which('phantomjs'):
        loop = loop or asyncio.get_event_loop()
        parsed_url = url_concat(url, **params)
        source = await loop.run_in_executor(None, get_page_source, url, dcap)
        return source
    else:
        print("You don't have phantomjs installed! Please install for more good experience")
        result = await urlfetch(url, params=params, loop=loop)
        return result