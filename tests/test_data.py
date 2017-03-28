import unittest
from tests.base import async_test
from data import data

class NeedActions(data.Item):
	item = data.TextField(selector=".column1 li")


class StallmanData(data.Item):

	title = data.TextField(selector=".column1 h3")
	action_items = data.RelatedItem(NeedActions)

	class Meta:
		base_url = "https://stallman.org"


class TestData(unittest.TestCase):

	@async_test
	async def test_data_fetch(self):
		response = await StallmanData.all('/')
		print(await response[0].action_items)
		self.assertIsNotNone(response)