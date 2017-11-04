"""phatom.py"""

from .base import Fetcher
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class PhatomJSFetcher(Fetcher):

    """PhatomJS based fetching"""

    def __init__(self, *args, **kwargs):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
        self.desired_capabilities = kwargs.get("desired_capabilities", dcap)
        super(PhatomJSFetcher, self).__init__(*args, **kwargs)
    
    def on_fetch(self, url, extra):
        """on fetch callback for phatomjs"""
        driver = webdriver.PhantomJS(desired_capabilities=self.desired_capabilities)
        driver.get(url)
        return driver.page_source