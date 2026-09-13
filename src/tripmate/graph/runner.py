import asyncio

from tripmate.graph.builder import (
    compile_travel_graph,
)


async def main() -> None:

    graph = compile_travel_graph()

    initial_state = {
        "user_id": 1,

        "user_query": (
            "Plan a trip to Jeddah for me. "
            "Search for flights from BOM to JED "
            "on 2026-10-10. "
            "Find hotels in Jeddah from 2026-10-10 "
            "to 2026-10-15 for 2 adults. "
            "Check the current weather in Jeddah, Saudi Arabia. "
            "Find tourist attractions to visit. "
            "Then create a travel itinerary using "
            "the available information."
        ),

        "completed_agents": [],
        "failed_agents": [],
    }

    result = await graph.ainvoke(
        initial_state
    )

    print("\n=== ROUTING DECISION ===")

    routing_decision = result.get(
        "routing_decision"
    )

    if routing_decision:
        print(
            routing_decision.model_dump()
        )

    print("\n=== FLIGHT AGENT ===")

    flight_result = result.get(
        "flight_result"
    )

    if flight_result:
        print(
            flight_result.model_dump()
        )
    else:
        print(
            "Flight Agent was not executed."
        )

    print("\n=== HOTEL AGENT ===")

    hotel_result = result.get(
        "hotel_result"
    )

    if hotel_result:
        print(
            hotel_result.model_dump()
        )
    else:
        print(
            "Hotel Agent was not executed."
        )

    print("\n=== WEATHER AGENT ===")

    weather_result = result.get(
        "weather_result"
    )

    if weather_result:
        print(
            weather_result.model_dump()
        )
    else:
        print(
            "Weather Agent was not executed."
        )

    print("\n=== PLACES AGENT ===")

    places_result = result.get(
        "places_result"
    )

    if places_result:
        print(
            places_result.model_dump()
        )
    else:
        print(
            "Places Agent was not executed."
        )

    print("\n=== COMPLETED AGENTS ===")

    print(
        result.get(
            "completed_agents",
            [],
        )
    )

    print("\n=== FAILED AGENTS ===")

    print(
        result.get(
            "failed_agents",
            [],
        )
    )

    print("\n=== AGGREGATED CONTEXT ===")

    print(
        result.get(
            "aggregated_context",
            "No aggregated context generated.",
        )
    )

    print("\n=== ITINERARY AGENT ===")

    itinerary_result = result.get(
        "itinerary_result"
    )

    if itinerary_result:
        print(
            itinerary_result.model_dump()
        )
    else:
        print(
            "Itinerary Agent was not executed."
        )

    print("\n=== FINAL RESPONSE ===")

    print(
        result.get(
            "final_response",
            "No final response generated.",
        )
    )

    print(
        "\nTRIP SAVED:",
        result.get(
            "trip_saved"
        )
    )

    print(
        "SAVED TRIP ID:",
        result.get(
            "saved_trip_id"
        )
    )

    print(
        "PERSISTENCE ERROR:",
        result.get(
            "persistence_error"
        )
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )