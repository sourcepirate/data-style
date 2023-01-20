import unittest
from tests.base import async_test, AsyncMock
from unittest.mock import patch, Mock
from data import data
from data.fetcher import Fetcher
from data.fetcher import PhatomJSFetcher


class StallMan(data.Item):
    """data from stallman.org"""

    urgent_items = data.TextField(repeated=True, selector=".column1 li")

    class Meta:
        base_url = "https://stallman.org/"
        fetcher = PhatomJSFetcher


class TestDataItem(unittest.TestCase):
    """Testing Item class"""

    @async_test
    async def test_my_data_item_is_fetching(self):
        """testing the fetch mock"""
        with patch.object(Fetcher, "fetch", new_callable=AsyncMock) as fm:
            fm.return_value = (
                "<html><div class='column1'><li>1</li></div></html>"
            )
            result = await StallMan.one("/")
            self.assertListEqual(result.urgent_items, ["1"])
