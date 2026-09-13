import asyncio

from datetime import date
from decimal import Decimal

from tripmate.database.connection import (
    AsyncSessionLocal,
    engine,
)
from tripmate.database.repositories import (
    create_trip,
    create_user,
    get_user_by_email,
    get_user_trips,
)


async def main() -> None:

    async with AsyncSessionLocal() as session:

        email = "test@tripmate.ai"

        user = await get_user_by_email(
            session,
            email,
        )

        if user is None:

            user = await create_user(
                session=session,
                name="TripMate Test User",
                email=email,
            )

            print(
                "User created:",
                user.id,
                user.email,
            )

        else:

            print(
                "Existing user:",
                user.id,
                user.email,
            )

        trip = await create_trip(
            session=session,
            user_id=user.id,
            user_query=(
                "Plan a Goa trip from Mumbai "
                "for 2 adults."
            ),
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
            budget=Decimal(
                "50000.00"
            ),
            adults=2,
            children=0,
            itinerary=(
                "Sample itinerary for "
                "database testing."
            ),
            final_response=(
                "Sample final TripMate response."
            ),
        )

        print(
            "Trip created:",
            trip.id,
            trip.destination,
        )

        trips = await get_user_trips(
            session,
            user.id,
        )

        print(
            "Total trips:",
            len(trips),
        )

        for saved_trip in trips:

            print(
                saved_trip.id,
                saved_trip.origin,
                "->",
                saved_trip.destination,
            )

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(
        main()
    )