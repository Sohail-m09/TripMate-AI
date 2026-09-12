import asyncio

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from tripmate.agents.prompts import (
    ORCHESTRATOR_PROMPT,
)
from tripmate.llm.model import get_gemini_model
from tripmate.schemas import RoutingDecision


async def run_orchestrator(
    user_query: str,
) -> RoutingDecision:

    model = get_gemini_model()

    structured_model = (
        model.with_structured_output(
            RoutingDecision
        )
    )

    messages = [
        SystemMessage(
            content=ORCHESTRATOR_PROMPT
        ),
        HumanMessage(
            content=user_query
        ),
    ]

    decision = await structured_model.ainvoke(
        messages
    )

    return decision


async def main() -> None:

    decision = await run_orchestrator(
        (
            "Find flights from Mumbai to Goa, "
            "find a hotel in Goa, and create "
            "a 5-day itinerary."
        )
    )

    print(
        decision.model_dump()
    )


if __name__ == "__main__":
    asyncio.run(main())