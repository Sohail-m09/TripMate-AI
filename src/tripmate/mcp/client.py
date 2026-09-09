import sys

from langchain_mcp_adapters.client import MultiServerMCPClient


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
            }
        }
    )

    return client


async def get_mcp_tools():

    client = get_mcp_client()

    tools = await client.get_tools(
        server_name="utility"
    )

    return tools