
import random
import shutil
from .base import Fetcher
from selenium import webdriver
from .phatom import PhatomJSFetcher
from selenium.webdriver.common.proxy import Proxy, ProxyType


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
            self.service_args = [
                "--proxy={}".format(proxy),
                "--proxy-type=https"
            ]
        driver = webdriver.PhantomJS(desired_capabilities=self.desired_capabilities, service_args=self.service_args)
        driver.get(url)
        return driver.page_source

    @classmethod
    def get_proxy(cls, proxy_servers):
        """selects a random proxy server from list"""
        server = random.choice(proxy_servers)
        return "https://{}".format(server)