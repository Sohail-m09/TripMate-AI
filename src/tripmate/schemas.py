from pydantic import BaseModel, Field
from typing import Literal
from pydantic import BaseModel, Field



class TravelRequest(BaseModel):
    origin: str | None = Field(
        default=None,
        description="City or place where the trip starts.",
    )

    destination: str | None = Field(
        default=None,
        description="Destination city or place.",
    )

    start_date: str | None = Field(
        default=None,
        description="Trip start date in YYYY-MM-DD format.",
    )

    end_date: str | None = Field(
        default=None,
        description="Trip end date in YYYY-MM-DD format.",
    )

    budget: float | None = Field(
        default=None,
        description="Total travel budget if provided by the user.",
    )

class TravelAgentResponse(BaseModel):
    answer: str = Field(
        description="Final answer returned to the user."
    )

    tools_used: list[str] = Field(
        default_factory=list,
        description="Names of tools used while processing the request."
    )

    is_complete: bool = Field(
        description="Whether the agent completed the user request successfully."
    )

class RoutingDecision(BaseModel):
    required_agents: list[
        Literal[
            "flight",
            "hotel",
            "weather",
            "places",
            "itinerary",
        ]
    ] = Field(
        default_factory=list,
        description=(
            "Specialist agents required to handle "
            "the user's travel request."
        ),
    )

    reason: str = Field(
        description=(
            "Short explanation for why these "
            "specialist agents were selected."
        )
    )

class WeatherResult(BaseModel):
    success: bool
    location: str | None = None
    country: str | None = None
    temperature: float | None = None
    feels_like: float | None = None
    precipitation: float | None = None
    wind_speed: float | None = None
    error: str | None = None


class FlightOption(BaseModel):
    airline: str
    departure_time: str
    arrival_time: str
    duration_minutes: int | None = None
    stops: int
    price: float | None = None


class FlightSearchResult(BaseModel):
    success: bool
    flights: list[FlightOption] = Field(
        default_factory=list
    )
    error: str | None = None


class HotelOption(BaseModel):
    name: str
    rating: float | None = None
    reviews: int | None = None
    hotel_class: str | None = None
    price_per_night: str | None = None
    amenities: list[str] = Field(
        default_factory=list
    )


class HotelSearchResult(BaseModel):
    success: bool
    hotels: list[HotelOption] = Field(
        default_factory=list
    )
    error: str | None = None


class PlaceOption(BaseModel):
    name: str
    place_type: str | None = None
    rating: float | None = None
    reviews: int | None = None
    address: str | None = None
    status: str | None = None


class PlacesSearchResult(BaseModel):
    success: bool
    places: list[PlaceOption] = Field(
        default_factory=list
    )
    error: str | None = None