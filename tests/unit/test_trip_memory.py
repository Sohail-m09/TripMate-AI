from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

import tripmate.database.trip_memory as trip_memory


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
async def test_build_trip_memory_context(
    monkeypatch,
):

    trips = [
        SimpleNamespace(
            id=3,
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
        ),
        SimpleNamespace(
            id=2,
            origin="Mumbai",
            destination="Goa",
            start_date=date(
                2026,
                10,
                10,
            ),
            end_date=date(
                2026,
                10,
                15,
            ),
            budget=None,
            adults=2,
            children=None,
        ),
    ]

    captured = {}

    async def fake_get_recent_user_trips(
        session,
        user_id,
        limit,
    ):

        captured["session"] = session
        captured["user_id"] = user_id
        captured["limit"] = limit

        return trips

    monkeypatch.setattr(
        trip_memory,
        "AsyncSessionLocal",
        fake_session_local,
    )

    monkeypatch.setattr(
        trip_memory,
        "get_recent_user_trips",
        fake_get_recent_user_trips,
    )

    result = (
        await trip_memory.build_trip_memory_context(
            user_id=1,
            limit=3,
        )
    )

    assert result is not None

    assert "Trip ID: 3" in result

    assert (
        "Route: Mumbai -> Dubai"
        in result
    )

    assert (
        "Dates: 2026-11-10 to 2026-11-15"
        in result
    )

    assert (
        "Budget: 50000.00"
        in result
    )

    assert "Adults: 2" in result

    assert "Children: 0" in result

    assert "Trip ID: 2" in result

    assert (
        "Route: Mumbai -> Goa"
        in result
    )

    assert captured["user_id"] == 1

    assert captured["limit"] == 3


@pytest.mark.asyncio
async def test_build_trip_memory_without_history(
    monkeypatch,
):

    async def fake_get_recent_user_trips(
        session,
        user_id,
        limit,
    ):
        return []

    monkeypatch.setattr(
        trip_memory,
        "AsyncSessionLocal",
        fake_session_local,
    )

    monkeypatch.setattr(
        trip_memory,
        "get_recent_user_trips",
        fake_get_recent_user_trips,
    )

    result = (
        await trip_memory.build_trip_memory_context(
            user_id=1
        )
    )

    assert result is None


@pytest.mark.asyncio
async def test_trip_memory_missing_optional_values(
    monkeypatch,
):

    trips = [
        SimpleNamespace(
            id=1,
            origin=None,
            destination=None,
            start_date=None,
            end_date=None,
            budget=None,
            adults=None,
            children=None,
        )
    ]

    async def fake_get_recent_user_trips(
        session,
        user_id,
        limit,
    ):
        return trips

    monkeypatch.setattr(
        trip_memory,
        "AsyncSessionLocal",
        fake_session_local,
    )

    monkeypatch.setattr(
        trip_memory,
        "get_recent_user_trips",
        fake_get_recent_user_trips,
    )

    result = (
        await trip_memory.build_trip_memory_context(
            user_id=1
        )
    )

    assert result is not None

    assert (
        "Route: Unknown -> Unknown"
        in result
    )

    assert "Dates:" not in result

    assert "Budget:" not in result

    assert "Adults:" not in result

    assert "Children:" not in result