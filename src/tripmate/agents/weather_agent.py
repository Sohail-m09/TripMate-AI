import asyncio

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from tripmate.agents.prompts import (
    WEATHER_AGENT_PROMPT,
)
from tripmate.agents.message_utils import (
    extract_message_text,
)
from tripmate.llm.model import get_gemini_model
from tripmate.mcp.client import get_mcp_tools
from tripmate.schemas import TravelAgentResponse


async def run_weather_agent(
    user_query: str,
) -> TravelAgentResponse:

    model = get_gemini_model()

    tools = await get_mcp_tools(
        "weather"
    )

    tools_by_name = {
        tool.name: tool
        for tool in tools
    }

    model_with_tools = model.bind_tools(
        tools
    )

    tools_used = []

    messages = [
        SystemMessage(
            content=WEATHER_AGENT_PROMPT
        ),
        HumanMessage(
            content=user_query
        ),
    ]

    for _ in range(3):

        response = await model_with_tools.ainvoke(
            messages
        )

        messages.append(response)

        if not response.tool_calls:
            return TravelAgentResponse(
                answer=extract_message_text(
                    response.content
                ),
                tools_used=tools_used,
                is_complete=True,
            )

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]

            if tool_name not in tools_by_name:
                return TravelAgentResponse(
                    answer=(
                        f"Weather tool '{tool_name}' "
                        "is not available."
                    ),
                    tools_used=tools_used,
                    is_complete=False,
                )

            selected_tool = tools_by_name[
                tool_name
            ]

            tool_result = await selected_tool.ainvoke(
                tool_call["args"]
            )

            tools_used.append(
                tool_name
            )

            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )

    return TravelAgentResponse(
        answer=(
            "The Weather Agent could not "
            "complete the request."
        ),
        tools_used=tools_used,
        is_complete=False,
    )


async def main() -> None:

    result = await run_weather_agent(
        "What is the current weather in Goa?"
    )

    print(
        result.model_dump()
    )


if __name__ == "__main__":
    asyncio.run(main())