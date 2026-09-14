from tripmate.state import TravelState


def build_destination_location(
    state: TravelState,
) -> str | None:

    destination = state.get(
        "destination"
    )

    country = state.get(
        "destination_country"
    )

    if destination and country:
        return f"{destination}, {country}"

    return destination


def build_flight_agent_input(
    state: TravelState,
) -> str:

    origin = (
        state.get("origin_airport")
        or state.get("origin")
    )

    destination = (
        state.get("destination_airport")
        or state.get("destination")
    )

    start_date = state.get(
        "start_date"
    )

    return (
        "Search for flight options using only "
        "the following trip information.\n"
        f"Origin: {origin or 'Not provided'}\n"
        f"Destination: {destination or 'Not provided'}\n"
        f"Departure date: "
        f"{start_date or 'Not provided'}"
    )


def build_hotel_agent_input(
    state: TravelState,
) -> str:

    location = build_destination_location(
        state
    )

    start_date = state.get(
        "start_date"
    )

    end_date = state.get(
        "end_date"
    )

    adults = state.get(
        "adults"
    )

    children = state.get(
        "children"
    )

    return (
        "Search for accommodation strictly within "
        "the following destination.\n"
        f"Location: {location or 'Not provided'}\n"
        f"Check-in date: {start_date or 'Not provided'}\n"
        f"Check-out date: {end_date or 'Not provided'}\n"
        f"Adults: "
        f"{adults if adults is not None else 'Not provided'}\n"
        f"Children: "
        f"{children if children is not None else 'Not provided'}\n"
        "Do not substitute hotels from another city or country."
    )


def build_weather_agent_input(
    state: TravelState,
) -> str:

    location = build_destination_location(
        state
    )

    return (
        "Provide the current weather only for "
        "the following destination.\n"
        f"Location: {location or 'Not provided'}"
    )


def build_places_agent_input(
    state: TravelState,
) -> str:

    location = build_destination_location(
        state
    )

    return (
        "Find places, attractions, or activities "
        "strictly within the following destination.\n"
        f"Location: {location or 'Not provided'}\n"
        "Use the places-related intent from the "
        "original request:\n"
        f"{state['user_query']}"
    )