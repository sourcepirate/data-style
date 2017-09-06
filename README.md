## Data-Style

[![Build Status](https://travis-ci.org/sourcepirate/data-style.svg?branch=master)](https://travis-ci.org/sourcepirate/data-style)

a structured scrapper writen on top of beautifulsoup and asyncio. Also provides javascript support(optional) through
phantomjs and selenium.

Phantomjs dependency can be left optional if you don't need javascript support.

## installation

[installing phantomjs](http://phantomjs.org)


## Usage

```python

import asyncio
from data import data

class MovieDetails(data.Item):

    movie_name = data.TextField(selector=".hidden-xs h1")
    movie_year = data.TextField(selector=".hidden-xs h2")

class YifyMovie(data.Item):
    details = data.SubPageFields(MovieDetails, link_selector=".browse-movie-wrap a.browse-movie-link")
    pixel = data.TextField(selector=".browse-movie-tags a")

    class Meta:
        base_url = "https://yts.ag/"

async def mymovie():
    results = await YifyMovie.one("/")
    print(results.pixel)
    details = await results.details
    for detail in details:
        print(detail.movie_name, detail.movie_year)

loop = asyncio.get_event_loop()
loop.run_until_complete(mymovie())


```

Inorder to use desired capabilities along with phantomjs-webdriver. 

```python

class MovieItem(data.Item):
    details = data.SubPageFields(MovieDetails, link_selector=".browse-movie-wrap a.browse-movie-link")
    pixel = data.TextField(selector=".browse-movie-tags a")

    class Meta:
        base_url = "https://yts.ag/"
        desired_capabilities = {
            "phantomjs.page.settings.userAgent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
            "(KHTML, like Gecko) Chrome/15.0.87")
        }

``` 

## Fetchers

Fetchers act as a bridge between url and its assosiated response. To create a 
new fetcher inherit from ```Fetcher``` base class and implement ```on_fetch``` method
on it.

```python

class PhatomJSFetcher(Fetcher):

    """PhatomJS based fetching"""

    def __init__(self, *args, **kwargs):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 ",
        "(KHTML, like Gecko) Chrome/15.0.87")
        self.desired_capabilities = kwargs.get("desired_capabilities", dcap)
        super(PhatomJSFetcher, self).__init__(*args, **kwargs)
    
    def on_fetch(self, url, loop=None, **extra):
        """on fetch callback for phatomjs"""
        driver = webdriver.PhantomJS(desired_capabilities=self.desired_capabilities)
        driver.get(url, **extra)
        return driver.page_source

class MovieItem(data.Item):
    details = data.SubPageFields(MovieDetails, link_selector=".browse-movie-wrap a.browse-movie-link")
    pixel = data.TextField(selector=".browse-movie-tags a")

    class Meta:
        base_url = "https://yts.ag/"
        fetcher = PhatomJSFetcher(desired_capabilities=None)

```

## Develop

```
  python setup.py develop
  python setup.py test
```

## License
MIT
