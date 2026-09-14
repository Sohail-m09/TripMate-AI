import asyncio

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from tripmate.agents.prompts import (
    TRIP_REQUEST_PROMPT,
)
from tripmate.llm.model import get_gemini_model
from tripmate.schemas import TripRequest


async def extract_trip_request(
    user_query: str,
) -> TripRequest:

    model = get_gemini_model()

    structured_model = (
        model.with_structured_output(
            TripRequest
        )
    )

    messages = [
        SystemMessage(
            content=TRIP_REQUEST_PROMPT
        ),
        HumanMessage(
            content=user_query
        ),
    ]

    result = await structured_model.ainvoke(
        messages
    )

    return result


async def main() -> None:

    result = await extract_trip_request(
        "Plan a trip to Jeddah, Saudi Arabia. "
        "Search for flights from BOM to JED "
        "on 2026-10-10. "
        "Find hotels in Jeddah, Saudi Arabia "
        "from 2026-10-10 to 2026-10-15 "
        "for 2 adults."
    )

    print(
        result.model_dump()
    )


if __name__ == "__main__":
    asyncio.run(main())