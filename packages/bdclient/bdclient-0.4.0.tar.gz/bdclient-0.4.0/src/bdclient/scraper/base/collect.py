import asyncio
import logging
import random
from typing import Generic, TypeVar

import httpx
from pydantic import BaseModel

from bdclient.scraper.base.polling import Polling

Q = TypeVar("Q", bound=BaseModel)
R = TypeVar("R", bound=BaseModel)

logger = logging.getLogger(__name__)


class CollectScraper(Generic[Q, R]):
    dataset_id: str
    query_model: type[Q]
    result_model: type[R]

    def __init__(
        self,
        api_key: str,
        include_errors: bool = True,
        limit_per_input: int | None = None,
        polling: Polling | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._include_errors = include_errors
        self._limit_per_input = limit_per_input
        if polling is None:
            self._polling = Polling()
        else:
            self._polling = polling
        self._timeout = timeout

    def _build_params(self) -> dict[str, str]:
        params: dict[str, str] = {}
        params["dataset_id"] = f"{self.dataset_id}"
        if self._include_errors:
            params["include_errors"] = "true"
        if self._limit_per_input is not None:
            params["limit_per_input"] = str(self._limit_per_input)
        return params

    async def scrape(self, queries: list[Q]) -> list[R]:
        snapshot_id = await self.start_scraping(queries)
        results = await self.wait_for_snapshot_results(snapshot_id)
        return results

    async def start_scraping(self, queries: list[Q]) -> str:
        api_url = "https://api.brightdata.com/datasets/v3/trigger"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        params = self._build_params()
        data = [query.model_dump(mode="json", exclude_none=True) for query in queries]

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                api_url,
                headers=headers,
                params=params,
                json=data,
            )
            response.raise_for_status()
            response_json = response.json()

            snapshot_id = str(response_json["snapshot_id"])
            return snapshot_id

    async def wait_for_snapshot_results(self, snapshot_id: str) -> list[R]:
        api_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
        headers = {"Authorization": f"Bearer {self._api_key}"}
        params = {"format": "json"}

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            current_interval = self._polling.poll_interval
            for attempt in range(1, self._polling.max_retries + 1):
                logger.debug(
                    f"Polling attempt {attempt} for snapshot {snapshot_id} after "
                    f"{current_interval:.2f} seconds..."
                )
                await asyncio.sleep(current_interval)

                response = await client.get(
                    api_url,
                    headers=headers,
                    params=params,
                )
                response.raise_for_status()
                response_json = response.json()
                if "status" in response_json:
                    if attempt < self._polling.max_retries:
                        next_interval = current_interval * self._polling.backoff_factor
                        if self._polling.max_poll_interval is not None:
                            next_interval = min(
                                next_interval, self._polling.max_poll_interval
                            )
                        if self._polling.jitter:
                            next_interval += random.uniform(
                                0, float(self._polling.jitter)
                            )
                        current_interval = next_interval
                    continue
                else:
                    return [
                        self.result_model.model_validate(item) for item in response_json
                    ]

            raise RuntimeError(
                f"Failed to retrieve results in time (snapshot {snapshot_id} still processing)."
            )
