from datetime import date
from decimal import Decimal

from tripmate.database.connection import (
    AsyncSessionLocal,
)
from tripmate.database.repositories import (
    create_trip,
)
from tripmate.state import TravelState


def parse_date(
    value: str | None,
) -> date | None:

    if value is None:
        return None

    return date.fromisoformat(
        value
    )


def parse_budget(
    value: float | None,
) -> Decimal | None:

    if value is None:
        return None

    return Decimal(
        str(value)
    )


async def save_trip_from_state(
    state: TravelState,
) -> int:

    user_id = state.get(
        "user_id"
    )

    if user_id is None:
        raise ValueError(
            "user_id is required "
            "to persist a trip."
        )

    async with AsyncSessionLocal() as session:

        trip = await create_trip(
            session=session,
            user_id=user_id,
            user_query=state["user_query"],
            origin=state.get("origin"),
            destination=state.get(
                "destination"
            ),
            start_date=parse_date(
                state.get("start_date")
            ),
            end_date=parse_date(
                state.get("end_date")
            ),
            budget=parse_budget(
                state.get("budget")
            ),
            adults=state.get("adults"),
            children=state.get(
                "children"
            ),
            itinerary=state.get(
                "itinerary"
            ),
            final_response=state.get(
                "final_response"
            ),
        )

        return trip.id