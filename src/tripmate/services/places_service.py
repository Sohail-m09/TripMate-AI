import asyncio

from tripmate.providers.errors import ProviderError
from tripmate.providers.factory import (
    get_travel_search_provider,
)
from tripmate.schemas import (
    PlaceOption,
    PlacesSearchResult,
)


async def search_places(
    location: str,
    query: str = "tourist attractions",
) -> PlacesSearchResult:

    provider = get_travel_search_provider()

    try:
        data = await provider.search_places(
            location=location,
            query=query,
        )

    except ProviderError as exc:
        return PlacesSearchResult(
            success=False,
            error=str(exc),
        )

    places = data.get(
        "local_results",
        [],
    )

    if not places:
        return PlacesSearchResult(
            success=False,
            error=(
                "No places were found "
                "for the requested location."
            ),
        )

    results: list[PlaceOption] = []

    for place in places[:5]:

        name = place.get(
            "title",
            "Unknown Place",
        )

        rating = place.get(
            "rating",
        )

        reviews = place.get(
            "reviews",
        )

        place_type = place.get(
            "type",
        )

        address = place.get(
            "address",
        )

        open_state = place.get(
            "open_state",
        )

        result = PlaceOption(
            name=name,

            place_type=(
                str(place_type)
                if place_type
                else None
            ),

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

            address=(
                str(address)
                if address
                else None
            ),

            status=(
                str(open_state)
                if open_state
                else None
            ),
        )

        results.append(result)

    return PlacesSearchResult(
        success=True,
        places=results,
    )


async def main() -> None:

    result = await search_places(
        location="Goa",
        query="tourist attractions",
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())