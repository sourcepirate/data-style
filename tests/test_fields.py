"""test all fields"""
import unittest
from unittest.mock import MagicMock, patch
from tests.base import async_test, AsyncMock
from bs4 import BeautifulSoup as q
from data import data
from untangle import Element

class TestBaseField(unittest.TestCase):
    """Testing BaseField"""
    def setUp(self):
        super(TestBaseField, self).setUp()
        self._field = data.BaseField(coerce=lambda x: "{}:{}".format(x, "coerce"))

    def test_get_value(self):
        """test get value should be inherited in base fields"""
        with self.assertRaises(NotImplementedError):
            self._field.get_value(None)

    def test_clean(self):
        """test for clean method in base fields"""
        value = self._field.clean("anyvalue")
        self.assertEqual(value, "anyvalue")

    def test_coerce(self):
        """test corect method in base fields"""
        value = self._field.coerce("coerce")
        self.assertEqual(value, "coerce:coerce")

class TestTextField(unittest.TestCase):
    """Testing TextField"""
    def setUp(self):
        super(TestTextField, self).setUp()
        self._html = q("<ul><li attr='big'>1</li><li attr2='small'>2</li></ul>")

    def test_get_value_for_noneselector(self):
        """testing the get value to be returning none"""
        field = data.TextField()
        self.assertIsNone(field.get_value(""))

    def test_get_value_for_bs4selector(self):
        """testing the get value if bs4 selector is given"""
        field = data.TextField(selector="li")
        self.assertEqual("1", field.get_value(self._html))

    def test_get_repeated_bs4selector(self):
        """testing the get value if repeated is enabled"""
        field = data.TextField(selector="li", repeated=True)
        self.assertListEqual(["1", "2"], field.get_value(self._html))

class TestAttributeValueField(unittest.TestCase):
    """Testing Attribute field"""
    def setUp(self):
        super(TestAttributeValueField, self).setUp()
        self._html = q("<ul><li attr='big'>1</li><li attr2='small'>2</li></ul>")

    def test_get_value_for_noneattr(self):
        """testing the get value if no attr is given"""
        field = data.AttributeValueField()
        self.assertIsNone(field.get_value(None))

    def test_get_value_for_domattr(self):
        """testing the value if attr is given"""
        field = data.AttributeValueField(attr="attr", selector="li")
        self.assertEqual("big", field.get_value(self._html))

    def test_get_value_for_domrepeated(self):
        """testing the value if repated property is enabled"""
        field = data.AttributeValueField(attr="attr", selector="li", repeated=True)
        self.assertListEqual(["big", None], field.get_value(self._html))

class TestHtmlField(unittest.TestCase):
    """Testing Html Field"""
    def setUp(self):
        super(TestHtmlField, self).setUp()
        self._html = q("<ul><li>1</li><li>2</li></ul>")

    def test_get_value_htmlnorepeat(self):
        """testing the get value base on html no repeat"""
        field = data.HtmlField(selector="li")
        self.assertEqual("<li>1</li>", field.get_value(self._html))

    def test_get_value_htmlrepeat(self):
        """testing the get value base on html repeat"""
        field = data.HtmlField(selector="li", repeated=True)
        self.assertListEqual(["<li>1</li>", "<li>2</li>"], field.get_value(self._html))

class TestRelationalField(unittest.TestCase):
    """Testing relational field"""
    def setUp(self):
        super(TestRelationalField, self).setUp()
        self._html = q("<ul><li>1</li><li>2</li></ul>")

    def test_get_value_for_related_item(self):
        """test whether the related item takes html from parent
           and passes it to subitem"""
        item_mock = MagicMock()
        field = data.RelationalField(item_mock, selector="ul")
        value = field.get_value(self._html)
        self.assertEqual(item_mock.call_count, 1)
        self.assertIsNotNone(value)

class TestDomObjectField(unittest.TestCase):
    """Testing dom dict field"""
    def setUp(self):
        super(TestDomObjectField, self).setUp()
        self._html = q("<ul><li>1</li><li>2</li></ul>")

    def test_get_for_domdict_no_repeat(self):
        """test value get if no repeat"""
        field = data.DomObjectField(selector="li")
        element = field.get_value(self._html)
        self.assertIsInstance(element, Element)

    def test_get_for_domdict_repeat(self):
        """test value get if repeat"""
        field = data.DomObjectField(selector="li", repeated=True)
        element = field.get_value(self._html)
        self.assertIsInstance(element, list)

class TestSubPageFields(unittest.TestCase):
    """Testing subpage fields which queries the other pages
       for info
    """
    def setUp(self):
        super(TestSubPageFields, self).setUp()
        self._html = q("<div><a href='/res1'>resource1</a></div>")
        self.q = q

    
    @async_test
    async def test_sub_page_crawls(self):
        """testing value of async fetch with respect to the given
           response
        """
        with patch('data.data.fetch', new_callable=AsyncMock) as fetch_mock:
            fetch_mock.return_value = "<ul><li>1</li></ul>"
            item_mock = MagicMock()
            instance_mock = MagicMock()
            instance_mock._q = self._html
            print(type(instance_mock._q))
            instance_mock._meta.base_url = 'http://gooble.com'
            field = data.SubPageFields(item_mock, link_selector="a")
            response = await field.__get__(instance_mock, None)
            print(response)
            self.assertIsNotNone(response)
            self.assertEquals(item_mock.call_count, 1)