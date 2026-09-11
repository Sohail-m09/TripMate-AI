import pytest

from tripmate.mcp.client import (
    get_mcp_tools,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "server_name, expected_tool",
    [
        ("weather", "current_weather"),
        ("flight", "find_flights"),
        ("hotel", "find_hotels"),
        ("places", "find_places"),
    ],
)
async def test_domain_mcp_tool_discovery(
    server_name: str,
    expected_tool: str,
):

    tools = await get_mcp_tools(
        server_name
    )

    tool_names = [
        tool.name
        for tool in tools
    ]

    assert expected_tool in tool_names