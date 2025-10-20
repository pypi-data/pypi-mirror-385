from enum import StrEnum
from urllib.parse import urlencode

import httpx


class Device(StrEnum):
    DESKTOP = "desktop"
    MOBILE = "mobile"


class SearchType(StrEnum):
    ALL = "all"
    IMAGES = "isch"
    SHOPPING = "shop"
    NEWS = "nws"
    VIDEOS = "vid"


class GoogleSearch:
    def __init__(
        self,
        api_key: str,
        zone: str,
        domain: str = "google.com",
        country: str | None = None,
        language: str | None = None,
        location: str | None = None,
        uule: str | None = None,
        device: Device = Device.DESKTOP,
        return_json: bool = True,
        timeout: float = 30.0,
    ) -> None:
        self._api_url = "https://api.brightdata.com/request"
        self._api_key = api_key
        self._zone = zone
        self._domain = domain
        self._country = country
        self._language = language
        self._location = location
        self._uule = uule
        self._device = device
        self._return_json = return_json
        self._timeout = timeout

    async def search(
        self,
        keyword: str,
        search_type: SearchType = SearchType.ALL,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        params = {"q": keyword}
        if self._country:
            params["gl"] = self._country
        if self._language:
            params["hl"] = self._language
        if self._location:
            params["location"] = self._location
        if self._uule:
            params["uule"] = self._uule
        if search_type is not SearchType.ALL:
            params["tbm"] = search_type.value
        params["brd_mobile"] = self._device.value
        if self._return_json:
            params["brd_json"] = "1"

        url = f"https://{self._domain}/search?{urlencode(params)}"

        payload = {
            "zone": self._zone,
            "url": url,
            "format": "raw",
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                self._api_url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.text
