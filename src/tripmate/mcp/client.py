import sys

from langchain_mcp_adapters.client import (
    MultiServerMCPClient,
)


def get_mcp_client() -> MultiServerMCPClient:

    client = MultiServerMCPClient(
        {
            "utility": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    "-m",
                    "tripmate.mcp.servers.utility_server",
                ],
            },

            "weather": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    "-m",
                    "tripmate.mcp.servers.weather_server",
                ],
            },

            "flight": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    "-m",
                    "tripmate.mcp.servers.flight_server",
                ],
            },

            "hotel": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    "-m",
                    "tripmate.mcp.servers.hotel_server",
                ],
            },

            "places": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    "-m",
                    "tripmate.mcp.servers.places_server",
                ],
            },

        }
    )

    return client


async def get_mcp_tools(
    server_name: str,
):

    client = get_mcp_client()

    tools = await client.get_tools(
        server_name=server_name
    )

    return tools

import asyncio


async def main() -> None:

    tools = await get_mcp_tools(
        "places"
    )

    print(
        [tool.name for tool in tools]
    )


if __name__ == "__main__":
    asyncio.run(main())