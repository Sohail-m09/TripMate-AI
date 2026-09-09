from tripmate.tools.travel_tools import (
    calculate_trip_budget,
    calculate_trip_duration,
)


def test_calculate_trip_duration():

    result = calculate_trip_duration(
        start_date="2026-10-10",
        end_date="2026-10-15",
    )

    assert result == "The trip duration is 6 days and 5 nights."


def test_calculate_trip_budget():

    result = calculate_trip_budget(
        flight_cost=8500,
        hotel_cost=12000,
        activity_cost=3500,
        food_cost=5000,
    )

    assert result == "The estimated total trip cost is ₹29,000.00."