import pytest

from tripmate.tools.travel_tools import (
    calculate_trip_budget,
    calculate_trip_duration,
)


def test_trip_duration_multiple_days():

    result = calculate_trip_duration(
        "2026-11-10",
        "2026-11-15",
    )

    assert result == (
        "The trip duration is "
        "6 days and 5 nights."
    )


def test_trip_duration_same_day():

    result = calculate_trip_duration(
        "2026-11-10",
        "2026-11-10",
    )

    assert result == (
        "The trip duration is "
        "1 days and 0 nights."
    )


def test_trip_duration_end_before_start():

    result = calculate_trip_duration(
        "2026-11-15",
        "2026-11-10",
    )

    assert result == (
        "End date cannot be earlier "
        "than start date."
    )


def test_trip_duration_invalid_start_date():

    with pytest.raises(ValueError):

        calculate_trip_duration(
            "10-11-2026",
            "2026-11-15",
        )


def test_trip_duration_invalid_end_date():

    with pytest.raises(ValueError):

        calculate_trip_duration(
            "2026-11-10",
            "15-11-2026",
        )


def test_trip_budget():

    result = calculate_trip_budget(
        flight_cost=10000,
        hotel_cost=25000,
        activity_cost=5000,
        food_cost=7000,
    )

    assert result == (
        "The estimated total trip cost "
        "is ₹47,000.00."
    )


def test_trip_budget_with_decimals():

    result = calculate_trip_budget(
        flight_cost=1000.50,
        hotel_cost=2000.25,
        activity_cost=300.10,
        food_cost=400.15,
    )

    assert result == (
        "The estimated total trip cost "
        "is ₹3,701.00."
    )


def test_trip_budget_zero_cost():

    result = calculate_trip_budget(
        flight_cost=0,
        hotel_cost=0,
        activity_cost=0,
        food_cost=0,
    )

    assert result == (
        "The estimated total trip cost "
        "is ₹0.00."
    )