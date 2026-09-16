import asyncio
import os
import sys

from langchain_mcp_adapters.client import (
    MultiServerMCPClient,
)


def get_mcp_environment() -> dict[str, str]:

    keys = [
        "GEMINI_API_KEY",
        "GEMINI_MODEL",
        "SERPAPI_API_KEY",
        "DATABASE_URL",
        "LANGSMITH_TRACING",
        "LANGSMITH_API_KEY",
        "LANGSMITH_PROJECT",
    ]

    return {
        key: value
        for key in keys
        if (
            value := os.getenv(key)
        ) is not None
    }


def get_mcp_client() -> MultiServerMCPClient:

    mcp_env = get_mcp_environment()

    client = MultiServerMCPClient(
        {
            "utility": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    "-m",
                    "tripmate.mcp.servers.utility_server",
                ],
                "env": mcp_env,
            },

            "weather": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    "-m",
                    "tripmate.mcp.servers.weather_server",
                ],
                "env": mcp_env,
            },

            "flight": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    "-m",
                    "tripmate.mcp.servers.flight_server",
                ],
                "env": mcp_env,
            },

            "hotel": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    "-m",
                    "tripmate.mcp.servers.hotel_server",
                ],
                "env": mcp_env,
            },

            "places": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    "-m",
                    "tripmate.mcp.servers.places_server",
                ],
                "env": mcp_env,
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


async def main() -> None:

    tools = await get_mcp_tools(
        "places"
    )

    print(
        [tool.name for tool in tools]
    )


if __name__ == "__main__":
    asyncio.run(main())