import pytest

import tripmate.agents.places_agent as places_agent


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
async def test_places_agent_without_tool_call(
    monkeypatch,
):

    fake_model = FakeModel(
        responses=[
            FakeResponse(
                content=(
                    "Dubai has several popular "
                    "tourist attractions."
                ),
                tool_calls=[],
            )
        ]
    )

    async def fake_get_mcp_tools(
        server_name,
    ):
        assert server_name == "places"

        return []

    monkeypatch.setattr(
        places_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        places_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await places_agent.run_places_agent(
        "Find tourist attractions in Dubai."
    )

    assert result.answer == (
        "Dubai has several popular "
        "tourist attractions."
    )

    assert result.tools_used == []

    assert result.is_complete is True


# -----------------------------------
# Test: successful places tool call
# -----------------------------------

@pytest.mark.asyncio
async def test_places_agent_successful_tool_call(
    monkeypatch,
):

    fake_tool = FakeTool(
        name="find_places",
        result={
            "location": "Dubai, UAE",
            "places": [
                {
                    "name": "Burj Khalifa",
                    "category": "Landmark",
                },
                {
                    "name": "Dubai Mall",
                    "category": "Shopping",
                },
            ],
        },
    )

    fake_model = FakeModel(
        responses=[
            FakeResponse(
                content="",
                tool_calls=[
                    {
                        "name": "find_places",
                        "args": {
                            "location": "Dubai, UAE",
                            "query": "tourist attractions",
                        },
                        "id": "places-call-1",
                    }
                ],
            ),
            FakeResponse(
                content=(
                    "Popular places include "
                    "Burj Khalifa and Dubai Mall."
                ),
                tool_calls=[],
            ),
        ]
    )

    async def fake_get_mcp_tools(
        server_name,
    ):
        assert server_name == "places"

        return [
            fake_tool
        ]

    monkeypatch.setattr(
        places_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        places_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await places_agent.run_places_agent(
        (
            "Find tourist attractions "
            "in Dubai, UAE."
        )
    )

    assert result.is_complete is True

    assert result.tools_used == [
        "find_places"
    ]

    assert "Burj Khalifa" in result.answer

    assert fake_tool.call_count == 1

    assert fake_tool.received_args == {
        "location": "Dubai, UAE",
        "query": "tourist attractions",
    }


# -----------------------------------
# Test: unavailable tool
# -----------------------------------

@pytest.mark.asyncio
async def test_places_agent_unavailable_tool(
    monkeypatch,
):

    fake_tool = FakeTool(
        name="find_places",
        result={},
    )

    fake_model = FakeModel(
        responses=[
            FakeResponse(
                content="",
                tool_calls=[
                    {
                        "name": "unknown_places_tool",
                        "args": {
                            "location": "Dubai"
                        },
                        "id": "places-call-1",
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
        places_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        places_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await places_agent.run_places_agent(
        "Find places in Dubai."
    )

    assert result.is_complete is False

    assert result.tools_used == []

    assert result.answer == (
        "Places tool "
        "'unknown_places_tool' "
        "is not available."
    )

    assert fake_tool.call_count == 0


# -----------------------------------
# Test: maximum agent loop reached
# -----------------------------------

@pytest.mark.asyncio
async def test_places_agent_stops_after_three_iterations(
    monkeypatch,
):

    fake_tool = FakeTool(
        name="find_places",
        result={
            "places": []
        },
    )

    tool_call = {
        "name": "find_places",
        "args": {
            "location": "Dubai, UAE",
            "query": "tourist attractions",
        },
        "id": "places-call-1",
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
        places_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        places_agent,
        "get_mcp_tools",
        fake_get_mcp_tools,
    )

    result = await places_agent.run_places_agent(
        "Keep searching for attractions in Dubai."
    )

    assert result.is_complete is False

    assert result.answer == (
        "The Places Agent could not "
        "complete the request."
    )

    assert fake_tool.call_count == 3

    assert result.tools_used == [
        "find_places",
        "find_places",
        "find_places",
    ]