import httpx

from tripmate.providers.errors import (
    ProviderConnectionError,
    ProviderResponseError,
)


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


class OpenMeteoProvider:

    async def _request(
        self,
        client: httpx.AsyncClient,
        url: str,
        params: dict,
    ) -> dict:

        try:
            response = await client.get(
                url,
                params=params,
            )

            response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise ProviderConnectionError(
                "Open-Meteo request timed out."
            ) from exc

        except httpx.ConnectError as exc:
            raise ProviderConnectionError(
                "Could not connect to Open-Meteo."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise ProviderResponseError(
                f"Open-Meteo returned HTTP "
                f"{exc.response.status_code}."
            ) from exc

        try:
            return response.json()

        except ValueError as exc:
            raise ProviderResponseError(
                "Open-Meteo returned invalid JSON."
            ) from exc


    async def get_current_weather(
        self,
        location: str,
    ) -> dict:

        async with httpx.AsyncClient(
            timeout=10.0
        ) as client:

            location_data = await self._request(
                client=client,
                url=GEOCODING_URL,
                params={
                    "name": location,
                    "count": 1,
                    "language": "en",
                    "format": "json",
                },
            )

            results = location_data.get(
                "results"
            )

            if not results:
                return {
                    "found": False,
                    "location": location,
                }

            place = results[0]

            latitude = place["latitude"]
            longitude = place["longitude"]

            weather_data = await self._request(
                client=client,
                url=WEATHER_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": (
                        "temperature_2m,"
                        "apparent_temperature,"
                        "precipitation,"
                        "wind_speed_10m"
                    ),
                    "timezone": "auto",
                },
            )

            current = weather_data.get(
                "current"
            )

            if not current:
                raise ProviderResponseError(
                    "Open-Meteo returned no current weather data."
                )

            return {
                "found": True,
                "name": place["name"],
                "country": place.get(
                    "country",
                    "",
                ),
                "current": current,
            }