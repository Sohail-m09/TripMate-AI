import pytest
import pytest_asyncio

from httpx import (
    ASGITransport,
    AsyncClient,
)

from tripmate.api.main import app
from tripmate.schemas import (
    RoutingDecision,
    TravelAgentResponse,
)

import tripmate.api.routes.trips as trips_routes
import tripmate.api.routes.users as users_routes


# -------------------------------------------------
# FastAPI test client
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
# Fake LangGraph
# -------------------------------------------------

class FakeTravelGraph:

    def __init__(
        self,
        result=None,
        error=None,
    ):
        self.result = result
        self.error = error
        self.received_state = None

    async def ainvoke(
        self,
        state,
    ):
        self.received_state = state

        if self.error is not None:
            raise self.error

        return self.result


# -------------------------------------------------
# Root / health
# -------------------------------------------------

@pytest.mark.asyncio
async def test_root_endpoint(
    client,
):

    response = await client.get(
        "/"
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": (
            "TripMate AI API is running."
        )
    }


@pytest.mark.asyncio
async def test_health_endpoint(
    client,
):

    response = await client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "service": "tripmate-api",
    }


# -------------------------------------------------
# User endpoints
# -------------------------------------------------

@pytest.mark.asyncio
async def test_create_user_success(
    client,
    monkeypatch,
):

    async def fake_register_user(
        name,
        email,
    ):
        return {
            "id": 10,
            "name": name,
            "email": email,
            "created_at": None,
        }

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

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 10
    assert data["name"] == "Sohail"

    assert data["email"] == (
        "sohail@example.com"
    )


@pytest.mark.asyncio
async def test_create_user_duplicate_email(
    client,
    monkeypatch,
):

    async def fake_register_user(
        name,
        email,
    ):
        raise ValueError(
            "A user with this email already exists."
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
            "email": "duplicate@example.com",
        },
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail": (
            "A user with this email already exists."
        )
    }


@pytest.mark.asyncio
async def test_get_user_by_email_success(
    client,
    monkeypatch,
):

    async def fake_get_user_by_email(
        email,
    ):
        return {
            "id": 5,
            "name": "Msa",
            "email": email,
            "created_at": None,
        }

    monkeypatch.setattr(
        users_routes,
        "get_user_by_email_address",
        fake_get_user_by_email,
    )

    response = await client.get(
        "/users/by-email",
        params={
            "email": "msa@example.com"
        },
    )

    assert response.status_code == 200

    assert response.json()["id"] == 5


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(
    client,
    monkeypatch,
):

    async def fake_get_user_by_email(
        email,
    ):
        return None

    monkeypatch.setattr(
        users_routes,
        "get_user_by_email_address",
        fake_get_user_by_email,
    )

    response = await client.get(
        "/users/by-email",
        params={
            "email": "missing@example.com"
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "User not found."
    }


@pytest.mark.asyncio
async def test_get_user_invalid_id(
    client,
):

    response = await client.get(
        "/users/0"
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": (
            "user_id must be greater than 0."
        )
    }


# -------------------------------------------------
# Trip planning
# -------------------------------------------------

