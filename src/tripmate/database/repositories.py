from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tripmate.database.models import (
    Trip,
    User,
)

async def get_user_by_id(
    session: AsyncSession,
    user_id: int,
) -> User | None:

    statement = select(User).where(
        User.id == user_id
    )

    result = await session.execute(
        statement
    )

    return result.scalar_one_or_none()


async def get_user_by_email(
    session: AsyncSession,
    email: str,
) -> User | None:

    statement = select(User).where(
        User.email == email
    )

    result = await session.execute(
        statement
    )

    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    name: str,
    email: str,
) -> User:

    user = User(
        name=name,
        email=email,
    )

    session.add(user)

    await session.commit()
    await session.refresh(user)

    return user


async def create_trip(
    session: AsyncSession,
    user_id: int,
    user_query: str,
    origin: str | None = None,
    destination: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    budget: Decimal | None = None,
    adults: int | None = None,
    children: int | None = None,
    itinerary: str | None = None,
    final_response: str | None = None,
) -> Trip:

    trip = Trip(
        user_id=user_id,
        user_query=user_query,
        origin=origin,
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        budget=budget,
        adults=adults,
        children=children,
        itinerary=itinerary,
        final_response=final_response,
    )

    session.add(trip)

    await session.commit()
    await session.refresh(trip)

    return trip


async def get_trip_by_id(
    session: AsyncSession,
    trip_id: int,
) -> Trip | None:

    statement = select(Trip).where(
        Trip.id == trip_id
    )

    result = await session.execute(
        statement
    )

    return result.scalar_one_or_none()


async def get_user_trips(
    session: AsyncSession,
    user_id: int,
) -> list[Trip]:

    statement = (
        select(Trip)
        .where(
            Trip.user_id == user_id
        )
        .order_by(
            Trip.created_at.desc()
        )
    )

    result = await session.execute(
        statement
    )

    return list(
        result.scalars().all()
    )

async def get_recent_user_trips(
    session: AsyncSession,
    user_id: int,
    limit: int = 3,
) -> list[Trip]:

    statement = (
        select(Trip)
        .where(
            Trip.user_id == user_id
        )
        .order_by(
            Trip.created_at.desc()
        )
        .limit(limit)
    )

    result = await session.execute(
        statement
    )

    return list(
        result.scalars().all()
    )