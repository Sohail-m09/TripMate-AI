import pytest

import tripmate.graph.builder as graph_builder

from tripmate.schemas import (
    RoutingDecision,
    TravelAgentResponse,
)


# -------------------------------------------------
# Initial state helper
# -------------------------------------------------

def make_initial_state(
    user_query: str = "Test travel request",
) -> dict:

    return {
        "user_id": 1,
        "user_query": user_query,
        "completed_agents": [],
        "failed_agents": [],
    }


# -------------------------------------------------
# Test 1:
# Invalid request must stop after validation
# -------------------------------------------------

@pytest.mark.asyncio
async def test_invalid_request_stops_after_validation(
    monkeypatch,
):

    async def fake_trip_request_node(
        state,
    ):
        return {
            "origin": None,
            "destination": "Jeddah",
            "origin_airport": None,
            "destination_airport": "JED",
            "destination_country": "Saudi Arabia",
            "start_date": None,
            "end_date": None,
            "budget": None,
            "adults": None,
            "children": None,
        }

    async def fake_orchestrator_node(
        state,
    ):
        return {
            "routing_decision": RoutingDecision(
                required_agents=[
                    "flight"
                ],
                reason="Flight requested.",
            )
        }

    async def unexpected_node(
        state,
    ):
        raise AssertionError(
            "This node should not run "
            "for an invalid request."
        )

    monkeypatch.setattr(
        graph_builder,
        "trip_request_node",
        fake_trip_request_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "orchestrator_node",
        fake_orchestrator_node,
    )

    # None of these should execute.
    for node_name in (
        "memory_node",
        "flight_node",
        "hotel_node",
        "weather_node",
        "places_node",
        "aggregate_results_node",
        "itinerary_node",
        "persist_trip_node",
    ):
        monkeypatch.setattr(
            graph_builder,
            node_name,
            unexpected_node,
        )

    graph = (
        graph_builder.compile_travel_graph()
    )

    result = await graph.ainvoke(
        make_initial_state(
            "Find me a flight to Jeddah."
        )
    )

    assert result["request_valid"] is False

    assert (
        "Flight search requires an origin."
        in result["validation_errors"]
    )

    assert (
        "Flight search requires a departure date."
        in result["validation_errors"]
    )

    assert (
        "I need some additional information"
        in result["final_response"]
    )

    assert result["completed_agents"] == []

    assert result["failed_agents"] == []


# -------------------------------------------------
# Test 2:
# Hotel + Places + Itinerary graph flow
# -------------------------------------------------

