from mcp.server.fastmcp import FastMCP

from tripmate.services.places_service import (
    search_places,
)


mcp = FastMCP(
    "TripMate Places Server"
)


@mcp.tool()
async def find_places(
    location: str,
    query: str = "tourist attractions",
) -> dict:

    result = await search_places(
        location=location,
        query=query,
    )

    return result.model_dump()


if __name__ == "__main__":
    mcp.run(
        transport="stdio"
    )