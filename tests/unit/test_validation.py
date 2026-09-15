from tripmate.graph.validation import (
    validate_trip_request,
)
from tripmate.schemas import (
    RoutingDecision,
)


def make_state(
    required_agents: list[str],
    **kwargs,
) -> dict:

    state = {
        "user_query": "Test trip request",
        "routing_decision": RoutingDecision(
            required_agents=required_agents,
            reason="Test routing decision",
        ),
        "completed_agents": [],
        "failed_agents": [],
    }

    state.update(kwargs)

    return state


def test_missing_routing_decision():

    state = {
        "user_query": "Test request",
        "completed_agents": [],
        "failed_agents": [],
    }

    errors = validate_trip_request(
        state
    )

    assert errors == [
        "Routing decision is missing."
    ]


def test_valid_flight_request():

    state = make_state(
        ["flight"],
        origin_airport="BOM",
        destination_airport="DXB",
        start_date="2026-11-10",
    )

    errors = validate_trip_request(
        state
    )

    assert errors == []


def test_flight_missing_origin():

    state = make_state(
        ["flight"],
        destination_airport="DXB",
        start_date="2026-11-10",
    )

    errors = validate_trip_request(
        state
    )

    assert (
        "Flight search requires an origin."
        in errors
    )


def test_flight_missing_departure_date():

    state = make_state(
        ["flight"],
        origin_airport="BOM",
        destination_airport="DXB",
    )

    errors = validate_trip_request(
        state
    )

    assert (
        "Flight search requires a departure date."
        in errors
    )


def test_valid_hotel_request():

    state = make_state(
        ["hotel"],
        destination="Dubai",
        start_date="2026-11-10",
        end_date="2026-11-15",
        adults=2,
    )

    errors = validate_trip_request(
        state
    )

    assert errors == []


def test_hotel_missing_required_fields():

    state = make_state(
        ["hotel"],
    )

    errors = validate_trip_request(
        state
    )

    assert (
        "Hotel search requires a destination city."
        in errors
    )

    assert (
        "Hotel search requires a check-in date."
        in errors
    )

    assert (
        "Hotel search requires a check-out date."
        in errors
    )

    assert (
        "Hotel search requires the number of adults."
        in errors
    )


def test_weather_requires_destination():

    state = make_state(
        ["weather"],
    )

    errors = validate_trip_request(
        state
    )

    assert (
        "Weather search requires a destination city."
        in errors
    )


def test_places_requires_destination():

    state = make_state(
        ["places"],
    )

    errors = validate_trip_request(
        state
    )

    assert (
        "Places search requires a destination city."
        in errors
    )


def test_complete_trip_request():

    state = make_state(
        [
            "flight",
            "hotel",
            "weather",
            "places",
            "itinerary",
        ],
        origin="Mumbai",
        destination="Dubai",
        origin_airport="BOM",
        destination_airport="DXB",
        destination_country="UAE",
        start_date="2026-11-10",
        end_date="2026-11-15",
        adults=2,
        children=0,
    )

    errors = validate_trip_request(
        state
    )

    assert errors == []