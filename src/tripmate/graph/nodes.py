from tripmate.agents.flight_agent import (
    run_flight_agent,
)
from tripmate.agents.hotel_agent import (
    run_hotel_agent,
)
from tripmate.agents.itinerary_agent import (
    run_itinerary_agent,
)
from tripmate.agents.places_agent import (
    run_places_agent,
)
from tripmate.agents.weather_agent import (
    run_weather_agent,
)
from tripmate.state import TravelState


async def flight_node(
    state: TravelState,
) -> dict:

    result = await run_flight_agent(
        state["user_query"]
    )

    return {
        "flight_result": result
    }


async def hotel_node(
    state: TravelState,
) -> dict:

    result = await run_hotel_agent(
        state["user_query"]
    )

    return {
        "hotel_result": result
    }


async def weather_node(
    state: TravelState,
) -> dict:

    result = await run_weather_agent(
        state["user_query"]
    )

    return {
        "weather_result": result
    }


async def places_node(
    state: TravelState,
) -> dict:

    result = await run_places_agent(
        state["user_query"]
    )

    return {
        "places_result": result
    }


async def itinerary_node(
    state: TravelState,
) -> dict:

    flight_result = state.get(
        "flight_result"
    )

    hotel_result = state.get(
        "hotel_result"
    )

    weather_result = state.get(
        "weather_result"
    )

    places_result = state.get(
        "places_result"
    )

    result = await run_itinerary_agent(
        user_query=state["user_query"],

        flight_info=(
            flight_result.answer
            if flight_result
            else None
        ),

        hotel_info=(
            hotel_result.answer
            if hotel_result
            else None
        ),

        weather_info=(
            weather_result.answer
            if weather_result
            else None
        ),

        places_info=(
            places_result.answer
            if places_result
            else None
        ),
    )

    return {
        "itinerary_result": result,
        "itinerary": result.answer,
        "final_response": result.answer,
    }