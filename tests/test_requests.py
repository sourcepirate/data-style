import unittest
from tests.base import async_test
from data.requests import fetch

class TestAsyncRequests(unittest.TestCase):

	@async_test
	async def test_asyncrequests(self):
		response = await fetch('https://google.com')
		self.assertIsNotNone(response)