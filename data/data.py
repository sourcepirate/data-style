"""data item class and fields"""

from data.requests import fetch
from bs4 import BeautifulSoup as _q
from bs4.element import Tag
from urllib.parse import urljoin, urlparse


def is_absoulte(url):
	return bool(urlparse(url).netloc)

def with_metaclass(meta, base=object):
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

    def get_value(self, pq):
        """Extract value from given _q element."""
        raise NotImplementedError("Custom fields have to implement this method")

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
    	if not self.selector:
    		return None
    	tag = q.select(self.selector)
    	mapped = map(lambda x: self.clean(x.text), tag)
    	return next(mapped) if not self.repeated else list(mapped)

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

    def get_value(self, q):
        value = None

        if self.selector is not None:
            tag = q.select(self.selector)
        else:
            tag = q

        if tag and self.attr:
            mapped = map(lambda x: x.get(self.attr), tag)
            return next(mapped) if not self.repeated else list(mapped)
        else:
        	return None

class RelatedItem(object):
    """Set a related  item.
    Defined as a field, a related item could be part of the item it is defined
    on, scraped from the item's inner HTML, or following an URL given by the
    specified attribute, if given.
    Related item(s) will be fetch on first field access.
    """

    def __init__(self, item, selector=None, attr=None):
        super(RelatedItem, self).__init__()
        self.item = item
        self.selector = selector
        self.attr = attr

    def _build_url(self, instance, path):
        url = path
        if path and not is_absolute(path):
            url = urljoin(instance._meta.base_url, path)
        return url

    async def __get__(self, instance, owner):
        value = instance.__dict__.get(self.label, None)
        if value is None:
            # default: use given item object as base
            source = instance._q

            kwargs = {}

            if self.selector:
                # if selector provided, traversing from the item
                source = source.select_one(self.selector)
                kwargs['content'] = str(source)

            if self.attr:
                # if attr is provided,
                # assume we are searching for an url to follow
                html_elem = source[0]
                path = html_elem.get(self.attr)
                source = self._build_url(instance, path)
                kwargs['url']  = source

            related_item = self.item
            print(kwargs)
            value = await related_item.all_from(**kwargs)
            instance.__dict__[self.label] = value
        return value

    def __set__(self, obj, value):
    	raise AttributeError('RelatedItem cannot be set.')

def get_fields(bases, attrs):
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
        self.selector = getattr(meta, 'selector', 'html')
        self.base_url = getattr(meta, 'base_url', '')
        attrs = getattr(meta, '__dict__', {})
        self._qkwargs = {}
        for attr, value in attrs.items():
            if (attr not in self.DATUM_VALUES and not attr.startswith('_')):
            	self._qkwargs[attr] = value

class ItemMeta(type):
    """Metaclass for a item."""

    def __new__(cls, name, bases, attrs):
        # set up related item descriptors
        for field_name, obj in list(attrs.items()):
            if isinstance(obj, RelatedItem):
                obj.label = field_name
        # set up fields
        attrs['_fields'] = get_fields(bases, attrs)
        new_class = super(ItemMeta, cls).__new__(cls, name, bases, attrs)
        new_class._meta = ItemOptions(getattr(new_class, 'Meta', None))
        return new_class


class ItemDoesNotExist(Exception):
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
    	if kwargs.get('url'):
    		pq = await fetch(**kwargs)
    	else:
    		pq = kwargs.get("content", None)

    	if not kwargs.get('relational', False):
    		items = _q(pq).select(cls._meta.selector)
    	else:
    		items = _q(pq)
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
    async def all(cls, path=''):
        """Return all ocurrences of the item."""
        url = urljoin(cls._meta.base_url, path)
        pq_items = await cls._get_items(url=url, **cls._meta._qkwargs)
        return [cls(item=i) for i in pq_items]