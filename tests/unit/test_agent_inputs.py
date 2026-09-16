from tripmate.graph.agent_inputs import (
    build_destination_location,
    build_flight_agent_input,
    build_hotel_agent_input,
    build_places_agent_input,
    build_weather_agent_input,
)


def make_state(**kwargs) -> dict:

    state = {
        "user_query": "Test travel request",
        "completed_agents": [],
        "failed_agents": [],
    }

    state.update(kwargs)

    return state


def test_destination_with_country():

    state = make_state(
        destination="Dubai",
        destination_country="UAE",
    )

    location = build_destination_location(
        state
    )

    assert location == "Dubai, UAE"


def test_destination_without_country():

    state = make_state(
        destination="Singapore",
        destination_country=None,
    )

    location = build_destination_location(
        state
    )

    assert location == "Singapore"


def test_destination_missing():

    state = make_state()

    location = build_destination_location(
        state
    )

    assert location is None


def test_flight_input_prefers_airport_codes():

    state = make_state(
        origin="Mumbai",
        destination="Dubai",
        origin_airport="BOM",
        destination_airport="DXB",
        start_date="2026-11-10",
    )

    agent_input = build_flight_agent_input(
        state
    )

    assert "Origin: BOM" in agent_input
    assert "Destination: DXB" in agent_input
    assert "Departure date: 2026-11-10" in agent_input


def test_flight_input_does_not_fall_back_to_city():

    state = make_state(
        origin="Mumbai",
        destination="Dubai",
        origin_airport=None,
        destination_airport=None,
        start_date="2026-11-10",
    )

    agent_input = build_flight_agent_input(
        state
    )

    assert "Origin: Not provided" in agent_input
    assert "Destination: Not provided" in agent_input

    assert "Origin: Mumbai" not in agent_input
    assert "Destination: Dubai" not in agent_input


def test_hotel_input_uses_geographic_destination():

    state = make_state(
        destination="Dubai",
        destination_airport="DXB",
        destination_country="UAE",
        start_date="2026-11-10",
        end_date="2026-11-15",
        adults=2,
        children=0,
    )

    agent_input = build_hotel_agent_input(
        state
    )

    assert "Location: Dubai, UAE" in agent_input

    assert "DXB" not in agent_input

    assert "Check-in date: 2026-11-10" in agent_input
    assert "Check-out date: 2026-11-15" in agent_input
    assert "Adults: 2" in agent_input
    assert "Children: 0" in agent_input


def test_weather_input_uses_geographic_destination():

    state = make_state(
        destination="Jeddah",
        destination_airport="JED",
        destination_country="Saudi Arabia",
    )

    agent_input = build_weather_agent_input(
        state
    )

    assert "Location: Jeddah, Saudi Arabia" in agent_input

    assert "JED" not in agent_input


def test_places_input_uses_geographic_destination():

    state = make_state(
        destination="Jeddah",
        destination_airport="JED",
        destination_country="Saudi Arabia",
        user_query=(
            "Find tourist attractions in Jeddah."
        ),
    )

    agent_input = build_places_agent_input(
        state
    )

    assert "Location: Jeddah, Saudi Arabia" in agent_input

    assert "JED" not in agent_input

    assert (
        "Find tourist attractions in Jeddah."
        in agent_input
    )


def test_missing_values_are_handled():

    state = make_state()

    flight_input = build_flight_agent_input(
        state
    )

    hotel_input = build_hotel_agent_input(
        state
    )

    weather_input = build_weather_agent_input(
        state
    )

    places_input = build_places_agent_input(
        state
    )

    assert "Not provided" in flight_input

    assert "Not provided" in hotel_input

    assert "Not provided" in weather_input

    assert "Not provided" in places_input