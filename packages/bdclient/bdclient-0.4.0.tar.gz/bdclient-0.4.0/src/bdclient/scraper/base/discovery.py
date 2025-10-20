from typing import TypeVar, override

from pydantic import BaseModel

from bdclient.scraper.base.collect import CollectScraper
from bdclient.scraper.base.polling import Polling

Q = TypeVar("Q", bound=BaseModel)
R = TypeVar("R", bound=BaseModel)


class DiscoveryScraper(CollectScraper[Q, R]):
    discover_by: str

    def __init__(
        self,
        api_key: str,
        include_errors: bool = True,
        discovery_only: bool = False,
        limit_per_input: int | None = None,
        polling: Polling | None = None,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(
            api_key=api_key,
            include_errors=include_errors,
            limit_per_input=limit_per_input,
            polling=polling,
            timeout=timeout,
        )
        self._discovery_only = discovery_only

    @override
    def _build_params(self) -> dict[str, str]:
        params = super()._build_params()
        params["type"] = "discover_new"
        params["discover_by"] = self.discover_by
        if self._discovery_only:
            params["discovery_only"] = "true"
        return params
