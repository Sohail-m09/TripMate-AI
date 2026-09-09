from mcp.server.fastmcp import FastMCP

from tripmate.tools.travel_tools import (
    calculate_trip_budget,
    calculate_trip_duration,
)


mcp = FastMCP("TripMate Utility Server")


@mcp.tool()
def trip_duration(
    start_date: str,
    end_date: str,
) -> str:
    """
    Calculate the duration of a trip.

    Dates must use YYYY-MM-DD format.
    """

    return calculate_trip_duration(
        start_date=start_date,
        end_date=end_date,
    )


@mcp.tool()
def trip_budget(
    flight_cost: float,
    hotel_cost: float,
    activity_cost: float,
    food_cost: float,
) -> str:
    """
    Calculate the estimated total cost of a trip.
    """

    return calculate_trip_budget(
        flight_cost=flight_cost,
        hotel_cost=hotel_cost,
        activity_cost=activity_cost,
        food_cost=food_cost,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")