from datetime import datetime

def calculate_trip_duration(start_date: str, end_date: str) -> str:
    """
    Calculate the duration of a trip.

    Dates must be provided in YYYY-MM-DD format.
    """

    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    if end < start:
        return "End date cannot be earlier than start date."

    nights = (end - start).days
    days = nights + 1

    return f"The trip duration is {days} days and {nights} nights."


def calculate_trip_budget(
    flight_cost: float,
    hotel_cost: float,
    activity_cost: float,
    food_cost: float,
) -> str:
    """
    Calculate the total estimated cost of a trip.

    Use this tool when the user provides travel expenses
    and wants to know the total trip budget.
    """

    total_cost = (
        flight_cost
        + hotel_cost
        + activity_cost
        + food_cost
    )

    return f"The estimated total trip cost is ₹{total_cost:,.2f}."