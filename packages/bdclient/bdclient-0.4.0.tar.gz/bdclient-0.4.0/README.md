# BDClient

An unofficial Python client for Bright Data APIs.

Features:
- Scraper API
    - Google News
    - Google SERP
    - YouTube Videos
- SERP API
    - Google Search
- Unlocker API

## Installation

Installing using pip:
```bash
pip install bdclient
```

Installing using uv:
```bash
uv add bdclient
```

## Usage

Example Scraper API usage:
```python
import asyncio

from bdclient.scraper.youtube_videos import DiscoverByKeyword, DiscoverByKeywordQuery


async def main():
    scraper = DiscoverByKeyword(api_key="your_bright_data_api_key")
    query = DiscoverByKeywordQuery(keyword="How to make pizza")

    results = await scraper.scrape([query])
    for result in results:
        print(result.model_dump_json(indent=4))


if __name__ == "__main__":
    asyncio.run(main())
```

Example SERP API usage:
```python
import asyncio

from bdclient.serp.google_search import GoogleSearch


async def main():
    google_search = GoogleSearch(
        api_key="your_bright_data_api_key",
        zone="your_serp_zone",
    )
    result = await google_search.search(keyword="Pizza toppings")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

Example Unlocker API usage:
```python
import asyncio

from bdclient.unlocker import Unlocker


async def main():
    unlocker = Unlocker(
        api_key="your_bright_data_api_key",
        zone="your_unlocker_zone",
    )

    result = await unlocker.unlock("https://www.bbc.com/news/articles/c8ex2l58en4o")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```
