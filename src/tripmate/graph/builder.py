from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from tripmate.graph.nodes import (
    flight_node,
    hotel_node,
    itinerary_node,
    places_node,
    weather_node,
)
from tripmate.state import TravelState


def create_travel_graph() -> StateGraph:

    builder = StateGraph(
        TravelState
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
        "itinerary",
        itinerary_node,
    )

    builder.add_edge(
        START,
        "flight",
    )

    builder.add_edge(
        "flight",
        "hotel",
    )

    builder.add_edge(
        "hotel",
        "weather",
    )

    builder.add_edge(
        "weather",
        "places",
    )

    builder.add_edge(
        "places",
        "itinerary",
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