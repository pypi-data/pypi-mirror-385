import httpx


class Unlocker:
    def __init__(
        self,
        api_key: str,
        zone: str,
        country: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._zone = zone
        self._country = country
        self._timeout = timeout

    async def unlock(self, url: str) -> str:
        api_url = "https://api.brightdata.com/request"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        payload = {
            "zone": self._zone,
            "url": url,
            "format": "raw",
        }
        if self._country:
            payload["country"] = self._country

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                api_url,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return response.text
