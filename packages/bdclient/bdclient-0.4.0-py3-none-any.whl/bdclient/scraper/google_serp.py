from datetime import datetime as dt

from pydantic import BaseModel

from bdclient.scraper.base import CollectScraper

DATASET_ID = "gd_mfz5x93lmsjjjylob"


class Organic(BaseModel):
    url: str
    rank: int
    link: str
    title: str


class General(BaseModel):
    search_engine: str | None = None
    language: str | None = None
    location: str | None = None
    search_type: str | None = None
    page_title: str | None = None
    datetime: dt | None = None
    query: str | None = None


class Related(BaseModel):
    rank: int | None = None
    link: str | None = None
    text: str | None = None


class Pagination(BaseModel):
    page: str
    link: str


class Result(BaseModel):
    url: str
    keyword: str
    general: General
    related: list[Related]
    pagination: list[Pagination]
    organic: list[Organic]
    people_also_ask: list[str]
    language: str | None = None
    country: str | None = None


class CollectByURLQuery(BaseModel):
    url: str = "https://www.google.com/"
    keyword: str | None = None
    language: str | None = None
    country: str | None = None
    uule: str | None = None
    start_page: int | None = None
    end_page: int | None = None


class CollectByURL(CollectScraper[CollectByURLQuery, Result]):
    dataset_id = DATASET_ID
    query_model = CollectByURLQuery
    result_model = Result
