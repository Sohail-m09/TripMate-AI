from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from tripmate.graph.nodes import (
    aggregate_results_node,
    dispatch_node,
    flight_node,
    hotel_node,
    itinerary_node,
    orchestrator_node,
    places_node,
    trip_request_node,
    validation_node,
    weather_node,
)

from tripmate.graph.routing import (
    route_after_aggregation,
    route_after_validation,
    route_parallel_agents,
)

from tripmate.state import TravelState


def create_travel_graph() -> StateGraph:

    builder = StateGraph(
        TravelState
    )

    # Register nodes

    builder.add_node(
        "trip_request",
        trip_request_node,
    )

    builder.add_node(
        "orchestrator",
        orchestrator_node,
    )

    builder.add_node(
        "validation",
        validation_node,
    )

    builder.add_node(
        "dispatch",
        dispatch_node,
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

    # -----------------------------------
    # 1. Extract structured trip request
    # -----------------------------------

    builder.add_edge(
        START,
        "trip_request",
    )

    # -----------------------------------
    # 2. Decide which agents are required
    # -----------------------------------

    builder.add_edge(
        "trip_request",
        "orchestrator",
    )

    # -----------------------------------
    # 3. Validate required information
    # -----------------------------------

    builder.add_edge(
        "orchestrator",
        "validation",
    )

    builder.add_conditional_edges(
        "validation",
        route_after_validation,
        {
            "continue": "dispatch",
            "end": END,
        },
    )

    # -----------------------------------
    # 4. Dispatch selected agents
    # -----------------------------------

    builder.add_conditional_edges(
        "dispatch",
        route_parallel_agents,
        [
            "flight",
            "hotel",
            "weather",
            "places",
            "aggregate",
        ],
    )

    # -----------------------------------
    # 5. Fan-in specialist results
    # -----------------------------------

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

    # -----------------------------------
    # 6. Continue to itinerary if needed
    # -----------------------------------

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