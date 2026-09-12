from typing import NotRequired, TypedDict, Annotated
from operator import add
from tripmate.schemas import (
    RoutingDecision,
    TravelAgentResponse,
)


class TravelState(TypedDict):

    # Original request
    user_query: str

    # Trip information
    origin: NotRequired[str | None]
    destination: NotRequired[str | None]
    start_date: NotRequired[str | None]
    end_date: NotRequired[str | None]
    budget: NotRequired[float | None]

    # Orchestrator routing decision
    routing_decision: NotRequired[
        RoutingDecision
    ]

    completed_agents: Annotated[
        list[str],
        add,
    ]

    failed_agents: Annotated[
        list[str],
        add,
    ]

    # Specialist agent results
    flight_result: NotRequired[
        TravelAgentResponse
    ]

    hotel_result: NotRequired[
        TravelAgentResponse
    ]

    weather_result: NotRequired[
        TravelAgentResponse
    ]

    places_result: NotRequired[
        TravelAgentResponse
    ]

    # Aggregated specialist information
    aggregated_context: NotRequired[str]

    # Itinerary result
    itinerary_result: NotRequired[
        TravelAgentResponse
    ]

    # Final user-facing values
    itinerary: NotRequired[str]
    final_response: NotRequired[str]