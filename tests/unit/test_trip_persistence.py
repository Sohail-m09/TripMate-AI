from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

import tripmate.database.trip_persistence as trip_persistence


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


def test_parse_date():

    result = trip_persistence.parse_date(
        "2026-11-10"
    )

    assert result == date(
        2026,
        11,
        10,
    )


def test_parse_date_none():

    result = trip_persistence.parse_date(
        None
    )

    assert result is None


def test_parse_budget():

    result = trip_persistence.parse_budget(
        50000.50
    )

    assert result == Decimal(
        "50000.5"
    )


def test_parse_budget_none():

    result = trip_persistence.parse_budget(
        None
    )

    assert result is None


@pytest.mark.asyncio
async def test_save_trip_requires_user_id():

    state = {
        "user_query": "Plan Dubai trip",
    }

    with pytest.raises(
        ValueError,
        match="user_id is required",
    ):

        await trip_persistence.save_trip_from_state(
            state
        )


@pytest.mark.asyncio
async def test_save_trip_from_state(
    monkeypatch,
):

    captured = {}

    async def fake_create_trip(
        **kwargs,
    ):
        captured.update(
            kwargs
        )

        return SimpleNamespace(
            id=42
        )

    monkeypatch.setattr(
        trip_persistence,
        "AsyncSessionLocal",
        fake_session_local,
    )

    monkeypatch.setattr(
        trip_persistence,
        "create_trip",
        fake_create_trip,
    )

    state = {
        "user_id": 1,
        "user_query": "Plan a trip to Dubai.",
        "origin": "Mumbai",
        "destination": "Dubai",
        "start_date": "2026-11-10",
        "end_date": "2026-11-15",
        "budget": 50000.0,
        "adults": 2,
        "children": 0,
        "itinerary": "Dubai itinerary.",
        "final_response": "Final Dubai response.",
    }

    trip_id = (
        await trip_persistence.save_trip_from_state(
            state
        )
    )

    assert trip_id == 42

    assert captured["session"] == (
        "fake-session"
    )

    assert captured["user_id"] == 1

    assert captured["origin"] == (
        "Mumbai"
    )

    assert captured["destination"] == (
        "Dubai"
    )

    assert captured["start_date"] == date(
        2026,
        11,
        10,
    )

    assert captured["end_date"] == date(
        2026,
        11,
        15,
    )

    assert captured["budget"] == Decimal(
        "50000.0"
    )

    assert captured["adults"] == 2
    assert captured["children"] == 0

    assert captured["itinerary"] == (
        "Dubai itinerary."
    )