@pytest.mark.asyncio
async def test_selected_agents_and_itinerary_flow(
    monkeypatch,
):

    executed_nodes = []

    async def fake_trip_request_node(
        state,
    ):
        return {
            "origin": None,
            "destination": "Singapore",
            "origin_airport": None,
            "destination_airport": None,
            "destination_country": "Singapore",
            "start_date": "2026-12-10",
            "end_date": "2026-12-14",
            "budget": None,
            "adults": 2,
            "children": 0,
        }

    async def fake_orchestrator_node(
        state,
    ):
        return {
            "routing_decision": RoutingDecision(
                required_agents=[
                    "hotel",
                    "places",
                    "itinerary",
                ],
                reason=(
                    "Hotels, attractions and "
                    "itinerary requested."
                ),
            )
        }

    async def fake_memory_node(
        state,
    ):
        executed_nodes.append(
            "memory"
        )

        return {
            "memory_loaded": True,
            "memory_context": (
                "Previous trip history."
            ),
        }

    async def fake_hotel_node(
        state,
    ):
        executed_nodes.append(
            "hotel"
        )

        result = TravelAgentResponse(
            answer=(
                "Singapore hotel information."
            ),
            tools_used=[
                "find_hotels"
            ],
            is_complete=True,
        )

        return {
            "hotel_result": result,
            "completed_agents": [
                "hotel"
            ],
        }

    async def fake_places_node(
        state,
    ):
        executed_nodes.append(
            "places"
        )

        result = TravelAgentResponse(
            answer=(
                "Singapore attraction information."
            ),
            tools_used=[
                "find_places"
            ],
            is_complete=True,
        )

        return {
            "places_result": result,
            "completed_agents": [
                "places"
            ],
        }

    async def unexpected_specialist(
        state,
    ):
        raise AssertionError(
            "Unselected specialist executed."
        )

    async def fake_itinerary_node(
        state,
    ):
        executed_nodes.append(
            "itinerary"
        )

        assert (
            state["hotel_result"].answer
            == "Singapore hotel information."
        )

        assert (
            state["places_result"].answer
            == "Singapore attraction information."
        )

        assert (
            state["memory_context"]
            == "Previous trip history."
        )

        result = TravelAgentResponse(
            answer=(
                "Final Singapore itinerary."
            ),
            tools_used=[],
            is_complete=True,
        )

        return {
            "itinerary_result": result,
            "itinerary": result.answer,
            "final_response": result.answer,
        }

    async def fake_persist_node(
        state,
    ):
        executed_nodes.append(
            "persist"
        )

        assert (
            state["final_response"]
            == "Final Singapore itinerary."
        )

        return {
            "trip_saved": True,
            "saved_trip_id": 101,
            "persistence_error": None,
        }

    monkeypatch.setattr(
        graph_builder,
        "trip_request_node",
        fake_trip_request_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "orchestrator_node",
        fake_orchestrator_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "memory_node",
        fake_memory_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "hotel_node",
        fake_hotel_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "places_node",
        fake_places_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "flight_node",
        unexpected_specialist,
    )

    monkeypatch.setattr(
        graph_builder,
        "weather_node",
        unexpected_specialist,
    )

    monkeypatch.setattr(
        graph_builder,
        "itinerary_node",
        fake_itinerary_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "persist_trip_node",
        fake_persist_node,
    )

    graph = (
        graph_builder.compile_travel_graph()
    )

    result = await graph.ainvoke(
        make_initial_state(
            (
                "Plan a Singapore trip. "
                "Find hotels and attractions "
                "and create an itinerary."
            )
        )
    )

    assert result["request_valid"] is True

    assert set(
        result["completed_agents"]
    ) == {
        "hotel",
        "places",
    }

    assert result["failed_agents"] == []

    assert (
        result["itinerary"]
        == "Final Singapore itinerary."
    )

    assert result["trip_saved"] is True

    assert result["saved_trip_id"] == 101

    assert "hotel" in executed_nodes
    assert "places" in executed_nodes
    assert "itinerary" in executed_nodes
    assert "persist" in executed_nodes


# -------------------------------------------------
# Test 3:
# No itinerary → aggregate directly to persistence
# -------------------------------------------------

@pytest.mark.asyncio
async def test_graph_without_itinerary_goes_to_persist(
    monkeypatch,
):

    async def fake_trip_request_node(
        state,
    ):
        return {
            "origin": None,
            "destination": "Dubai",
            "origin_airport": None,
            "destination_airport": None,
            "destination_country": "UAE",
            "start_date": None,
            "end_date": None,
            "budget": None,
            "adults": None,
            "children": None,
        }

    async def fake_orchestrator_node(
        state,
    ):
        return {
            "routing_decision": RoutingDecision(
                required_agents=[
                    "weather"
                ],
                reason=(
                    "Only weather was requested."
                ),
            )
        }

    async def fake_memory_node(
        state,
    ):
        return {
            "memory_loaded": False,
            "memory_context": None,
        }

    async def fake_weather_node(
        state,
    ):
        result = TravelAgentResponse(
            answer=(
                "Dubai weather is sunny."
            ),
            tools_used=[
                "current_weather"
            ],
            is_complete=True,
        )

        return {
            "weather_result": result,
            "completed_agents": [
                "weather"
            ],
        }

    async def unexpected_itinerary_node(
        state,
    ):
        raise AssertionError(
            "Itinerary node should not run."
        )

    async def fake_persist_node(
        state,
    ):
        assert (
            "WEATHER INFORMATION (SUCCESS)"
            in state["final_response"]
        )

        assert (
            "Dubai weather is sunny."
            in state["final_response"]
        )

        return {
            "trip_saved": True,
            "saved_trip_id": 102,
            "persistence_error": None,
        }

    monkeypatch.setattr(
        graph_builder,
        "trip_request_node",
        fake_trip_request_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "orchestrator_node",
        fake_orchestrator_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "memory_node",
        fake_memory_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "weather_node",
        fake_weather_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "itinerary_node",
        unexpected_itinerary_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "persist_trip_node",
        fake_persist_node,
    )

    graph = (
        graph_builder.compile_travel_graph()
    )

    result = await graph.ainvoke(
        make_initial_state(
            "What is the weather in Dubai?"
        )
    )

    assert result["request_valid"] is True

    assert result["completed_agents"] == [
        "weather"
    ]

    assert result["failed_agents"] == []

    assert (
        "WEATHER INFORMATION (SUCCESS)"
        in result["final_response"]
    )

    assert (
        "Dubai weather is sunny."
        in result["final_response"]
    )

    assert result.get(
        "itinerary"
    ) is None

    assert result["trip_saved"] is True

    assert result["saved_trip_id"] == 102


