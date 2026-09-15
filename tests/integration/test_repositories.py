from datetime import (
    date,
    datetime,
    timedelta,
)
from decimal import Decimal

import pytest
import pytest_asyncio

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from tripmate.database.base import Base
from tripmate.database.repositories import (
    create_trip,
    create_user,
    get_recent_user_trips,
    get_trip_by_id,
    get_user_by_email,
    get_user_by_id,
    get_user_trips,
)


# -------------------------------------------------
# Temporary test database
# -------------------------------------------------

@pytest_asyncio.fixture
async def session(
    tmp_path,
):

    database_file = (
        tmp_path / "tripmate_test.db"
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

    async with SessionLocal() as test_session:

        yield test_session

    await engine.dispose()


# -------------------------------------------------
# User tests
# -------------------------------------------------

@pytest.mark.asyncio
async def test_create_user(
    session,
):

    user = await create_user(
        session=session,
        name="Test User",
        email="test@example.com",
    )

    assert user.id is not None

    assert user.name == "Test User"

    assert user.email == (
        "test@example.com"
    )


@pytest.mark.asyncio
async def test_get_user_by_id(
    session,
):

    created_user = await create_user(
        session=session,
        name="Sohail",
        email="sohail@example.com",
    )

    user = await get_user_by_id(
        session=session,
        user_id=created_user.id,
    )

    assert user is not None

    assert user.id == created_user.id

    assert user.email == (
        "sohail@example.com"
    )


@pytest.mark.asyncio
async def test_get_user_by_email(
    session,
):

    created_user = await create_user(
        session=session,
        name="Msa",
        email="msa@example.com",
    )

    user = await get_user_by_email(
        session=session,
        email="msa@example.com",
    )

    assert user is not None

    assert user.id == created_user.id

    assert user.name == "Msa"


@pytest.mark.asyncio
async def test_user_not_found(
    session,
):

    user = await get_user_by_id(
        session=session,
        user_id=999999,
    )

    assert user is None


@pytest.mark.asyncio
async def test_duplicate_email_rejected(
    session,
):

    await create_user(
        session=session,
        name="First User",
        email="duplicate@example.com",
    )

    with pytest.raises(
        IntegrityError
    ):

        await create_user(
            session=session,
            name="Second User",
            email="duplicate@example.com",
        )

    # Important after a failed transaction
    await session.rollback()


# -------------------------------------------------
# Trip tests
# -------------------------------------------------

@pytest.mark.asyncio
async def test_create_trip(
    session,
):

    user = await create_user(
        session=session,
        name="Trip User",
        email="trip@example.com",
    )

    trip = await create_trip(
        session=session,
        user_id=user.id,
        user_query=(
            "Plan a trip to Dubai."
        ),
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
        itinerary=(
            "Dubai itinerary."
        ),
        final_response=(
            "Final Dubai response."
        ),
    )

    assert trip.id is not None

    assert trip.user_id == user.id

    assert trip.origin == "Mumbai"

    assert trip.destination == "Dubai"

    assert trip.budget == Decimal(
        "50000.00"
    )

    assert trip.adults == 2

    assert trip.children == 0


@pytest.mark.asyncio
async def test_get_trip_by_id(
    session,
):

    user = await create_user(
        session=session,
        name="Trip Lookup User",
        email="lookup@example.com",
    )

    created_trip = await create_trip(
        session=session,
        user_id=user.id,
        user_query=(
            "Plan a Singapore trip."
        ),
        destination="Singapore",
    )

    trip = await get_trip_by_id(
        session=session,
        trip_id=created_trip.id,
    )

    assert trip is not None

    assert trip.id == created_trip.id

    assert trip.destination == (
        "Singapore"
    )


@pytest.mark.asyncio
async def test_trip_not_found(
    session,
):

    trip = await get_trip_by_id(
        session=session,
        trip_id=999999,
    )

    assert trip is None


# -------------------------------------------------
# User trip history
# -------------------------------------------------

@pytest.mark.asyncio
async def test_get_user_trips(
    session,
):

    user = await create_user(
        session=session,
        name="History User",
        email="history@example.com",
    )

    first_trip = await create_trip(
        session=session,
        user_id=user.id,
        user_query="Trip one",
        destination="Goa",
    )

    second_trip = await create_trip(
        session=session,
        user_id=user.id,
        user_query="Trip two",
        destination="Dubai",
    )

    # Give the trips deterministic timestamps
    # so the ordering test is reliable.
    first_trip.created_at = datetime(
        2026,
        1,
        1,
        10,
        0,
    )

    second_trip.created_at = datetime(
        2026,
        1,
        2,
        10,
        0,
    )

    await session.commit()

    trips = await get_user_trips(
        session=session,
        user_id=user.id,
    )

    assert len(trips) == 2

    assert trips[0].destination == (
        "Dubai"
    )

    assert trips[1].destination == (
        "Goa"
    )


# -------------------------------------------------
# Recent trip history
# -------------------------------------------------

@pytest.mark.asyncio
async def test_get_recent_user_trips_limit(
    session,
):

    user = await create_user(
        session=session,
        name="Memory User",
        email="memory@example.com",
    )

    destinations = [
        "Goa",
        "Dubai",
        "Singapore",
        "Jeddah",
    ]

    base_time = datetime(
        2026,
        1,
        1,
        10,
        0,
    )

    created_trips = []

    for index, destination in enumerate(
        destinations
    ):

        trip = await create_trip(
            session=session,
            user_id=user.id,
            user_query=(
                f"Plan trip to "
                f"{destination}"
            ),
            destination=destination,
        )

        trip.created_at = (
            base_time
            + timedelta(
                days=index
            )
        )

        created_trips.append(
            trip
        )

    await session.commit()

    trips = await get_recent_user_trips(
        session=session,
        user_id=user.id,
        limit=3,
    )

    assert len(trips) == 3

    assert [
        trip.destination
        for trip in trips
    ] == [
        "Jeddah",
        "Singapore",
        "Dubai",
    ]