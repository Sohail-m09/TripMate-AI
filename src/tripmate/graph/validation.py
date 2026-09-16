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

    # Geographic locations
    origin = state.get(
        "origin"
    )

    destination = state.get(
        "destination"
    )

    # Airport codes
    origin_airport = state.get(
        "origin_airport"
    )

    destination_airport = state.get(
        "destination_airport"
    )

    # Trip dates
    start_date = state.get(
        "start_date"
    )

    end_date = state.get(
        "end_date"
    )

    # Travelers
    adults = state.get(
        "adults"
    )

    # -----------------------------------
    # Flight validation
    # -----------------------------------

    if "flight" in required_agents:

        if not state.get(
            "origin_airport"
        ):
            errors.append(
                "Flight search requires a "
                "valid origin airport."
            )

        if not state.get(
            "destination_airport"
        ):
            errors.append(
                "Flight search requires a "
                "valid destination airport."
            )

        if not state.get(
            "start_date"
        ):
            errors.append(
                "Flight search requires a "
                "departure date."
            )

    # -----------------------------------
    # Hotel validation
    # -----------------------------------

    if "hotel" in required_agents:

        # Hotels require a real geographic
        # destination, not only an airport code
        if not destination:
            errors.append(
                "Hotel search requires a destination city."
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

    # -----------------------------------
    # Weather validation
    # -----------------------------------

    if "weather" in required_agents:

        # Weather also requires a real location
        if not destination:
            errors.append(
                "Weather search requires a destination city."
            )

    # -----------------------------------
    # Places validation
    # -----------------------------------

    if "places" in required_agents:

        # Places search requires a geographic
        # destination, not an airport code
        if not destination:
            errors.append(
                "Places search requires a destination city."
            )

    return errors