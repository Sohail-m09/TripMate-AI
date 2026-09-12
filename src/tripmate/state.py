from typing import NotRequired, TypedDict, Annotated
from operator import add
from tripmate.schemas import (
    RoutingDecision,
    TravelAgentResponse,
    TripRequest,
)


class TravelState(TypedDict):

    # Original request
    user_query: str

    trip_request: NotRequired[
        TripRequest
    ]

    # Trip information
    origin: NotRequired[str | None]
    destination: NotRequired[str | None]
    start_date: NotRequired[str | None]
    end_date: NotRequired[str | None]
    budget: NotRequired[float | None]
    adults: NotRequired[int | None]
    children: NotRequired[int | None]

    # Request validation
    request_valid: NotRequired[bool]

    validation_errors: NotRequired[
        list[str]
    ]

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