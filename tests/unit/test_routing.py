from tripmate.graph.routing import (
    get_required_agents,
    route_after_aggregation,
    route_after_validation,
    route_parallel_agents,
)
from tripmate.schemas import RoutingDecision


def make_state(
    required_agents: list[str] | None = None,
    **kwargs,
) -> dict:

    state = {
        "user_query": "Test request",
        "completed_agents": [],
        "failed_agents": [],
    }

    if required_agents is not None:

        state["routing_decision"] = RoutingDecision(
            required_agents=required_agents,
            reason="Test routing",
        )

    state.update(kwargs)

    return state


def test_get_required_agents():

    state = make_state(
        [
            "flight",
            "hotel",
        ]
    )

    agents = get_required_agents(
        state
    )

    assert agents == [
        "flight",
        "hotel",
    ]


def test_get_required_agents_without_decision():

    state = make_state()

    agents = get_required_agents(
        state
    )

    assert agents == []


def test_route_all_parallel_agents():

    state = make_state(
        [
            "flight",
            "hotel",
            "weather",
            "places",
            "itinerary",
        ]
    )

    agents = route_parallel_agents(
        state
    )

    assert agents == [
        "flight",
        "hotel",
        "weather",
        "places",
    ]


def test_route_selected_parallel_agents():

    state = make_state(
        [
            "hotel",
            "places",
            "itinerary",
        ]
    )

    agents = route_parallel_agents(
        state
    )

    assert agents == [
        "hotel",
        "places",
    ]


def test_route_parallel_agents_ignores_itinerary():

    state = make_state(
        [
            "itinerary",
        ]
    )

    agents = route_parallel_agents(
        state
    )

    assert agents == [
        "aggregate"
    ]


def test_route_parallel_agents_without_specialists():

    state = make_state(
        []
    )

    agents = route_parallel_agents(
        state
    )

    assert agents == [
        "aggregate"
    ]


def test_route_after_validation_continue():

    state = make_state(
        request_valid=True,
    )

    route = route_after_validation(
        state
    )

    assert route == "continue"


def test_route_after_validation_end():

    state = make_state(
        request_valid=False,
    )

    route = route_after_validation(
        state
    )

    assert route == "end"


def test_route_after_aggregation_to_itinerary():

    state = make_state(
        [
            "hotel",
            "places",
            "itinerary",
        ]
    )

    route = route_after_aggregation(
        state
    )

    assert route == "itinerary"


def test_route_after_aggregation_to_persist():

    state = make_state(
        [
            "hotel",
            "places",
        ]
    )

    route = route_after_aggregation(
        state
    )

    assert route == "persist"