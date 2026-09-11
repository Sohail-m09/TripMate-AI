from typing import Protocol


class WeatherProvider(Protocol):

    async def get_current_weather(
        self,
        location: str,
    ) -> dict:
        ...


class TravelSearchProvider(Protocol):

    async def search_flights(
        self,
        departure_id: str,
        arrival_id: str,
        outbound_date: str,
    ) -> dict:
        ...

    async def search_hotels(
        self,
        location: str,
        check_in_date: str,
        check_out_date: str,
        adults: int,
    ) -> dict:
        ...

    async def search_places(
        self,
        location: str,
        query: str,
    ) -> dict:
        ...