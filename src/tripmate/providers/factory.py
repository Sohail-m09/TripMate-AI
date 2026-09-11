from tripmate.providers.base import (
    TravelSearchProvider,
    WeatherProvider,
)
from tripmate.providers.open_meteo import (
    OpenMeteoProvider,
)
from tripmate.providers.serpapi import (
    SerpApiProvider,
)


def get_weather_provider(
) -> WeatherProvider:

    return OpenMeteoProvider()


def get_travel_search_provider(
) -> TravelSearchProvider:

    return SerpApiProvider()