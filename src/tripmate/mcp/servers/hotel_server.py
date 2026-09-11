from mcp.server.fastmcp import FastMCP

from tripmate.services.hotel_service import (
    search_hotels,
)


mcp = FastMCP(
    "TripMate Hotel Server"
)


@mcp.tool()
async def find_hotels(
    location: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 2,
) -> dict:

    result = await search_hotels(
        location=location,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        adults=adults,
    )

    return result.model_dump()


if __name__ == "__main__":
    mcp.run(
        transport="stdio"
    )