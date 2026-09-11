import asyncio

from tripmate.providers.errors import ProviderError
from tripmate.providers.factory import (
    get_travel_search_provider,
)
from tripmate.schemas import (
    HotelOption,
    HotelSearchResult,
)


async def search_hotels(
    location: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 2,
) -> HotelSearchResult:

    provider = get_travel_search_provider()

    try:
        data = await provider.search_hotels(
            location=location,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            adults=adults,
        )

    except ProviderError as exc:
        return HotelSearchResult(
            success=False,
            error=str(exc),
        )

    properties = data.get(
        "properties",
        [],
    )

    if not properties:
        return HotelSearchResult(
            success=False,
            error=(
                "No hotels were found for "
                "the requested location and dates."
            ),
        )

    results: list[HotelOption] = []

    for hotel in properties[:3]:

        name = hotel.get(
            "name",
            "Unknown Hotel",
        )

        rating = hotel.get(
            "overall_rating",
        )

        reviews = hotel.get(
            "reviews",
        )

        hotel_class = hotel.get(
            "hotel_class",
        )

        rate = hotel.get(
            "rate_per_night",
            {},
        )

        price = rate.get(
            "lowest",
        )

        amenities = hotel.get(
            "amenities",
            [],
        )

        top_amenities = amenities[:3]

        result = HotelOption(
            name=name,

            rating=(
                float(rating)
                if isinstance(rating, (int, float))
                else None
            ),

            reviews=(
                int(reviews)
                if isinstance(reviews, int)
                else None
            ),

            hotel_class=(
                str(hotel_class)
                if hotel_class
                else None
            ),

            price_per_night=(
                str(price)
                if price
                else None
            ),

            amenities=top_amenities,
        )

        results.append(result)

    return HotelSearchResult(
        success=True,
        hotels=results,
    )


async def main() -> None:

    result = await search_hotels(
        location="Goa",
        check_in_date="2026-10-10",
        check_out_date="2026-10-15",
        adults=2,
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())