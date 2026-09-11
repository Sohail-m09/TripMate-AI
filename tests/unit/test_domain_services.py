import pytest

from tripmate.providers.errors import (
    ProviderConnectionError,
)
from tripmate.schemas import (
    FlightSearchResult,
    HotelSearchResult,
    PlacesSearchResult,
    WeatherResult,
)


# ---------------------------------------------------------
# WEATHER
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_weather_service_success(
    monkeypatch,
):
    from tripmate.services import weather_service

    class FakeWeatherProvider:

        async def get_current_weather(
            self,
            location: str,
        ):
            return {
                "found": True,
                "name": "Goa",
                "country": "India",
                "current": {
                    "temperature_2m": 29.0,
                    "apparent_temperature": 32.0,
                    "precipitation": 0.0,
                    "wind_speed_10m": 12.0,
                },
            }

    monkeypatch.setattr(
        weather_service,
        "get_weather_provider",
        lambda: FakeWeatherProvider(),
    )

    result = await weather_service.get_current_weather(
        "Goa"
    )

    assert isinstance(
        result,
        WeatherResult,
    )

    assert result.success is True
    assert result.location == "Goa"
    assert result.country == "India"
    assert result.temperature == 29.0


@pytest.mark.asyncio
async def test_weather_service_provider_error(
    monkeypatch,
):
    from tripmate.services import weather_service

    class FailingWeatherProvider:

        async def get_current_weather(
            self,
            location: str,
        ):
            raise ProviderConnectionError(
                "Weather provider unavailable."
            )

    monkeypatch.setattr(
        weather_service,
        "get_weather_provider",
        lambda: FailingWeatherProvider(),
    )

    result = await weather_service.get_current_weather(
        "Goa"
    )

    assert result.success is False
    assert result.error is not None


# ---------------------------------------------------------
# FLIGHTS
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_flight_service_success(
    monkeypatch,
):
    from tripmate.services import flight_service

    class FakeTravelProvider:

        async def search_flights(
            self,
            departure_id: str,
            arrival_id: str,
            outbound_date: str,
        ):
            return {
                "best_flights": [
                    {
                        "price": 4500,
                        "total_duration": 80,
                        "flights": [
                            {
                                "airline": "IndiGo",
                                "departure_airport": {
                                    "time": "10:00"
                                },
                                "arrival_airport": {
                                    "time": "11:20"
                                },
                            }
                        ],
                    }
                ]
            }

    monkeypatch.setattr(
        flight_service,
        "get_travel_search_provider",
        lambda: FakeTravelProvider(),
    )

    result = await flight_service.search_flights(
        departure_id="BOM",
        arrival_id="GOI",
        outbound_date="2026-10-10",
    )

    assert isinstance(
        result,
        FlightSearchResult,
    )

    assert result.success is True
    assert len(result.flights) == 1

    assert (
        result.flights[0].airline
        == "IndiGo"
    )

    assert (
        result.flights[0].price
        == 4500
    )


# ---------------------------------------------------------
# HOTELS
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_hotel_service_success(
    monkeypatch,
):
    from tripmate.services import hotel_service

    class FakeTravelProvider:

        async def search_hotels(
            self,
            location: str,
            check_in_date: str,
            check_out_date: str,
            adults: int,
        ):
            return {
                "properties": [
                    {
                        "name": "Goa Beach Resort",
                        "overall_rating": 4.5,
                        "reviews": 1200,
                        "hotel_class": "4-star hotel",
                        "rate_per_night": {
                            "lowest": "₹5,000"
                        },
                        "amenities": [
                            "Pool",
                            "Wi-Fi",
                            "Parking",
                        ],
                    }
                ]
            }

    monkeypatch.setattr(
        hotel_service,
        "get_travel_search_provider",
        lambda: FakeTravelProvider(),
    )

    result = await hotel_service.search_hotels(
        location="Goa",
        check_in_date="2026-10-10",
        check_out_date="2026-10-15",
        adults=2,
    )

    assert isinstance(
        result,
        HotelSearchResult,
    )

    assert result.success is True
    assert len(result.hotels) == 1

    assert (
        result.hotels[0].name
        == "Goa Beach Resort"
    )

    assert result.hotels[0].rating == 4.5


# ---------------------------------------------------------
# PLACES
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_places_service_success(
    monkeypatch,
):
    from tripmate.services import places_service

    class FakeTravelProvider:

        async def search_places(
            self,
            location: str,
            query: str,
        ):
            return {
                "local_results": [
                    {
                        "title": "Baga Beach",
                        "rating": 4.4,
                        "reviews": 15000,
                        "type": "Beach",
                        "address": "Goa, India",
                        "open_state": "Open",
                    }
                ]
            }

    monkeypatch.setattr(
        places_service,
        "get_travel_search_provider",
        lambda: FakeTravelProvider(),
    )

    result = await places_service.search_places(
        location="Goa",
        query="beaches",
    )

    assert isinstance(
        result,
        PlacesSearchResult,
    )

    assert result.success is True
    assert len(result.places) == 1

    assert (
        result.places[0].name
        == "Baga Beach"
    )

    assert (
        result.places[0].place_type
        == "Beach"
    )