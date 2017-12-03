
import shutil
import warnings
from .base import Fetcher
from .phatom import PhatomJSFetcher
from .urlfetcher import UrlFetcher
from .phatom_proxy import PhantomProxyFetcher

def select_default_fetcher():
    """select default fetcher base on binary available"""
    if shutil.which('phantomjs'):
        return PhatomJSFetcher
    warnings.warn("You don't have phantomjs installed! please install fro more good experience")
    return UrlFetcher


__all__ = ["Fetcher", "PhatomJSFetcher", "UrlFetcher", "select_default_fetcher", "PhantomProxyFetcher"]