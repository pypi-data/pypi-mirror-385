from datetime import datetime

from pydantic import BaseModel

from bdclient.scraper.base import DiscoveryScraper

DATASET_ID = "gd_lk56epmy2i5g7lzu0k"


class Result(BaseModel):
    url: str
    title: str
    youtuber: str | None = None
    youtuber_md5: str | None = None
    video_url: str | None = None
    video_length: float
    likes: int | None = None
    views: int | None = None
    date_posted: datetime
    description: str | None = None
    num_comments: int | None = None
    subscribers: int | None = None
    video_id: str
    channel_url: str


class DiscoverByKeywordQuery(BaseModel):
    keyword: str
    num_of_posts: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    country: str | None = None


class DiscoverByKeyword(DiscoveryScraper[DiscoverByKeywordQuery, Result]):
    dataset_id = DATASET_ID
    discover_by = "keyword"
    query_model = DiscoverByKeywordQuery
    result_model = Result
