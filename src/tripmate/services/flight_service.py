import asyncio
from tripmate.providers.errors import ProviderError
from tripmate.schemas import (
    FlightOption,
    FlightSearchResult,
)
from tripmate.providers.factory import (
    get_travel_search_provider,
)


async def search_flights(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
) -> FlightSearchResult:

    provider = get_travel_search_provider()

    try:
        data = await provider.search_flights(
            departure_id=departure_id,
            arrival_id=arrival_id,
            outbound_date=outbound_date,
        )

    except ProviderError as exc:
        return FlightSearchResult(
            success=False,
            error=str(exc),
        )

    data = await provider.search_flights(
        departure_id=departure_id,
        arrival_id=arrival_id,
        outbound_date=outbound_date,
    )

    flights = (
        data.get("best_flights")
        or data.get("other_flights")
        or []
    )

    if not flights:
        return FlightSearchResult(
            success=False,
            error="No flights were found for the requested route.",
        )

    results: list[FlightOption] = []

    for option in flights[:3]:

        segments = option.get(
            "flights",
            []
        )

        if not segments:
            continue

        first_segment = segments[0]
        last_segment = segments[-1]

        departure = first_segment.get(
            "departure_airport",
            {}
        )

        arrival = last_segment.get(
            "arrival_airport",
            {}
        )

        airlines = []

        for segment in segments:

            airline = segment.get(
                "airline"
            )

            if (
                airline
                and airline not in airlines
            ):
                airlines.append(
                    airline
                )

        price = option.get(
            "price",
            "N/A"
        )

        duration = option.get(
            "total_duration",
            "N/A"
        )

        stops = max(
            len(segments) - 1,
            0
        )

        result = FlightOption(
            airline=", ".join(airlines),
            departure_time=departure.get(
                "time",
                "N/A",
            ),
            arrival_time=arrival.get(
                "time",
                "N/A",
            ),
            duration_minutes=(
                duration
                if isinstance(duration, int)
                else None
            ),
            stops=stops,
            price=(
                float(price)
                if isinstance(price, (int, float))
                else None
            ),
    )

        results.append(result)

    return FlightSearchResult(
        success=True,
        flights=results,
    )


async def main() -> None:

    result = await search_flights(
        departure_id="BOM",
        arrival_id="GOI",
        outbound_date="2026-10-10",
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())