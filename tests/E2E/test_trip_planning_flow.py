from decimal import Decimal

import pytest
import pytest_asyncio

from httpx import (
    ASGITransport,
    AsyncClient,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from tripmate.api.main import app
from tripmate.database.base import Base
from tripmate.database.repositories import (
    create_user,
)
from tripmate.schemas import (
    RoutingDecision,
    TravelAgentResponse,
    TripRequest,
)

import tripmate.agents.itinerary_agent as itinerary_agent
import tripmate.database.trip_history as trip_history
import tripmate.database.trip_memory as trip_memory
import tripmate.database.trip_persistence as trip_persistence
import tripmate.database.user_service as user_service
import tripmate.graph.nodes as graph_nodes


# -------------------------------------------------
# Temporary database
# -------------------------------------------------

@pytest_asyncio.fixture
async def test_session_factory(
    tmp_path,
    monkeypatch,
):

    database_file = (
        tmp_path / "tripmate_e2e.db"
    )

    database_url = (
        f"sqlite+aiosqlite:///"
        f"{database_file.as_posix()}"
    )

    engine = create_async_engine(
        database_url,
        echo=False,
    )

    async with engine.begin() as connection:

        await connection.run_sync(
            Base.metadata.create_all
        )

    SessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # -----------------------------------
    # Point all DB services to test DB
    # -----------------------------------

    monkeypatch.setattr(
        user_service,
        "AsyncSessionLocal",
        SessionLocal,
    )

    monkeypatch.setattr(
        trip_persistence,
        "AsyncSessionLocal",
        SessionLocal,
    )

    monkeypatch.setattr(
        trip_history,
        "AsyncSessionLocal",
        SessionLocal,
    )

    monkeypatch.setattr(
        trip_memory,
        "AsyncSessionLocal",
        SessionLocal,
    )

    yield SessionLocal

    await engine.dispose()


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
# Complete TripMate flow
# -------------------------------------------------

@pytest.mark.asyncio
async def test_complete_trip_planning_flow(
    client,
    test_session_factory,
    monkeypatch,
):

    # -----------------------------------
    # Create a real user in test DB
    # -----------------------------------

    async with test_session_factory() as session:

        user = await create_user(
            session=session,
            name="E2E User",
            email="e2e@example.com",
        )

        user_id = user.id

    # -----------------------------------
    # Mock Trip Request LLM extraction
    # -----------------------------------

    async def fake_extract_trip_request(
        user_query,
    ):

        assert "Dubai" in user_query

        return TripRequest(
            origin="Mumbai",
            destination="Dubai",

            origin_airport="BOM",
            destination_airport="DXB",

            destination_country="UAE",

            start_date="2026-11-10",
            end_date="2026-11-15",

            budget=50000.0,

            adults=2,
            children=0,
        )

    monkeypatch.setattr(
        graph_nodes,
        "extract_trip_request",
        fake_extract_trip_request,
    )

    # -----------------------------------
    # Mock orchestrator LLM
    # -----------------------------------

    async def fake_run_orchestrator(
        user_query,
    ):

        return RoutingDecision(
            required_agents=[
                "flight",
                "hotel",
                "weather",
                "places",
                "itinerary",
            ],
            reason=(
                "Complete travel planning "
                "request."
            ),
        )

    monkeypatch.setattr(
        graph_nodes,
        "run_orchestrator",
        fake_run_orchestrator,
    )

    # -----------------------------------
    # Mock external specialist boundaries
    # -----------------------------------

    async def fake_run_flight_agent(
        user_query,
    ):

        # Real agent-input builder should
        # convert state into airport input.
        assert "Origin: BOM" in user_query
        assert "Destination: DXB" in user_query

        return TravelAgentResponse(
            answer=(
                "Flight BOM to DXB "
                "available for ₹15,000."
            ),
            tools_used=[
                "find_flights"
            ],
            is_complete=True,
        )

    async def fake_run_hotel_agent(
        user_query,
    ):

        # Hotels must use geographic
        # destination, NOT DXB.
        assert (
            "Location: Dubai, UAE"
            in user_query
        )

        assert "DXB" not in user_query

        return TravelAgentResponse(
            answer=(
                "Dubai hotel available "
                "for ₹7,000 per night."
            ),
            tools_used=[
                "find_hotels"
            ],
            is_complete=True,
        )

    async def fake_run_weather_agent(
        user_query,
    ):

        assert (
            "Location: Dubai, UAE"
            in user_query
        )

        return TravelAgentResponse(
            answer=(
                "Dubai weather is sunny."
            ),
            tools_used=[
                "current_weather"
            ],
            is_complete=True,
        )

    async def fake_run_places_agent(
        user_query,
    ):

        assert (
            "Location: Dubai, UAE"
            in user_query
        )

        return TravelAgentResponse(
            answer=(
                "Visit Burj Khalifa "
                "and Dubai Mall."
            ),
            tools_used=[
                "find_places"
            ],
            is_complete=True,
        )

    monkeypatch.setattr(
        graph_nodes,
        "run_flight_agent",
        fake_run_flight_agent,
    )

    monkeypatch.setattr(
        graph_nodes,
        "run_hotel_agent",
        fake_run_hotel_agent,
    )

    monkeypatch.setattr(
        graph_nodes,
        "run_weather_agent",
        fake_run_weather_agent,
    )

    monkeypatch.setattr(
        graph_nodes,
        "run_places_agent",
        fake_run_places_agent,
    )

    # -----------------------------------
    # Mock only itinerary LLM generation
    # -----------------------------------

    async def fake_run_itinerary_agent(
        user_query,
        flight_info=None,
        hotel_info=None,
        weather_info=None,
        places_info=None,
        memory_context=None,
    ):

        assert (
            "Flight BOM to DXB"
            in flight_info
        )

        assert (
            "Dubai hotel"
            in hotel_info
        )

        assert (
            "Dubai weather"
            in weather_info
        )

        assert (
            "Burj Khalifa"
            in places_info
        )

        return TravelAgentResponse(
            answer=(
                "Day 1: Arrive in Dubai.\n"
                "Day 2: Visit Burj Khalifa.\n"
                "Day 3: Explore Dubai Mall."
            ),
            tools_used=[],
            is_complete=True,
        )

    monkeypatch.setattr(
        graph_nodes,
        "run_itinerary_agent",
        fake_run_itinerary_agent,
    )

    # -----------------------------------
    # Send real HTTP request
    # -----------------------------------

    response = await client.post(
        "/trips/plan",
        json={
            "user_id": user_id,
            "user_query": (
                "Plan a trip to Dubai, UAE. "
                "Find flights, hotels, weather, "
                "tourist attractions and create "
                "a complete itinerary."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    # -----------------------------------
    # API response
    # -----------------------------------

    assert data["required_agents"] == [
        "flight",
        "hotel",
        "weather",
        "places",
        "itinerary",
    ]

    assert set(
        data["completed_agents"]
    ) == {
        "flight",
        "hotel",
        "weather",
        "places",
    }

    assert data["failed_agents"] == []

    assert data["trip_saved"] is True

    assert data["saved_trip_id"] is not None

    assert (
        "Day 1: Arrive in Dubai."
        in data["itinerary"]
    )

    assert (
        data["flight_result"]["is_complete"]
        is True
    )

    assert (
        data["hotel_result"]["is_complete"]
        is True
    )

    # -----------------------------------
    # Verify actual DB persistence
    # through real history API
    # -----------------------------------

    saved_trip_id = data[
        "saved_trip_id"
    ]

    history_response = await client.get(
        f"/trips/history/{user_id}"
    )

    assert (
        history_response.status_code
        == 200
    )

    history = (
        history_response.json()
    )

    assert history["total_trips"] == 1

    saved_history_trip = (
        history["trips"][0]
    )

    assert (
        saved_history_trip["destination"]
        == "Dubai"
    )

    assert (
        saved_history_trip["origin"]
        == "Mumbai"
    )

    assert (
        saved_history_trip["budget"]
        == 50000.0
    )

    assert (
        "Day 1: Arrive in Dubai."
        in saved_history_trip["itinerary"]
    )

    # -----------------------------------
    # Verify single-trip endpoint too
    # -----------------------------------

    trip_response = await client.get(
        f"/trips/{saved_trip_id}"
    )

    assert (
        trip_response.status_code
        == 200
    )

    saved_trip = trip_response.json()

    assert saved_trip["id"] == (
        saved_trip_id
    )

    assert saved_trip["user_id"] == (
        user_id
    )

    assert saved_trip["destination"] == (
        "Dubai"
    )

    assert saved_trip["start_date"] == (
        "2026-11-10"
    )

    assert saved_trip["end_date"] == (
        "2026-11-15"
    )

    assert saved_trip["budget"] == (
        50000.0
    )

@pytest.mark.asyncio
async def test_previous_trip_memory_used_for_next_trip(
    client,
    test_session_factory,
    monkeypatch,
):

    # -----------------------------------
    # Create one real user
    # -----------------------------------

    async with test_session_factory() as session:

        user = await create_user(
            session=session,
            name="Memory E2E User",
            email="memory-e2e@example.com",
        )

        user_id = user.id

    # -----------------------------------
    # Mock structured request extraction
    # depending on the current query
    # -----------------------------------

    async def fake_extract_trip_request(
        user_query,
    ):

        if "Singapore" in user_query:

            return TripRequest(
                origin="Mumbai",
                destination="Singapore",
                origin_airport=None,
                destination_airport=None,
                destination_country="Singapore",
                start_date="2026-12-10",
                end_date="2026-12-14",
                budget=60000.0,
                adults=2,
                children=0,
            )

        if "Dubai" in user_query:

            return TripRequest(
                origin="Mumbai",
                destination="Dubai",
                origin_airport=None,
                destination_airport=None,
                destination_country="UAE",
                start_date="2027-01-10",
                end_date="2027-01-14",
                budget=80000.0,
                adults=2,
                children=0,
            )

        raise AssertionError(
            "Unexpected trip request."
        )

    monkeypatch.setattr(
        graph_nodes,
        "extract_trip_request",
        fake_extract_trip_request,
    )

    # -----------------------------------
    # Same routing pattern for both trips
    # -----------------------------------

    async def fake_run_orchestrator(
        user_query,
    ):

        return RoutingDecision(
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

    monkeypatch.setattr(
        graph_nodes,
        "run_orchestrator",
        fake_run_orchestrator,
    )

    # -----------------------------------
    # Mock specialist external boundaries
    # -----------------------------------

    async def fake_run_hotel_agent(
        user_query,
    ):

        if "Singapore" in user_query:

            assert (
                "Location: Singapore, Singapore"
                in user_query
            )

            answer = (
                "Singapore hotel information."
            )

        elif "Dubai" in user_query:

            assert (
                "Location: Dubai, UAE"
                in user_query
            )

            answer = (
                "Dubai hotel information."
            )

        else:

            raise AssertionError(
                "Unexpected hotel request."
            )

        return TravelAgentResponse(
            answer=answer,
            tools_used=[
                "find_hotels"
            ],
            is_complete=True,
        )

    async def fake_run_places_agent(
        user_query,
    ):

        if "Singapore" in user_query:

            answer = (
                "Singapore attraction information."
            )

        elif "Dubai" in user_query:

            answer = (
                "Dubai attraction information."
            )

        else:

            raise AssertionError(
                "Unexpected places request."
            )

        return TravelAgentResponse(
            answer=answer,
            tools_used=[
                "find_places"
            ],
            is_complete=True,
        )

    monkeypatch.setattr(
        graph_nodes,
        "run_hotel_agent",
        fake_run_hotel_agent,
    )

    monkeypatch.setattr(
        graph_nodes,
        "run_places_agent",
        fake_run_places_agent,
    )

    # -----------------------------------
    # Capture memory passed to itinerary
    # -----------------------------------

    itinerary_calls = []

    async def fake_run_itinerary_agent(
        user_query,
        flight_info=None,
        hotel_info=None,
        weather_info=None,
        places_info=None,
        memory_context=None,
    ):

        itinerary_calls.append(
            {
                "user_query": user_query,
                "hotel_info": hotel_info,
                "places_info": places_info,
                "memory_context": memory_context,
            }
        )

        # First trip should have no
        # previous trip history.
        if "Singapore" in user_query:

            assert memory_context is None

            return TravelAgentResponse(
                answer=(
                    "Singapore itinerary."
                ),
                tools_used=[],
                is_complete=True,
            )

        # Second trip should receive
        # Singapore as persistent memory.
        if "Dubai" in user_query:

            assert memory_context is not None

            assert (
                "Route: Mumbai -> Singapore"
                in memory_context
            )

            assert (
                "Dates: 2026-12-10 "
                "to 2026-12-14"
                in memory_context
            )

            assert (
                "Budget: 60000.00"
                in memory_context
            )

            # Current trip data still wins.
            assert (
                hotel_info
                == "Dubai hotel information."
            )

            assert (
                places_info
                == "Dubai attraction information."
            )

            return TravelAgentResponse(
                answer=(
                    "Dubai itinerary using "
                    "current trip information."
                ),
                tools_used=[],
                is_complete=True,
            )

        raise AssertionError(
            "Unexpected itinerary request."
        )

    monkeypatch.setattr(
        graph_nodes,
        "run_itinerary_agent",
        fake_run_itinerary_agent,
    )

    # -----------------------------------
    # FIRST TRIP — Singapore
    # -----------------------------------

    first_response = await client.post(
        "/trips/plan",
        json={
            "user_id": user_id,
            "user_query": (
                "Plan a trip to Singapore. "
                "Find hotels, attractions "
                "and create an itinerary."
            ),
        },
    )

    assert (
        first_response.status_code
        == 200
    )

    first_data = (
        first_response.json()
    )

    assert first_data[
        "trip_saved"
    ] is True

    assert first_data[
        "saved_trip_id"
    ] is not None

    assert (
        first_data["itinerary"]
        == "Singapore itinerary."
    )

    # -----------------------------------
    # SECOND TRIP — Dubai
    # -----------------------------------

    second_response = await client.post(
        "/trips/plan",
        json={
            "user_id": user_id,
            "user_query": (
                "Plan another trip to Dubai. "
                "Find hotels, attractions "
                "and create an itinerary."
            ),
        },
    )

    assert (
        second_response.status_code
        == 200
    )

    second_data = (
        second_response.json()
    )

    assert second_data[
        "trip_saved"
    ] is True

    assert second_data[
        "saved_trip_id"
    ] is not None

    assert (
        second_data["saved_trip_id"]
        != first_data["saved_trip_id"]
    )

    assert (
        second_data["itinerary"]
        == (
            "Dubai itinerary using "
            "current trip information."
        )
    )

    # Memory node should have loaded
    # the previous Singapore trip.
    assert second_data[
        "memory_loaded"
    ] is True

    # -----------------------------------
    # Verify itinerary was called twice
    # -----------------------------------

    assert len(
        itinerary_calls
    ) == 2

    assert (
        itinerary_calls[0][
            "memory_context"
        ]
        is None
    )

    assert (
        "Route: Mumbai -> Singapore"
        in itinerary_calls[1][
            "memory_context"
        ]
    )

    # -----------------------------------
    # Both trips must exist in DB
    # -----------------------------------

    history_response = await client.get(
        f"/trips/history/{user_id}"
    )

    assert (
        history_response.status_code
        == 200
    )

    history = (
        history_response.json()
    )

    assert history[
        "total_trips"
    ] == 2

    destinations = {
        trip["destination"]
        for trip in history["trips"]
    }

    assert destinations == {
        "Singapore",
        "Dubai",
    }