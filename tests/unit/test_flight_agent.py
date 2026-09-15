import pytest

import tripmate.agents.flight_agent as flight_agent


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
async def test_flight_agent_without_tool_call(
    monkeypatch,
):

    fake_model = FakeModel(
        responses=[
            FakeResponse(
                content=(
                    "Flights are available from "
                    "BOM to DXB."
                ),
                tool_calls=[],
            )
        ]
    )

    async def fake_get_mcp_tools(
        server_name,
    ):
        assert server_name == "flight"

        return []

    monkeypatch.setattr(
        flight_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        flight_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await flight_agent.run_flight_agent(
        "Find flights from BOM to DXB."
    )

    assert result.answer == (
        "Flights are available from "
        "BOM to DXB."
    )

    assert result.tools_used == []

    assert result.is_complete is True


# -----------------------------------
# Test: successful flight tool call
# -----------------------------------

@pytest.mark.asyncio
async def test_flight_agent_successful_tool_call(
    monkeypatch,
):

    fake_tool = FakeTool(
        name="find_flights",
        result={
            "origin": "BOM",
            "destination": "DXB",
            "flights": [
                {
                    "airline": "Test Airline",
                    "price": 15000,
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
                        "name": "find_flights",
                        "args": {
                            "origin": "BOM",
                            "destination": "DXB",
                            "departure_date": "2026-11-10",
                        },
                        "id": "flight-call-1",
                    }
                ],
            ),
            FakeResponse(
                content=(
                    "I found a flight from BOM "
                    "to DXB for ₹15,000."
                ),
                tool_calls=[],
            ),
        ]
    )

    async def fake_get_mcp_tools(
        server_name,
    ):
        assert server_name == "flight"

        return [
            fake_tool
        ]

    monkeypatch.setattr(
        flight_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        flight_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await flight_agent.run_flight_agent(
        (
            "Find flights from BOM to DXB "
            "on 2026-11-10."
        )
    )

    assert result.is_complete is True

    assert result.tools_used == [
        "find_flights"
    ]

    assert "BOM" in result.answer
    assert "DXB" in result.answer

    assert fake_tool.call_count == 1

    assert fake_tool.received_args == {
        "origin": "BOM",
        "destination": "DXB",
        "departure_date": "2026-11-10",
    }


# -----------------------------------
# Test: unavailable tool
# -----------------------------------

@pytest.mark.asyncio
async def test_flight_agent_unavailable_tool(
    monkeypatch,
):

    fake_tool = FakeTool(
        name="find_flights",
        result={},
    )

    fake_model = FakeModel(
        responses=[
            FakeResponse(
                content="",
                tool_calls=[
                    {
                        "name": "unknown_flight_tool",
                        "args": {
                            "origin": "BOM",
                            "destination": "DXB",
                        },
                        "id": "flight-call-1",
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
        flight_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        flight_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await flight_agent.run_flight_agent(
        "Find flights from BOM to DXB."
    )

    assert result.is_complete is False

    assert result.tools_used == []

    assert result.answer == (
        "Flight tool "
        "'unknown_flight_tool' "
        "is not available."
    )

    assert fake_tool.call_count == 0


# -----------------------------------
# Test: maximum agent loop reached
# -----------------------------------

@pytest.mark.asyncio
async def test_flight_agent_stops_after_three_iterations(
    monkeypatch,
):

    fake_tool = FakeTool(
        name="find_flights",
        result={
            "flights": []
        },
    )

    tool_call = {
        "name": "find_flights",
        "args": {
            "origin": "BOM",
            "destination": "DXB",
            "departure_date": "2026-11-10",
        },
        "id": "flight-call-1",
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
        flight_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        flight_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await flight_agent.run_flight_agent(
        (
            "Keep searching for flights "
            "from BOM to DXB."
        )
    )

    assert result.is_complete is False

    assert result.answer == (
        "The Flight Agent could not "
        "complete the request."
    )

    assert fake_tool.call_count == 3

    assert result.tools_used == [
        "find_flights",
        "find_flights",
        "find_flights",
    ]