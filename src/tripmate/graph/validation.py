from tripmate.state import TravelState


def validate_trip_request(
    state: TravelState,
) -> list[str]:

    errors = []

    decision = state.get(
        "routing_decision"
    )

    if decision is None:
        return [
            "Routing decision is missing."
        ]

    required_agents = (
        decision.required_agents
    )

    origin = state.get(
        "origin"
    )

    destination = state.get(
        "destination"
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

    if "flight" in required_agents:

        if not origin:
            errors.append(
                "Flight search requires an origin."
            )

        if not destination:
            errors.append(
                "Flight search requires a destination."
            )

        if not start_date:
            errors.append(
                "Flight search requires a departure date."
            )

    if "hotel" in required_agents:

        if not destination:
            errors.append(
                "Hotel search requires a destination."
            )

        if not start_date:
            errors.append(
                "Hotel search requires a check-in date."
            )

        if not end_date:
            errors.append(
                "Hotel search requires a check-out date."
            )

        if adults is None:
            errors.append(
                "Hotel search requires the number of adults."
            )

    if "weather" in required_agents:

        if not destination:
            errors.append(
                "Weather search requires a destination."
            )

    if "places" in required_agents:

        if not destination:
            errors.append(
                "Places search requires a destination."
            )

    return errors