import pytest

import tripmate.agents.weather_agent as weather_agent


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
async def test_weather_agent_without_tool_call(
    monkeypatch,
):

    fake_model = FakeModel(
        responses=[
            FakeResponse(
                content=(
                    "The weather in Goa is sunny."
                ),
                tool_calls=[],
            )
        ]
    )

    async def fake_get_mcp_tools(
        server_name,
    ):
        assert server_name == "weather"

        return []

    monkeypatch.setattr(
        weather_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        weather_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await weather_agent.run_weather_agent(
        "What is the weather in Goa?"
    )

    assert result.answer == (
        "The weather in Goa is sunny."
    )

    assert result.tools_used == []

    assert result.is_complete is True


# -----------------------------------
# Test: successful weather tool call
# -----------------------------------

@pytest.mark.asyncio
async def test_weather_agent_successful_tool_call(
    monkeypatch,
):

    fake_tool = FakeTool(
        name="current_weather",
        result={
            "location": "Goa",
            "temperature": 30,
            "condition": "Sunny",
        },
    )

    fake_model = FakeModel(
        responses=[
            FakeResponse(
                content="",
                tool_calls=[
                    {
                        "name": "current_weather",
                        "args": {
                            "location": "Goa"
                        },
                        "id": "weather-call-1",
                    }
                ],
            ),
            FakeResponse(
                content=(
                    "The current weather in Goa "
                    "is sunny with a temperature "
                    "of 30°C."
                ),
                tool_calls=[],
            ),
        ]
    )

    async def fake_get_mcp_tools(
        server_name,
    ):
        assert server_name == "weather"

        return [
            fake_tool
        ]

    monkeypatch.setattr(
        weather_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        weather_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await weather_agent.run_weather_agent(
        "What is the current weather in Goa?"
    )

    assert result.is_complete is True

    assert result.tools_used == [
        "current_weather"
    ]

    assert (
        "sunny"
        in result.answer.lower()
    )

    assert fake_tool.call_count == 1

    assert fake_tool.received_args == {
        "location": "Goa"
    }


# -----------------------------------
# Test: unavailable tool
# -----------------------------------

@pytest.mark.asyncio
async def test_weather_agent_unavailable_tool(
    monkeypatch,
):

    fake_tool = FakeTool(
        name="current_weather",
        result={
            "temperature": 30
        },
    )

    fake_model = FakeModel(
        responses=[
            FakeResponse(
                content="",
                tool_calls=[
                    {
                        "name": "unknown_weather_tool",
                        "args": {
                            "location": "Goa"
                        },
                        "id": "weather-call-1",
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
        weather_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        weather_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await weather_agent.run_weather_agent(
        "What is the weather in Goa?"
    )

    assert result.is_complete is False

    assert result.tools_used == []

    assert result.answer == (
        "Weather tool "
        "'unknown_weather_tool' "
        "is not available."
    )

    assert fake_tool.call_count == 0


# -----------------------------------
# Test: maximum agent loop reached
# -----------------------------------

@pytest.mark.asyncio
async def test_weather_agent_stops_after_three_iterations(
    monkeypatch,
):

    fake_tool = FakeTool(
        name="current_weather",
        result={
            "location": "Goa",
            "temperature": 30,
        },
    )

    tool_call = {
        "name": "current_weather",
        "args": {
            "location": "Goa"
        },
        "id": "weather-call-1",
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
        weather_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        weather_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await weather_agent.run_weather_agent(
        "Keep checking the weather."
    )

    assert result.is_complete is False

    assert result.answer == (
        "The Weather Agent could not "
        "complete the request."
    )

    assert fake_tool.call_count == 3

    assert result.tools_used == [
        "current_weather",
        "current_weather",
        "current_weather",
    ]