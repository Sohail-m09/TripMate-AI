import asyncio

from tripmate.database.connection import (
    engine,
)
from tripmate.database.trip_history import (
    get_saved_trip,
    get_trip_history,
)


async def main() -> None:

    user_id = 1

    history = await get_trip_history(
        user_id=user_id
    )

    print(
        "\n=== TRIP HISTORY ==="
    )

    print(
        "Total trips:",
        len(history)
    )

    for trip in history:

        print(
            f"Trip ID: {trip['id']}"
        )

        print(
            f"{trip['origin']} "
            f"-> {trip['destination']}"
        )

        print(
            "Dates:",
            trip["start_date"],
            "to",
            trip["end_date"],
        )

        print(
            "-" * 40
        )

    if history:

        latest_trip_id = history[0][
            "id"
        ]

        saved_trip = await get_saved_trip(
            latest_trip_id
        )

        print(
            "\n=== LATEST TRIP ==="
        )

        print(
            saved_trip
        )

    await engine.dispose()


if __name__ == "__main__":

    asyncio.run(
        main()
    )