import asyncio

from tripmate.graph.builder import (
    compile_travel_graph,
)


async def main() -> None:

    graph = compile_travel_graph()

    initial_state = {
        "user_query": (
            "Plan a Goa trip for me. "
            "Search for flights from BOM to GOI "
            "on 2026-10-10. "
            "Find hotels in Goa from 2026-10-10 "
            "to 2026-10-15 for 2 adults and 3 childrens. "
            "Check the current weather in Goa "
            "and find tourist attractions to visit. "
            "Then create a travel itinerary using "
            "the available information."
        )
    }

    result = await graph.ainvoke(
        initial_state
    )

    print("\n=== FLIGHT AGENT ===")
    flight_result = result.get(
        "flight_result"
    )

    if flight_result:
        print(
            flight_result.model_dump()
        )

    print("\n=== HOTEL AGENT ===")
    hotel_result = result.get(
        "hotel_result"
    )

    if hotel_result:
        print(
            hotel_result.model_dump()
        )

    print("\n=== WEATHER AGENT ===")
    weather_result = result.get(
        "weather_result"
    )

    if weather_result:
        print(
            weather_result.model_dump()
        )

    print("\n=== PLACES AGENT ===")
    places_result = result.get(
        "places_result"
    )

    if places_result:
        print(
            places_result.model_dump()
        )

    print("\n=== ITINERARY AGENT ===")
    itinerary_result = result.get(
        "itinerary_result"
    )

    if itinerary_result:
        print(
            itinerary_result.model_dump()
        )

    print("\n=== FINAL RESPONSE ===")
    print(
        result.get(
            "final_response",
            "No final response generated.",
        )
    )


if __name__ == "__main__":
    asyncio.run(main())