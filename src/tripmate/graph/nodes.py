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
from tripmate.agents.orchestrator_agent import (
    run_orchestrator,
)
from tripmate.state import TravelState
from tripmate.schemas import TravelAgentResponse

async def orchestrator_node(
    state: TravelState,
) -> dict:

    decision = await run_orchestrator(
        state["user_query"]
    )

    return {
        "routing_decision": decision
    }


async def flight_node(
    state: TravelState,
) -> dict:

    try:
        result = await run_flight_agent(
            state["user_query"]
        )

        if result.is_complete:
            return {
                "flight_result": result,
                "completed_agents": [
                    "flight"
                ],
            }

        return {
            "flight_result": result,
            "failed_agents": [
                "flight"
            ],
        }

    except Exception as exc:

        failed_result = TravelAgentResponse(
            answer=(
                "The Flight Agent failed: "
                f"{exc}"
            ),
            tools_used=[],
            is_complete=False,
        )

        return {
            "flight_result": failed_result,
            "failed_agents": [
                "flight"
            ],
        }


async def hotel_node(
    state: TravelState,
) -> dict:

    try:
        result = await run_hotel_agent(
            state["user_query"]
        )

        if result.is_complete:
            return {
                "hotel_result": result,
                "completed_agents": [
                    "hotel"
                ],
            }

        return {
            "hotel_result": result,
            "failed_agents": [
                "hotel"
            ],
        }

    except Exception as exc:

        failed_result = TravelAgentResponse(
            answer=(
                "The Hotel Agent failed: "
                f"{exc}"
            ),
            tools_used=[],
            is_complete=False,
        )

        return {
            "hotel_result": failed_result,
            "failed_agents": [
                "hotel"
            ],
        }


async def weather_node(
    state: TravelState,
) -> dict:

    try:
        result = await run_weather_agent(
            state["user_query"]
        )

        if result.is_complete:
            return {
                "weather_result": result,
                "completed_agents": [
                    "weather"
                ],
            }

        return {
            "weather_result": result,
            "failed_agents": [
                "weather"
            ],
        }

    except Exception as exc:

        failed_result = TravelAgentResponse(
            answer=(
                "The Weather Agent failed: "
                f"{exc}"
            ),
            tools_used=[],
            is_complete=False,
        )

        return {
            "weather_result": failed_result,
            "failed_agents": [
                "weather"
            ],
        }


async def places_node(
    state: TravelState,
) -> dict:

    try:
        result = await run_places_agent(
            state["user_query"]
        )

        if result.is_complete:
            return {
                "places_result": result,
                "completed_agents": [
                    "places"
                ],
            }

        return {
            "places_result": result,
            "failed_agents": [
                "places"
            ],
        }

    except Exception as exc:

        failed_result = TravelAgentResponse(
            answer=(
                "The Places Agent failed: "
                f"{exc}"
            ),
            tools_used=[],
            is_complete=False,
        )

        return {
            "places_result": failed_result,
            "failed_agents": [
                "places"
            ],
        }

async def aggregate_results_node(
    state: TravelState,
) -> dict:

    sections = []

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

    if flight_result:

        flight_status = (
            "SUCCESS"
            if flight_result.is_complete
            else "FAILED"
        )

        sections.append(
            (
                f"FLIGHT INFORMATION "
                f"({flight_status}):\n"
                f"{flight_result.answer}"
            )
        )


    if hotel_result:

        hotel_status = (
            "SUCCESS"
            if hotel_result.is_complete
            else "FAILED"
        )

        sections.append(
            (
                f"HOTEL INFORMATION "
                f"({hotel_status}):\n"
                f"{hotel_result.answer}"
            )
        )


    if weather_result:

        weather_status = (
            "SUCCESS"
            if weather_result.is_complete
            else "FAILED"
        )

        sections.append(
            (
                f"WEATHER INFORMATION "
                f"({weather_status}):\n"
                f"{weather_result.answer}"
            )
        )


    if places_result:

        places_status = (
            "SUCCESS"
            if places_result.is_complete
            else "FAILED"
        )

        sections.append(
            (
                f"PLACES INFORMATION "
                f"({places_status}):\n"
                f"{places_result.answer}"
            )
        )

    if sections:
        aggregated_context = "\n\n".join(
            sections
        )
    else:
        aggregated_context = (
            "No specialist information "
            "was required or available."
        )

    updates = {
        "aggregated_context": aggregated_context
    }

    decision = state.get(
        "routing_decision"
    )

    if (
        decision is None
        or "itinerary"
        not in decision.required_agents
    ):
        updates["final_response"] = (
            aggregated_context
        )

    return updates


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