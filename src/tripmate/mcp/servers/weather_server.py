from mcp.server.fastmcp import FastMCP

from tripmate.services.weather_service import (
    get_current_weather,
)


mcp = FastMCP(
    "TripMate Weather Server"
)


@mcp.tool()
async def current_weather(
    location: str,
) -> dict:
    """
    Get the current weather for a city
    or travel destination.
    """

    result = await get_current_weather(
        location
    )

    return result.model_dump()


if __name__ == "__main__":
    mcp.run(
        transport="stdio"
    )