@pytest.mark.asyncio
async def test_plan_trip_success(
    client,
    monkeypatch,
):

    async def fake_get_user(
        user_id,
    ):
        return {
            "id": user_id,
            "name": "Sohail",
            "email": "sohail@example.com",
        }

    flight_result = TravelAgentResponse(
        answer="Flight BOM to DXB found.",
        tools_used=[
            "find_flights"
        ],
        is_complete=True,
    )

    hotel_result = TravelAgentResponse(
        answer="Dubai hotel found.",
        tools_used=[
            "find_hotels"
        ],
        is_complete=True,
    )

    fake_graph = FakeTravelGraph(
        result={
            "routing_decision":
                RoutingDecision(
                    required_agents=[
                        "flight",
                        "hotel",
                        "itinerary",
                    ],
                    reason="Test routing.",
                ),

            "flight_result":
                flight_result,

            "hotel_result":
                hotel_result,

            "final_response":
                "Final Dubai itinerary.",

            "itinerary":
                "Final Dubai itinerary.",

            "completed_agents": [
                "flight",
                "hotel",
            ],

            "failed_agents": [],

            "memory_loaded": True,

            "trip_saved": True,

            "saved_trip_id": 50,
        }
    )

    monkeypatch.setattr(
        trips_routes,
        "get_user",
        fake_get_user,
    )

    monkeypatch.setattr(
        trips_routes,
        "travel_graph",
        fake_graph,
    )

    response = await client.post(
        "/trips/plan",
        json={
            "user_id": 1,
            "user_query": (
                "Plan a Dubai trip."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["final_response"] == (
        "Final Dubai itinerary."
    )

    assert data["itinerary"] == (
        "Final Dubai itinerary."
    )

    assert data["required_agents"] == [
        "flight",
        "hotel",
        "itinerary",
    ]

    assert data["completed_agents"] == [
        "flight",
        "hotel",
    ]

    assert data["failed_agents"] == []

    assert data["memory_loaded"] is True

    assert data["trip_saved"] is True

    assert data["saved_trip_id"] == 50

    assert (
        data["flight_result"]["tools_used"]
        == ["find_flights"]
    )

    assert (
        data["hotel_result"]["is_complete"]
        is True
    )

    assert fake_graph.received_state == {
        "user_id": 1,
        "user_query": (
            "Plan a Dubai trip."
        ),
        "completed_agents": [],
        "failed_agents": [],
    }


@pytest.mark.asyncio
async def test_plan_trip_user_not_found(
    client,
    monkeypatch,
):

    async def fake_get_user(
        user_id,
    ):
        return None

    monkeypatch.setattr(
        trips_routes,
        "get_user",
        fake_get_user,
    )

    response = await client.post(
        "/trips/plan",
        json={
            "user_id": 999,
            "user_query": (
                "Plan a trip to Dubai."
            ),
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "User not found."
    }


@pytest.mark.asyncio
async def test_plan_trip_workflow_failure(
    client,
    monkeypatch,
):

    async def fake_get_user(
        user_id,
    ):
        return {
            "id": user_id
        }

    fake_graph = FakeTravelGraph(
        error=RuntimeError(
            "Graph failure"
        )
    )

    monkeypatch.setattr(
        trips_routes,
        "get_user",
        fake_get_user,
    )

    monkeypatch.setattr(
        trips_routes,
        "travel_graph",
        fake_graph,
    )

    response = await client.post(
        "/trips/plan",
        json={
            "user_id": 1,
            "user_query": (
                "Plan a Dubai trip."
            ),
        },
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": (
            "Trip planning workflow failed: "
            "Graph failure"
        )
    }


@pytest.mark.asyncio
async def test_plan_trip_invalid_request_body(
    client,
):

    response = await client.post(
        "/trips/plan",
        json={
            "user_id": 0,
            "user_query": "Hi",
        },
    )

    assert response.status_code == 422


# -------------------------------------------------
# Trip history
# -------------------------------------------------

@pytest.mark.asyncio
async def test_trip_history_success(
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
        return [
            {
                "id": 1,
                "origin": "Mumbai",
                "destination": "Dubai",
                "start_date": "2026-11-10",
                "end_date": "2026-11-15",
                "budget": 50000.0,
                "adults": 2,
                "children": 0,
                "user_query": (
                    "Plan Dubai trip."
                ),
                "itinerary": (
                    "Dubai itinerary."
                ),
                "final_response": (
                    "Final response."
                ),
                "created_at": (
                    "2026-09-15T10:00:00"
                ),
            }
        ]

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

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == 1

    assert data["total_trips"] == 1

    assert (
        data["trips"][0]["destination"]
        == "Dubai"
    )


@pytest.mark.asyncio
async def test_trip_history_user_not_found(
    client,
    monkeypatch,
):

    async def fake_get_user(
        user_id,
    ):
        return None

    monkeypatch.setattr(
        trips_routes,
        "get_user",
        fake_get_user,
    )

    response = await client.get(
        "/trips/history/999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "User not found."
    }


# -------------------------------------------------
# Saved trip endpoint
# -------------------------------------------------

@pytest.mark.asyncio
async def test_get_saved_trip_success(
    client,
    monkeypatch,
):

    async def fake_get_saved_trip(
        trip_id,
    ):
        return {
            "id": trip_id,
            "user_id": 1,
            "origin": "Mumbai",
            "destination": "Singapore",
            "start_date": "2026-12-10",
            "end_date": "2026-12-14",
            "budget": 75000.0,
            "adults": 2,
            "children": 0,
            "user_query": (
                "Plan Singapore trip."
            ),
            "itinerary": (
                "Singapore itinerary."
            ),
            "final_response": (
                "Singapore response."
            ),
        }

    monkeypatch.setattr(
        trips_routes,
        "get_saved_trip",
        fake_get_saved_trip,
    )

    response = await client.get(
        "/trips/10"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 10

    assert data["destination"] == (
        "Singapore"
    )

    assert data["budget"] == 75000.0


@pytest.mark.asyncio
async def test_get_saved_trip_not_found(
    client,
    monkeypatch,
):

    async def fake_get_saved_trip(
        trip_id,
    ):
        return None

    monkeypatch.setattr(
        trips_routes,
        "get_saved_trip",
        fake_get_saved_trip,
    )

    response = await client.get(
        "/trips/999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Trip not found."
    }