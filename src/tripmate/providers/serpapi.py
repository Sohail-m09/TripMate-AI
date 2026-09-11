import httpx

from tripmate.config import SERPAPI_API_KEY
from tripmate.providers.errors import (
    ProviderConnectionError,
    ProviderResponseError,
)


SERPAPI_URL = "https://serpapi.com/search"


class SerpApiProvider:

    async def _request(
        self,
        params: dict,
    ) -> dict:

        request_params = {
            **params,
            "api_key": SERPAPI_API_KEY,
        }

        try:
            async with httpx.AsyncClient(
                timeout=20.0
            ) as client:

                response = await client.get(
                    SERPAPI_URL,
                    params=request_params,
                )

                response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise ProviderConnectionError(
                "SerpApi request timed out."
            ) from exc

        except httpx.ConnectError as exc:
            raise ProviderConnectionError(
                "Could not connect to SerpApi."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise ProviderResponseError(
                f"SerpApi returned HTTP "
                f"{exc.response.status_code}."
            ) from exc

        try:
            data = response.json()

        except ValueError as exc:
            raise ProviderResponseError(
                "SerpApi returned invalid JSON."
            ) from exc

        if data.get("error"):
            raise ProviderResponseError(
                f"SerpApi error: {data['error']}"
            )

        return data


    async def search_flights(
        self,
        departure_id: str,
        arrival_id: str,
        outbound_date: str,
    ) -> dict:

        params = {
            "engine": "google_flights",
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "type": 2,
            "travel_class": 1,
            "currency": "INR",
            "hl": "en",
            "gl": "in",
        }

        return await self._request(
            params
        )


    async def search_hotels(
        self,
        location: str,
        check_in_date: str,
        check_out_date: str,
        adults: int,
    ) -> dict:

        params = {
            "engine": "google_hotels",
            "q": f"Hotels in {location}",
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "adults": adults,
            "children": 0,
            "currency": "INR",
            "hl": "en",
            "gl": "in",
        }

        return await self._request(
            params
        )


    async def search_places(
        self,
        location: str,
        query: str,
    ) -> dict:

        params = {
            "engine": "google_maps",
            "q": f"{query} in {location}",
            "type": "search",
            "hl": "en",
            "gl": "in",
        }

        return await self._request(
            params
        )