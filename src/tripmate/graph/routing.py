from typing import Literal

from tripmate.state import TravelState


def get_required_agents(
    state: TravelState,
) -> list[str]:

    decision = state.get(
        "routing_decision"
    )

    if decision is None:
        return []

    return decision.required_agents


def route_parallel_agents(
    state: TravelState,
) -> list[str]:

    required_agents = get_required_agents(
        state
    )

    parallel_agents = []

    for agent in (
        "flight",
        "hotel",
        "weather",
        "places",
    ):

        if agent in required_agents:
            parallel_agents.append(
                agent
            )

    # Example: itinerary-only request.
    # There are no specialist branches,
    # so continue directly to aggregation.
    if not parallel_agents:
        return [
            "aggregate"
        ]

    return parallel_agents


def route_after_aggregation(
    state: TravelState,
) -> Literal[
    "itinerary",
    "end",
]:

    required_agents = get_required_agents(
        state
    )

    if "itinerary" in required_agents:
        return "itinerary"

    return "end"