from tripmate.database.connection import (
    AsyncSessionLocal,
)
from tripmate.database.repositories import (
    get_recent_user_trips,
)


async def build_trip_memory_context(
    user_id: int,
    limit: int = 3,
) -> str | None:

    async with AsyncSessionLocal() as session:

        trips = await get_recent_user_trips(
            session=session,
            user_id=user_id,
            limit=limit,
        )

        if not trips:
            return None

        sections = []

        for trip in trips:

            trip_details = [
                f"Trip ID: {trip.id}",
                (
                    f"Route: "
                    f"{trip.origin or 'Unknown'} "
                    f"-> "
                    f"{trip.destination or 'Unknown'}"
                ),
            ]

            if (
                trip.start_date
                and trip.end_date
            ):
                trip_details.append(
                    (
                        f"Dates: "
                        f"{trip.start_date.isoformat()} "
                        f"to "
                        f"{trip.end_date.isoformat()}"
                    )
                )

            if trip.budget is not None:
                trip_details.append(
                    f"Budget: {trip.budget}"
                )

            if trip.adults is not None:
                trip_details.append(
                    f"Adults: {trip.adults}"
                )

            if trip.children is not None:
                trip_details.append(
                    f"Children: {trip.children}"
                )

            sections.append(
                "\n".join(
                    trip_details
                )
            )

        return "\n\n".join(
            sections
        )