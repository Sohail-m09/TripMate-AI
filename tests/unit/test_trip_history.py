from datetime import (
    date,
    datetime,
)
from decimal import Decimal
from types import SimpleNamespace

import pytest

import tripmate.database.trip_history as trip_history


class FakeSessionContext:

    async def __aenter__(self):
        return "fake-session"

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        return False


def fake_session_local():
    return FakeSessionContext()


@pytest.mark.asyncio
async def test_get_trip_history(
    monkeypatch,
):

    fake_trip = SimpleNamespace(
        id=10,
        origin="Mumbai",
        destination="Dubai",
        start_date=date(
            2026,
            11,
            10,
        ),
        end_date=date(
            2026,
            11,
            15,
        ),
        budget=Decimal(
            "50000.00"
        ),
        adults=2,
        children=0,
        user_query=(
            "Plan a Dubai trip."
        ),
        itinerary=(
            "Dubai itinerary."
        ),
        final_response=(
            "Final response."
        ),
        created_at=datetime(
            2026,
            9,
            15,
            10,
            30,
        ),
    )

    async def fake_get_user_trips(
        session,
        user_id,
    ):

        assert session == (
            "fake-session"
        )

        assert user_id == 1

        return [
            fake_trip
        ]

    monkeypatch.setattr(
        trip_history,
        "AsyncSessionLocal",
        fake_session_local,
    )

    monkeypatch.setattr(
        trip_history,
        "get_user_trips",
        fake_get_user_trips,
    )

    result = await trip_history.get_trip_history(
        user_id=1
    )

    assert len(result) == 1

    trip = result[0]

    assert trip["id"] == 10

    assert trip["origin"] == (
        "Mumbai"
    )

    assert trip["destination"] == (
        "Dubai"
    )

    assert trip["start_date"] == (
        "2026-11-10"
    )

    assert trip["end_date"] == (
        "2026-11-15"
    )

    assert trip["budget"] == 50000.0

    assert trip["adults"] == 2
    assert trip["children"] == 0

    assert trip["created_at"] == (
        "2026-09-15T10:30:00"
    )


@pytest.mark.asyncio
async def test_get_trip_history_empty(
    monkeypatch,
):

    async def fake_get_user_trips(
        session,
        user_id,
    ):
        return []

    monkeypatch.setattr(
        trip_history,
        "AsyncSessionLocal",
        fake_session_local,
    )

    monkeypatch.setattr(
        trip_history,
        "get_user_trips",
        fake_get_user_trips,
    )

    result = await trip_history.get_trip_history(
        user_id=1
    )

    assert result == []


@pytest.mark.asyncio
async def test_get_saved_trip(
    monkeypatch,
):

    fake_trip = SimpleNamespace(
        id=20,
        user_id=5,
        origin="Mumbai",
        destination="Singapore",
        start_date=date(
            2026,
            12,
            10,
        ),
        end_date=date(
            2026,
            12,
            14,
        ),
        budget=Decimal(
            "75000.00"
        ),
        adults=2,
        children=None,
        user_query=(
            "Plan Singapore trip."
        ),
        itinerary=(
            "Singapore itinerary."
        ),
        final_response=(
            "Singapore response."
        ),
    )

    async def fake_get_trip_by_id(
        session,
        trip_id,
    ):

        assert trip_id == 20

        return fake_trip

    monkeypatch.setattr(
        trip_history,
        "AsyncSessionLocal",
        fake_session_local,
    )

    monkeypatch.setattr(
        trip_history,
        "get_trip_by_id",
        fake_get_trip_by_id,
    )

    result = await trip_history.get_saved_trip(
        trip_id=20
    )

    assert result is not None

    assert result["id"] == 20

    assert result["user_id"] == 5

    assert result["destination"] == (
        "Singapore"
    )

    assert result["start_date"] == (
        "2026-12-10"
    )

    assert result["budget"] == 75000.0


@pytest.mark.asyncio
async def test_get_saved_trip_not_found(
    monkeypatch,
):

    async def fake_get_trip_by_id(
        session,
        trip_id,
    ):
        return None

    monkeypatch.setattr(
        trip_history,
        "AsyncSessionLocal",
        fake_session_local,
    )

    monkeypatch.setattr(
        trip_history,
        "get_trip_by_id",
        fake_get_trip_by_id,
    )

    result = await trip_history.get_saved_trip(
        trip_id=999
    )

    assert result is None