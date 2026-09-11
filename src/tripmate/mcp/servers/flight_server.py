from mcp.server.fastmcp import FastMCP

from tripmate.services.flight_service import (
    search_flights,
)


mcp = FastMCP(
    "TripMate Flight Server"
)


@mcp.tool()
async def find_flights(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
) -> dict:

    result = await search_flights(
        departure_id=departure_id,
        arrival_id=arrival_id,
        outbound_date=outbound_date,
    )

    return result.model_dump()


if __name__ == "__main__":
    mcp.run(
        transport="stdio"
    )