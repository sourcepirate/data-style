import sys, os
import asyncio

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
from data import data, fetcher
from tests.base import async_test

sem = asyncio.Semaphore(5)


class StallMan(data.Item):

    urgent_items = data.TextField(repeated=True, selector=".column1 li")

    class Meta:
        base_url = "https://stallman.org/"
        fetcher = fetcher.PhantomProxyFetcher
        proxy_list = [
            "202.168.244.106:53281",
            "115.178.97.70:63909",
            "203.189.141.162:63909",
        ]


@async_test
async def hello():
    results = await StallMan.all("/")
    print(results[0].urgent_items)


# hello()


class MovieDetails(data.Item):

    movie_name = data.TextField(selector=".hidden-xs h1")
    movie_year = data.TextField(selector=".hidden-xs h2")


class YifyMovie(data.Item):
    details = data.SubPageFields(
        MovieDetails, link_selector=".browse-movie-wrap a.browse-movie-link"
    )
    pixel = data.TextField(selector=".browse-movie-tags a")

    class Meta:
        base_url = "https://yts.ag/"
        fetcher = fetcher.PhatomJSFetcher
        max_workers = 10


@async_test
async def mymovie():
    results = await YifyMovie.one("/")
    print(results.pixel)
    details = await results.details
    for detail in details:
        print(detail.movie_name, detail.movie_year)


mymovie()
