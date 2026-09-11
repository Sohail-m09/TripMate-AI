import pytest

from tripmate.mcp.client import (
    get_mcp_tools,
)


@pytest.mark.asyncio
async def test_trip_duration_mcp_tool():

    tools = await get_mcp_tools(
        "utility"
    )

    duration_tool = next(
        tool
        for tool in tools
        if tool.name == "trip_duration"
    )

    result = await duration_tool.ainvoke(
        {
            "start_date": "2026-10-10",
            "end_date": "2026-10-15",
        }
    )

    assert (
        "6 days and 5 nights"
        in str(result)
    )