# -------------------------------------------------
# Test 4:
# One specialist can fail while graph continues
# -------------------------------------------------

@pytest.mark.asyncio
async def test_partial_agent_failure_still_completes_graph(
    monkeypatch,
):

    async def fake_trip_request_node(
        state,
    ):
        return {
            "origin": "Mumbai",
            "destination": "Dubai",
            "origin_airport": "BOM",
            "destination_airport": "DXB",
            "destination_country": "UAE",
            "start_date": "2026-11-10",
            "end_date": "2026-11-15",
            "budget": None,
            "adults": 2,
            "children": 0,
        }

    async def fake_orchestrator_node(
        state,
    ):
        return {
            "routing_decision": RoutingDecision(
                required_agents=[
                    "flight",
                    "hotel",
                    "itinerary",
                ],
                reason=(
                    "Flight, hotel and itinerary "
                    "were requested."
                ),
            )
        }

    async def fake_memory_node(
        state,
    ):
        return {
            "memory_loaded": False,
            "memory_context": None,
        }

    async def fake_flight_node(
        state,
    ):
        result = TravelAgentResponse(
            answer=(
                "Flight BOM to DXB found."
            ),
            tools_used=[
                "find_flights"
            ],
            is_complete=True,
        )

        return {
            "flight_result": result,
            "completed_agents": [
                "flight"
            ],
        }

    async def fake_hotel_node(
        state,
    ):
        result = TravelAgentResponse(
            answer=(
                "Hotel search failed."
            ),
            tools_used=[
                "find_hotels"
            ],
            is_complete=False,
        )

        return {
            "hotel_result": result,
            "failed_agents": [
                "hotel"
            ],
        }

    async def fake_itinerary_node(
        state,
    ):
        assert (
            "FLIGHT INFORMATION (SUCCESS)"
            in state["aggregated_context"]
        )

        assert (
            "HOTEL INFORMATION (FAILED)"
            in state["aggregated_context"]
        )

        result = TravelAgentResponse(
            answer=(
                "Partial Dubai itinerary."
            ),
            tools_used=[],
            is_complete=True,
        )

        return {
            "itinerary_result": result,
            "itinerary": result.answer,
            "final_response": result.answer,
        }

    async def fake_persist_node(
        state,
    ):
        return {
            "trip_saved": True,
            "saved_trip_id": 103,
            "persistence_error": None,
        }

    monkeypatch.setattr(
        graph_builder,
        "trip_request_node",
        fake_trip_request_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "orchestrator_node",
        fake_orchestrator_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "memory_node",
        fake_memory_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "flight_node",
        fake_flight_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "hotel_node",
        fake_hotel_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "itinerary_node",
        fake_itinerary_node,
    )

    monkeypatch.setattr(
        graph_builder,
        "persist_trip_node",
        fake_persist_node,
    )

    graph = (
        graph_builder.compile_travel_graph()
    )

    result = await graph.ainvoke(
        make_initial_state(
            (
                "Find flights and hotels "
                "for Dubai and create an itinerary."
            )
        )
    )

    assert result["request_valid"] is True

    assert result["completed_agents"] == [
        "flight"
    ]

    assert result["failed_agents"] == [
        "hotel"
    ]

    assert (
        "FLIGHT INFORMATION (SUCCESS)"
        in result["aggregated_context"]
    )

    assert (
        "HOTEL INFORMATION (FAILED)"
        in result["aggregated_context"]
    )

    assert (
        result["final_response"]
        == "Partial Dubai itinerary."
    )

    assert result["trip_saved"] is True

    assert result["saved_trip_id"] == 103