import pytest

import tripmate.agents.hotel_agent as hotel_agent


# -----------------------------------
# Fake LLM response
# -----------------------------------

class FakeResponse:

    def __init__(
        self,
        content="",
        tool_calls=None,
    ):
        self.content = content
        self.tool_calls = tool_calls or []


# -----------------------------------
# Fake Gemini model
# -----------------------------------

class FakeModel:

    def __init__(
        self,
        responses,
    ):
        self.responses = list(responses)
        self.call_count = 0

    def bind_tools(
        self,
        tools,
    ):
        return self

    async def ainvoke(
        self,
        messages,
    ):
        response = self.responses[
            self.call_count
        ]

        self.call_count += 1

        return response


# -----------------------------------
# Fake MCP tool
# -----------------------------------

class FakeTool:

    def __init__(
        self,
        name,
        result,
    ):
        self.name = name
        self.result = result
        self.received_args = None
        self.call_count = 0

    async def ainvoke(
        self,
        args,
    ):
        self.received_args = args
        self.call_count += 1

        return self.result


# -----------------------------------
# Test: model answers without tool
# -----------------------------------

@pytest.mark.asyncio
async def test_hotel_agent_without_tool_call(
    monkeypatch,
):

    fake_model = FakeModel(
        responses=[
            FakeResponse(
                content=(
                    "Hotels are available in Dubai."
                ),
                tool_calls=[],
            )
        ]
    )

    async def fake_get_mcp_tools(
        server_name,
    ):
        assert server_name == "hotel"

        return []

    monkeypatch.setattr(
        hotel_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        hotel_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await hotel_agent.run_hotel_agent(
        "Find hotels in Dubai."
    )

    assert result.answer == (
        "Hotels are available in Dubai."
    )

    assert result.tools_used == []

    assert result.is_complete is True


# -----------------------------------
# Test: successful hotel tool call
# -----------------------------------

@pytest.mark.asyncio
async def test_hotel_agent_successful_tool_call(
    monkeypatch,
):

    fake_tool = FakeTool(
        name="find_hotels",
        result={
            "location": "Dubai, UAE",
            "hotels": [
                {
                    "name": "Test Hotel",
                    "rating": 4.5,
                    "price_per_night": 7000,
                }
            ],
        },
    )

    fake_model = FakeModel(
        responses=[
            FakeResponse(
                content="",
                tool_calls=[
                    {
                        "name": "find_hotels",
                        "args": {
                            "location": "Dubai, UAE",
                            "check_in": "2026-11-10",
                            "check_out": "2026-11-15",
                            "adults": 2,
                        },
                        "id": "hotel-call-1",
                    }
                ],
            ),
            FakeResponse(
                content=(
                    "I found a suitable hotel "
                    "in Dubai."
                ),
                tool_calls=[],
            ),
        ]
    )

    async def fake_get_mcp_tools(
        server_name,
    ):
        assert server_name == "hotel"

        return [
            fake_tool
        ]

    monkeypatch.setattr(
        hotel_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        hotel_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await hotel_agent.run_hotel_agent(
        (
            "Find hotels in Dubai, UAE "
            "from 2026-11-10 to 2026-11-15 "
            "for 2 adults."
        )
    )

    assert result.is_complete is True

    assert result.tools_used == [
        "find_hotels"
    ]

    assert "Dubai" in result.answer

    assert fake_tool.call_count == 1

    assert fake_tool.received_args == {
        "location": "Dubai, UAE",
        "check_in": "2026-11-10",
        "check_out": "2026-11-15",
        "adults": 2,
    }


# -----------------------------------
# Test: unavailable tool
# -----------------------------------

@pytest.mark.asyncio
async def test_hotel_agent_unavailable_tool(
    monkeypatch,
):

    fake_tool = FakeTool(
        name="find_hotels",
        result={},
    )

    fake_model = FakeModel(
        responses=[
            FakeResponse(
                content="",
                tool_calls=[
                    {
                        "name": "unknown_hotel_tool",
                        "args": {
                            "location": "Dubai"
                        },
                        "id": "hotel-call-1",
                    }
                ],
            )
        ]
    )

    async def fake_get_mcp_tools(
        server_name,
    ):
        return [
            fake_tool
        ]

    monkeypatch.setattr(
        hotel_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        hotel_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await hotel_agent.run_hotel_agent(
        "Find hotels in Dubai."
    )

    assert result.is_complete is False

    assert result.tools_used == []

    assert result.answer == (
        "Hotel tool "
        "'unknown_hotel_tool' "
        "is not available."
    )

    assert fake_tool.call_count == 0


# -----------------------------------
# Test: maximum agent loop reached
# -----------------------------------

@pytest.mark.asyncio
async def test_hotel_agent_stops_after_three_iterations(
    monkeypatch,
):

    fake_tool = FakeTool(
        name="find_hotels",
        result={
            "hotels": []
        },
    )

    tool_call = {
        "name": "find_hotels",
        "args": {
            "location": "Dubai, UAE",
            "check_in": "2026-11-10",
            "check_out": "2026-11-15",
            "adults": 2,
        },
        "id": "hotel-call-1",
    }

    fake_model = FakeModel(
        responses=[
            FakeResponse(
                tool_calls=[tool_call]
            ),
            FakeResponse(
                tool_calls=[tool_call]
            ),
            FakeResponse(
                tool_calls=[tool_call]
            ),
        ]
    )

    async def fake_get_mcp_tools(
        server_name,
    ):
        return [
            fake_tool
        ]

    monkeypatch.setattr(
        hotel_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        hotel_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await hotel_agent.run_hotel_agent(
        "Keep searching for hotels in Dubai."
    )

    assert result.is_complete is False

    assert result.answer == (
        "The Hotel Agent could not "
        "complete the request."
    )

    assert fake_tool.call_count == 3

    assert result.tools_used == [
        "find_hotels",
        "find_hotels",
        "find_hotels",
    ]