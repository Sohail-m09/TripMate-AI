import asyncio

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from tripmate import state
from tripmate.agents.prompts import (
    ITINERARY_AGENT_PROMPT,
)
from tripmate.agents.message_utils import (
    extract_message_text,
)
from tripmate.llm.model import get_gemini_model
from tripmate.schemas import TravelAgentResponse


async def run_itinerary_agent(
    user_query: str,
    flight_info: str | None = None,
    hotel_info: str | None = None,
    weather_info: str | None = None,
    places_info: str | None = None,
    memory_context: str | None = None,
) -> TravelAgentResponse:

    model = get_gemini_model()

    memory_section = (
        memory_context
        if memory_context
        else "No previous trip history is available."
    )

    context = f"""
Current User Request:
{user_query}

Flight Information:
{flight_info or "Not available."}

Hotel Information:
{hotel_info or "Not available."}

Weather Information:
{weather_info or "Not available."}

Places Information:
{places_info or "Not available."}

Previous Trip History:
{memory_section}
"""

    messages = [
        SystemMessage(
            content=ITINERARY_AGENT_PROMPT
        ),
        HumanMessage(
            content=context
        ),
    ]

    response = await model.ainvoke(
        messages
    )

    answer = extract_message_text(
        response.content
    )

    return TravelAgentResponse(
        answer=answer,
        tools_used=[],
        is_complete=True,
    )


async def main() -> None:

    result = await run_itinerary_agent(
        user_query=(
            "Create a 3-day Goa itinerary "
            "for a leisure trip."
        ),
        flight_info=(
            "Flight from Mumbai to Goa arrives "
            "in Goa at 10:30 AM."
        ),
        hotel_info=(
            "Hotel check-in is available from "
            "2:00 PM."
        ),
        weather_info=(
            "Current weather is warm with "
            "low precipitation."
        ),
        places_info=(
            "Available places include Baga Beach, "
            "Calangute Beach, and Basilica of Bom Jesus."
        ),
        memory_context=state.get(
        "memory_context"
        ),
    )

    print(
        result.model_dump()
    )


if __name__ == "__main__":
    asyncio.run(main())