"""data item class and fields"""

from data.requests import fetch
from bs4 import BeautifulSoup as _q
from bs4.element import Tag
from urllib.parse import urljoin, urlparse
from untangle import parse
import asyncio


def is_absoulte(url):
    """check whether the url is absolute"""
    return bool(urlparse(url).netloc)


def with_metaclass(meta, base=object):
    """create a new base for meta class"""
    return meta("NewBase", (base,), {})


class BaseField(object):
    """Base field."""

    def __init__(self, coerce=None):
        super(BaseField, self).__init__()
        self._coerce = coerce

    def clean(self, value):
        """Clean extracted value."""
        return value

    def coerce(self, value):
        """Coerce a cleaned value."""
        if self._coerce is not None:
            value = self._coerce(value)
        return value

    def get_value(self, value):
        """Extract value from given _q element."""
        raise NotImplementedError(
            "Custom fields have to implement this method")

class TextField(BaseField):
    """Simple text field.
    Extract text content from a tag given by 'selector'.
    'selector' is a _q supported selector; if not specified, the Item
    base element is used.
    """

    def __init__(self, selector=None, coerce=None, repeated=False):
        super(TextField, self).__init__(coerce=coerce)
        self.selector = selector
        self.repeated = repeated

    def clean(self, value):
        value = super(TextField, self).clean(value)
        return value.strip()

    def get_value(self, q):
        """get value from query"""
        if not self.selector:
            return None
        tag = q.select(self.selector)
        mapped = map(lambda x: self.clean(x.text), tag)
        try:
            return next(mapped) if not self.repeated else list(mapped)
        except StopIteration:
            return None


class AttributeValueField(TextField):
    """Simple text field, getting an attribute value.
    Extract specific attribute value from a tag given by 'selector'.
    'selector' is a _q supported selector; if not specified, the Item
    base element is used.
    """

    def __init__(self, selector=None, attr=None, coerce=None, repeated=False):
        super(AttributeValueField, self).__init__(
            selector=selector, coerce=coerce, repeated=False)
        self.attr = attr
        self.repeated = repeated

    def get_value(self, q):
        if self.selector is not None:
            tag = q.select(self.selector)
        else:
            tag = q
        if tag and self.attr:
            mapped = map(lambda x: x.get(self.attr), tag)
            return next(mapped) if not self.repeated else list(mapped)
        else:
            return None


class HtmlField(TextField):
    """Extracting only html content from Output. Implement your own clean
       method to sanitize the html"""

    def __init__(self, *args, repeated=False, **kwargs):
        super(HtmlField, self).__init__(*args, **kwargs)
        self.repeated = repeated

    def get_value(self, q):
        if not self.selector:
            return None
        tag = q.select(self.selector)
        mapped = map(lambda x: self.clean(str(x)), tag)
        return next(mapped) if not self.repeated else list(mapped)


class RelationalField(TextField):
    """Get the related fields from page"""

    def __init__(self, item, **kwargs):
        super(RelationalField, self).__init__(**kwargs)
        self.item = item

    def get_value(self, q):
        if not self.selector:
            return []
        tag = q.select(self.selector)
        items = [self.item(item=t) for t in tag]
        return items


class DomObjectField(TextField):
    """Get the dom from page as dict"""

    def __init__(self, **kwargs):
        super(DomObjectField, self).__init__(**kwargs)

    def get_value(self, q):
        if not self.selector:
            return []
        tags = q.select(self.selector)
        fields = map(lambda x: parse(str(x)), tags)
        return next(fields) if not self.repeated else list(fields)


class SubPageFields(object):
    """Get the resources from sub pages"""

    def __init__(self, item, **kwargs):
        self.item = item
        self.link_selector = kwargs.get("link_selector", None)
        super(SubPageFields, self).__init__()

    def _build_url(self, instance, path):
        url = path
        if path and not is_absoulte(path):
            url = urljoin(instance._meta.base_url, path)
        return url

    async def _parse_response(self, instance, link, method="GET"):
        """parse the repsonse to corotine"""
        url = self._build_url(instance, link)
        html = await fetch(url=url, method="GET")
        sub_q = _q(html)
        return self.item(item=sub_q)

    async def __get__(self, instance, owner):
        """overriding the descriptor to get the related links html"""
        page_source = instance._q
        if not self.link_selector:
            return []
        link_selectors = page_source.select(self.link_selector)
        links = map(lambda x: x.get('href'), link_selectors)
        routines = [self._parse_response(instance, link) for link in links]
        results = await asyncio.gather(*routines, return_exceptions=True)
        return results

    def __set__(self, obj, value):
        raise AttributeError('SubPageFields cannot be set.')


def get_fields(bases, attrs):
    """get fields from base classes"""
    fields = [(field_name, attrs.pop(field_name)) for field_name, obj in
              list(attrs.items()) if isinstance(obj, BaseField)]
    # add inherited fields
    for base in bases[::-1]:
        if hasattr(base, '_fields'):
            fields = list(base._fields.items()) + fields
    return dict(fields)


class ItemOptions(object):
    """Meta options for an item."""

    DATUM_VALUES = ('selector', 'base_url')

    def __init__(self, meta):
        self.selector = getattr(meta, 'selector', None)
        self.base_url = getattr(meta, 'base_url', '')
        attrs = getattr(meta, '__dict__', {})
        self._qkwargs = {}
        for attr, value in attrs.items():
            if attr not in self.DATUM_VALUES and not attr.startswith('_'):
                self._qkwargs[attr] = value


class ItemMeta(type):
    """Metaclass for a item."""
    def __new__(mcs, name, bases, attrs):
        attrs['_fields'] = get_fields(bases, attrs)
        new_class = super(ItemMeta, mcs).__new__(mcs, name, bases, attrs)
        new_class._meta = ItemOptions(getattr(new_class, 'Meta', None))
        return new_class


class ItemDoesNotExist(Exception):
    """Item not found"""
    pass


class Item(with_metaclass(ItemMeta)):
    """Base class for any demiurge item."""

    def __init__(self, item=None):
        if item is None or not isinstance(item, Tag):
            raise ValueError('bs4 object expected')
        self._q = item
        for field_name, field in self._fields.items():
            value = field.get_value(self._q)
            clean_field = getattr(self, 'clean_%s' % field_name, None)
            if clean_field:
                value = clean_field(value)
            value = field.coerce(value)
            setattr(self, field_name, value)

    @classmethod
    async def _get_items(cls, **kwargs):
        html = await fetch(**kwargs)
        if cls._meta.selector:
            items = _q(html).select(cls._meta.selector)
        else:
            items = [_q(html)]
        return items

    @classmethod
    async def all_from(cls, **kwargs):
        """Query for items passing args explicitly."""
        pq_items = await cls._get_items(**kwargs)
        return [cls(item=i) for i in pq_items]

    @classmethod
    async def one(cls, path='', index=0):
        """Return ocurrence (the first one, unless specified) of the item."""
        url = urljoin(cls._meta.base_url, path)
        pq_items = await cls._get_items(url=url, **cls._meta._qkwargs)
        item = pq_items[index]
        if not item:
            raise ItemDoesNotExist("%s not found" % cls.__name__)
        return cls(item=item)

    @classmethod
    async def all(cls, path='', **kwargs):
        """Return all ocurrences of the item."""
        url = urljoin(cls._meta.base_url, path)
        kwargs.update(cls._meta._qkwargs)
        pq_items = await cls._get_items(url=url, **kwargs)
        return [cls(item=i) for i in pq_items]
