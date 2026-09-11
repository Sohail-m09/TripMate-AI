import asyncio
from tripmate.providers.errors import ProviderError
from tripmate.schemas import WeatherResult
from tripmate.providers.factory import (
    get_weather_provider,
)


async def get_current_weather(
    location: str,
) -> WeatherResult:

    provider = get_weather_provider()

    try:
        data = await provider.get_current_weather(
            location
        )

    except ProviderError as exc:
        return WeatherResult(
            success=False,
            error=str(exc),
        )

    if not data["found"]:
        return WeatherResult(
            success=False,
            error=f"Location '{location}' was not found.",
        )

    current = data["current"]

    return WeatherResult(
        success=True,
        location=data["name"],
        country=data["country"],
        temperature=current["temperature_2m"],
        feels_like=current["apparent_temperature"],
        precipitation=current["precipitation"],
        wind_speed=current["wind_speed_10m"],
    )


async def main() -> None:

    result = await get_current_weather(
        "Bhiwandi, Maharashtra, India"
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())