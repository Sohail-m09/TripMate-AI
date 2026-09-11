from typing import NotRequired, TypedDict

from tripmate.schemas import TravelAgentResponse


class TravelState(TypedDict):

    # Original request
    user_query: str

    # Trip information
    origin: NotRequired[str | None]
    destination: NotRequired[str | None]
    start_date: NotRequired[str | None]
    end_date: NotRequired[str | None]
    budget: NotRequired[float | None]

    # Specialist agent results
    flight_result: NotRequired[TravelAgentResponse]
    hotel_result: NotRequired[TravelAgentResponse]
    weather_result: NotRequired[TravelAgentResponse]
    places_result: NotRequired[TravelAgentResponse]

    # Itinerary result
    itinerary_result: NotRequired[TravelAgentResponse]

    # Final user-facing values
    itinerary: NotRequired[str]
    final_response: NotRequired[str]