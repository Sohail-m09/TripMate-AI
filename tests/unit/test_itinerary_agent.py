import pytest

import tripmate.agents.itinerary_agent as itinerary_agent


# -----------------------------------
# Fake Gemini response
# -----------------------------------

class FakeResponse:

    def __init__(
        self,
        content,
    ):
        self.content = content


# -----------------------------------
# Fake Gemini model
# -----------------------------------

class FakeModel:

    def __init__(
        self,
        response,
    ):
        self.response = response
        self.received_messages = None
        self.call_count = 0

    async def ainvoke(
        self,
        messages,
    ):
        self.received_messages = messages
        self.call_count += 1

        return self.response


# -----------------------------------
# Test: basic itinerary generation
# -----------------------------------

@pytest.mark.asyncio
async def test_itinerary_agent_basic_generation(
    monkeypatch,
):

    fake_model = FakeModel(
        FakeResponse(
            content=(
                "Day 1: Explore Dubai.\n"
                "Day 2: Visit major attractions."
            )
        )
    )

    monkeypatch.setattr(
        itinerary_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    result = await itinerary_agent.run_itinerary_agent(
        user_query=(
            "Create a 2-day Dubai itinerary."
        )
    )

    assert result.is_complete is True

    assert result.tools_used == []

    assert "Day 1" in result.answer

    assert fake_model.call_count == 1


# -----------------------------------
# Test: specialist information
# is included in model context
# -----------------------------------

@pytest.mark.asyncio
async def test_itinerary_agent_includes_specialist_context(
    monkeypatch,
):

    fake_model = FakeModel(
        FakeResponse(
            content="Complete Dubai itinerary."
        )
    )

    monkeypatch.setattr(
        itinerary_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    await itinerary_agent.run_itinerary_agent(
        user_query=(
            "Create a Dubai itinerary."
        ),
        flight_info=(
            "Flight BOM to DXB arrives at 10 AM."
        ),
        hotel_info=(
            "Hotel check-in is at 2 PM."
        ),
        weather_info=(
            "Weather is sunny and warm."
        ),
        places_info=(
            "Visit Burj Khalifa and Dubai Mall."
        ),
    )

    messages = fake_model.received_messages

    human_message = messages[1]

    context = human_message.content

    assert (
        "Create a Dubai itinerary."
        in context
    )

    assert (
        "Flight BOM to DXB arrives at 10 AM."
        in context
    )

    assert (
        "Hotel check-in is at 2 PM."
        in context
    )

    assert (
        "Weather is sunny and warm."
        in context
    )

    assert (
        "Visit Burj Khalifa and Dubai Mall."
        in context
    )


# -----------------------------------
# Test: previous trip memory included
# -----------------------------------

@pytest.mark.asyncio
async def test_itinerary_agent_includes_memory(
    monkeypatch,
):

    fake_model = FakeModel(
        FakeResponse(
            content="Personalized itinerary."
        )
    )

    monkeypatch.setattr(
        itinerary_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    await itinerary_agent.run_itinerary_agent(
        user_query=(
            "Create another travel itinerary."
        ),
        memory_context=(
            "Previous trip: Mumbai to Goa "
            "for 3 days."
        ),
    )

    messages = fake_model.received_messages

    context = messages[1].content

    assert (
        "Previous Trip History:"
        in context
    )

    assert (
        "Previous trip: Mumbai to Goa "
        "for 3 days."
        in context
    )


# -----------------------------------
# Test: no-memory fallback
# -----------------------------------

@pytest.mark.asyncio
async def test_itinerary_agent_without_memory(
    monkeypatch,
):

    fake_model = FakeModel(
        FakeResponse(
            content="Generated itinerary."
        )
    )

    monkeypatch.setattr(
        itinerary_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    await itinerary_agent.run_itinerary_agent(
        user_query=(
            "Create a Singapore itinerary."
        ),
        memory_context=None,
    )

    messages = fake_model.received_messages

    context = messages[1].content

    assert (
        "No previous trip history is available."
        in context
    )


# -----------------------------------
# Test: missing specialist results
# use fallback text
# -----------------------------------

@pytest.mark.asyncio
async def test_itinerary_agent_missing_specialist_information(
    monkeypatch,
):

    fake_model = FakeModel(
        FakeResponse(
            content="Generated itinerary."
        )
    )

    monkeypatch.setattr(
        itinerary_agent,
        "get_gemini_model",
        lambda: fake_model,
    )

    await itinerary_agent.run_itinerary_agent(
        user_query=(
            "Create an itinerary."
        )
    )

    context = (
        fake_model
        .received_messages[1]
        .content
    )

    assert (
        "Flight Information:\nNot available."
        in context
    )

    assert (
        "Hotel Information:\nNot available."
        in context
    )

    assert (
        "Weather Information:\nNot available."
        in context
    )

    assert (
        "Places Information:\nNot available."
        in context
    )
    