from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from tripmate.graph.nodes import (
    aggregate_results_node,
    flight_node,
    hotel_node,
    itinerary_node,
    orchestrator_node,
    places_node,
    weather_node,
)
from tripmate.graph.routing import (
    route_after_aggregation,
    route_parallel_agents,
)
from tripmate.state import TravelState


def create_travel_graph() -> StateGraph:

    builder = StateGraph(
        TravelState
    )

    # Register nodes

    builder.add_node(
        "orchestrator",
        orchestrator_node,
    )

    builder.add_node(
        "flight",
        flight_node,
    )

    builder.add_node(
        "hotel",
        hotel_node,
    )

    builder.add_node(
        "weather",
        weather_node,
    )

    builder.add_node(
        "places",
        places_node,
    )

    builder.add_node(
        "aggregate",
        aggregate_results_node,
    )

    builder.add_node(
        "itinerary",
        itinerary_node,
    )

    # Start with orchestrator

    builder.add_edge(
        START,
        "orchestrator",
    )

    # Fan out selected specialists in parallel

    builder.add_conditional_edges(
        "orchestrator",
        route_parallel_agents,
        [
            "flight",
            "hotel",
            "weather",
            "places",
            "aggregate",
        ],
    )

    # Fan in specialist results

    builder.add_edge(
        "flight",
        "aggregate",
    )

    builder.add_edge(
        "hotel",
        "aggregate",
    )

    builder.add_edge(
        "weather",
        "aggregate",
    )

    builder.add_edge(
        "places",
        "aggregate",
    )

    # Continue to itinerary only when required

    builder.add_conditional_edges(
        "aggregate",
        route_after_aggregation,
        {
            "itinerary": "itinerary",
            "end": END,
        },
    )

    builder.add_edge(
        "itinerary",
        END,
    )

    return builder


def compile_travel_graph():

    builder = create_travel_graph()

    graph = builder.compile()

    return graph