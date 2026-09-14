from typing import (
    Annotated,
    NotRequired,
    TypedDict,
)
from operator import add

from tripmate.schemas import (
    RoutingDecision,
    TravelAgentResponse,
    TripRequest,
)


class TravelState(TypedDict):

    # -----------------------------------
    # Original request
    # -----------------------------------

    user_query: str

    trip_request: NotRequired[
        TripRequest
    ]

    # -----------------------------------
    # User / persistence information
    # -----------------------------------

    user_id: NotRequired[int]

    trip_saved: NotRequired[bool]

    saved_trip_id: NotRequired[int]

    persistence_error: NotRequired[
        str | None
    ]

    # -----------------------------------
    # Memory
    # -----------------------------------

    memory_loaded: NotRequired[
        bool
    ]

    memory_context: NotRequired[
        str | None
    ]

    # -----------------------------------
    # Trip information
    # -----------------------------------

    origin: NotRequired[
        str | None
    ]

    destination: NotRequired[
        str | None
    ]

    origin_airport: NotRequired[
        str | None
    ]

    destination_airport: NotRequired[
        str | None
    ]

    destination_country: NotRequired[
        str | None
    ]

    start_date: NotRequired[
        str | None
    ]

    end_date: NotRequired[
        str | None
    ]

    budget: NotRequired[
        float | None
    ]

    adults: NotRequired[
        int | None
    ]

    children: NotRequired[
        int | None
    ]

    # -----------------------------------
    # Request validation
    # -----------------------------------

    request_valid: NotRequired[
        bool
    ]

    validation_errors: NotRequired[
        list[str]
    ]

    # -----------------------------------
    # Orchestrator routing decision
    # -----------------------------------

    routing_decision: NotRequired[
        RoutingDecision
    ]

    # -----------------------------------
    # Parallel agent tracking
    # -----------------------------------

    completed_agents: Annotated[
        list[str],
        add,
    ]

    failed_agents: Annotated[
        list[str],
        add,
    ]

    # -----------------------------------
    # Specialist agent results
    # -----------------------------------

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

    # -----------------------------------
    # Aggregated specialist information
    # -----------------------------------

    aggregated_context: NotRequired[
        str
    ]

    # -----------------------------------
    # Itinerary result
    # -----------------------------------

    itinerary_result: NotRequired[
        TravelAgentResponse
    ]

    # -----------------------------------
    # Final user-facing values
    # -----------------------------------

    itinerary: NotRequired[
        str
    ]

    final_response: NotRequired[
        str
    ]