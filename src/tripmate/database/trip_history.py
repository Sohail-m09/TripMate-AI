from tripmate.database.connection import (
    AsyncSessionLocal,
)
from tripmate.database.repositories import (
    get_user_trips,
    get_trip_by_id,
)


async def get_trip_history(
    user_id: int,
) -> list[dict]:

    async with AsyncSessionLocal() as session:

        trips = await get_user_trips(
            session=session,
            user_id=user_id,
        )

        history = []

        for trip in trips:

            history.append(
                {
                    "id": trip.id,
                    "origin": trip.origin,
                    "destination": trip.destination,
                    "start_date": (
                        trip.start_date.isoformat()
                        if trip.start_date
                        else None
                    ),
                    "end_date": (
                        trip.end_date.isoformat()
                        if trip.end_date
                        else None
                    ),
                    "budget": (
                        float(trip.budget)
                        if trip.budget is not None
                        else None
                    ),
                    "adults": trip.adults,
                    "children": trip.children,
                    "user_query": trip.user_query,
                    "itinerary": trip.itinerary,
                    "final_response": trip.final_response,
                    "created_at": (
                        trip.created_at.isoformat()
                        if trip.created_at
                        else None
                    ),
                }
            )

        return history

async def get_saved_trip(
    trip_id: int,
) -> dict | None:

    async with AsyncSessionLocal() as session:

        trip = await get_trip_by_id(
            session=session,
            trip_id=trip_id,
        )

        if trip is None:
            return None

        return {
            "id": trip.id,
            "user_id": trip.user_id,
            "origin": trip.origin,
            "destination": trip.destination,
            "start_date": (
                trip.start_date.isoformat()
                if trip.start_date
                else None
            ),
            "end_date": (
                trip.end_date.isoformat()
                if trip.end_date
                else None
            ),
            "budget": (
                float(trip.budget)
                if trip.budget is not None
                else None
            ),
            "adults": trip.adults,
            "children": trip.children,
            "user_query": trip.user_query,
            "itinerary": trip.itinerary,
            "final_response": trip.final_response,
        }