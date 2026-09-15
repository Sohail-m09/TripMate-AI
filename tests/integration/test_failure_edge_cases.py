import pytest
import pytest_asyncio

from httpx import (
    ASGITransport,
    AsyncClient,
)

from tripmate.api.main import app
from tripmate.schemas import (
    RoutingDecision,
)

import tripmate.api.routes.trips as trips_routes
import tripmate.api.routes.users as users_routes
import tripmate.graph.nodes as graph_nodes


# -------------------------------------------------
# FastAPI client
# -------------------------------------------------

@pytest_asyncio.fixture
async def client():

    transport = ASGITransport(
        app=app
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:

        yield test_client


# -------------------------------------------------
# Memory failure isolation
# -------------------------------------------------

@pytest.mark.asyncio
async def test_memory_failure_does_not_crash_workflow(
    monkeypatch,
):

    async def fake_memory_builder(
        user_id,
        limit=3,
    ):
        raise RuntimeError(
            "Database unavailable"
        )

    monkeypatch.setattr(
        graph_nodes,
        "build_trip_memory_context",
        fake_memory_builder,
    )

    state = {
        "user_id": 1,
        "routing_decision":
            RoutingDecision(
                required_agents=[
                    "itinerary"
                ],
                reason=(
                    "Itinerary requested."
                ),
            ),
    }

    result = await graph_nodes.memory_node(
        state
    )

    assert result[
        "memory_loaded"
    ] is False

    assert result[
        "memory_context"
    ] is None


@pytest.mark.asyncio
async def test_memory_skipped_without_user_id():

    state = {
        "routing_decision":
            RoutingDecision(
                required_agents=[
                    "itinerary"
                ],
                reason=(
                    "Itinerary requested."
                ),
            ),
    }

    result = await graph_nodes.memory_node(
        state
    )

    assert result[
        "memory_loaded"
    ] is False

    assert result[
        "memory_context"
    ] is None


# -------------------------------------------------
# Specialist failure isolation
# -------------------------------------------------

@pytest.mark.asyncio
async def test_flight_agent_exception_is_isolated(
    monkeypatch,
):

    async def fake_run_flight_agent(
        user_query,
    ):
        raise RuntimeError(
            "Flight provider unavailable"
        )

    monkeypatch.setattr(
        graph_nodes,
        "run_flight_agent",
        fake_run_flight_agent,
    )

    state = {
        "origin": "Mumbai",
        "destination": "Dubai",
        "origin_airport": "BOM",
        "destination_airport": "DXB",
        "start_date": "2026-11-10",
    }

    result = await graph_nodes.flight_node(
        state
    )

    assert result[
        "failed_agents"
    ] == [
        "flight"
    ]

    assert result[
        "flight_result"
    ].is_complete is False

    assert (
        "Flight Agent failed"
        in result[
            "flight_result"
        ].answer
    )

    assert (
        "Flight provider unavailable"
        in result[
            "flight_result"
        ].answer
    )


# -------------------------------------------------
# Persistence failure isolation
# -------------------------------------------------

@pytest.mark.asyncio
async def test_persistence_failure_does_not_crash(
    monkeypatch,
):

    async def fake_save_trip(
        state,
    ):
        raise RuntimeError(
            "Database write failed"
        )

    monkeypatch.setattr(
        graph_nodes,
        "save_trip_from_state",
        fake_save_trip,
    )

    state = {
        "user_id": 1,
        "user_query": (
            "Plan a Dubai trip."
        ),
        "final_response": (
            "Generated itinerary."
        ),
    }

    result = (
        await graph_nodes.persist_trip_node(
            state
        )
    )

    assert result[
        "trip_saved"
    ] is False

    assert result[
        "saved_trip_id"
    ] is None

    assert (
        "Database write failed"
        in result[
            "persistence_error"
        ]
    )


# -------------------------------------------------
# Unexpected user creation failure
# -------------------------------------------------

@pytest.mark.asyncio
async def test_create_user_internal_failure(
    client,
    monkeypatch,
):

    async def fake_register_user(
        name,
        email,
    ):
        raise RuntimeError(
            "Database unavailable"
        )

    monkeypatch.setattr(
        users_routes,
        "register_user",
        fake_register_user,
    )

    response = await client.post(
        "/users",
        json={
            "name": "Sohail",
            "email": "sohail@example.com",
        },
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": (
            "Failed to create user: "
            "Database unavailable"
        )
    }


# -------------------------------------------------
# User validation failure before graph
# -------------------------------------------------

@pytest.mark.asyncio
async def test_plan_trip_user_validation_failure(
    client,
    monkeypatch,
):

    async def fake_get_user(
        user_id,
    ):
        raise RuntimeError(
            "Database unavailable"
        )

    monkeypatch.setattr(
        trips_routes,
        "get_user",
        fake_get_user,
    )

    response = await client.post(
        "/trips/plan",
        json={
            "user_id": 1,
            "user_query": (
                "Plan a trip to Dubai."
            ),
        },
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": (
            "Failed to validate user: "
            "Database unavailable"
        )
    }


# -------------------------------------------------
# Trip history database failure
# -------------------------------------------------

@pytest.mark.asyncio
async def test_trip_history_database_failure(
    client,
    monkeypatch,
):

    async def fake_get_user(
        user_id,
    ):
        return {
            "id": user_id
        }

    async def fake_get_trip_history(
        user_id,
    ):
        raise RuntimeError(
            "History database failure"
        )

    monkeypatch.setattr(
        trips_routes,
        "get_user",
        fake_get_user,
    )

    monkeypatch.setattr(
        trips_routes,
        "get_trip_history",
        fake_get_trip_history,
    )

    response = await client.get(
        "/trips/history/1"
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": (
            "Failed to retrieve "
            "trip history: "
            "History database failure"
        )
    }


# -------------------------------------------------
# Saved-trip database failure
# -------------------------------------------------

@pytest.mark.asyncio
async def test_saved_trip_database_failure(
    client,
    monkeypatch,
):

    async def fake_get_saved_trip(
        trip_id,
    ):
        raise RuntimeError(
            "Saved-trip database failure"
        )

    monkeypatch.setattr(
        trips_routes,
        "get_saved_trip",
        fake_get_saved_trip,
    )

    response = await client.get(
        "/trips/10"
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": (
            "Failed to retrieve saved trip: "
            "Saved-trip database failure"
        )
    }


# -------------------------------------------------
# Invalid history user ID
# -------------------------------------------------

@pytest.mark.asyncio
async def test_trip_history_invalid_user_id(
    client,
):

    response = await client.get(
        "/trips/history/0"
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": (
            "user_id must be greater than 0."
        )
    }


# -------------------------------------------------
# Invalid saved trip ID
# -------------------------------------------------

@pytest.mark.asyncio
async def test_saved_trip_invalid_id(
    client,
):

    response = await client.get(
        "/trips/0"
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": (
            "trip_id must be greater than 0."
        )
    }