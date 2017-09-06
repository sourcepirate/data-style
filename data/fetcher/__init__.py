
import shutil
from .base import Fetcher
from .phatom import PhatomJSFetcher
from .urlfetcher import UrlFetcher

def select_default_fetcher():
    """select default fetcher base on binary available"""
    if shutil.which('phantomjs'):
        return PhatomJSFetcher
    print("You don't have phantomjs installed! please install fro more good experience")
    return UrlFetcher


__all__ = ["Fetcher", "PhatomJSFetcher", "UrlFetcher", "select_default_fetcher"]