import asyncio
import inspect
import warnings
import random
import shutil
from concurrent.futures import ProcessPoolExecutor

from data.requests import url_concat, urlfetch
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType


class Fetcher(object):

    """Fetcher class acts as a middleware between
    between the fetching function on outgoing request
    all the intermidiate actions can be completed
    with in fetcher"""

    async def fetch(self, url, params={}, loop=None, max_workers=5, **extra):
        """fetches the result from fetcher and gives it"""

        result = {}
        pool = ProcessPoolExecutor(max_workers)
        extra.update({"loop": loop})
        parsed_url = url_concat(url, **params)
        if inspect.iscoroutinefunction(self.on_fetch):
            result = await self.on_fetch(parsed_url, extra)
        else:
            loop = loop or asyncio.get_event_loop()
            result = await loop.run_in_executor(pool, self.on_fetch, parsed_url, extra)
        return result

    async def on_fetch(self, url, extra):
        """on_fetch base impl"""
        raise NotImplementedError


class PhatomJSFetcher(Fetcher):
    """PhatomJS based fetching"""

    def __init__(self, *args, **kwargs):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap[
            "phantomjs.page.settings.userAgent"
        ] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
        self.desired_capabilities = kwargs.get("desired_capabilities", dcap)
        super(PhatomJSFetcher, self).__init__(*args, **kwargs)

    def on_fetch(self, url, extra):
        """on fetch callback for phatomjs"""
        driver = webdriver.PhantomJS(desired_capabilities=self.desired_capabilities)
        driver.get(url)
        return driver.page_source


class PhantomProxyFetcher(PhatomJSFetcher):
    """proxy based fetching for phantomjs"""

    def __init__(self, *args, **kwargs):
        self.service_args = None
        super(PhantomProxyFetcher, self).__init__(*args, **kwargs)

    def on_fetch(self, url, extra):
        """on fetch callback for phatomjs"""
        proxy_list = extra.get("proxy_list")
        if proxy_list:
            proxy = self.get_proxy(proxy_list)
            self.service_args = ["--proxy={}".format(proxy), "--proxy-type=https"]
        driver = webdriver.PhantomJS(
            desired_capabilities=self.desired_capabilities,
            service_args=self.service_args,
        )
        driver.get(url)
        return driver.page_source

    @classmethod
    def get_proxy(cls, proxy_servers):
        """selects a random proxy server from list"""
        server = random.choice(proxy_servers)
        return "https://{}".format(server)


class UrlFetcher(Fetcher):
    async def on_fetch(self, url, extra):
        """on data fetch using aiohttp """
        result = await urlfetch(url, **extra)
        return result


def select_default_fetcher():
    """select default fetcher base on binary available"""
    if shutil.which("phantomjs"):
        return PhatomJSFetcher
    warnings.warn(
        "You don't have phantomjs installed! please install fro more good experience"
    )
    return UrlFetcher
