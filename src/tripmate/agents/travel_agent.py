from langchain.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from tripmate.llm.model import get_gemini_model
from tripmate.mcp.client import get_mcp_tools
from tripmate.schemas import TravelAgentResponse


async def run_travel_agent(
    user_query: str,
) -> TravelAgentResponse:

    model = get_gemini_model()

    tools = await get_mcp_tools()

    tools_by_name = {
        tool.name: tool
        for tool in tools
    }

    model_with_tools = model.bind_tools(tools)

    messages = [
        SystemMessage(
            content=(
                "You are TripMate, an AI travel planning assistant. "
                "Use the available tools whenever they are useful. "
                "Do not perform deterministic calculations manually "
                "when an appropriate tool is available."
            )
        ),
        HumanMessage(content=user_query),
    ]

    tools_used = []

    for _ in range(3):

        response = await model_with_tools.ainvoke(
            messages
        )

        messages.append(response)

        if not response.tool_calls:

            return TravelAgentResponse(
                answer=str(response.content),
                tools_used=tools_used,
                is_complete=True,
            )

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]

            selected_tool = tools_by_name[
                tool_name
            ]

            tool_result = await selected_tool.ainvoke(
                tool_call["args"]
            )

            tools_used.append(tool_name)

            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )

    return TravelAgentResponse(
        answer="The agent could not complete the request.",
        tools_used=tools_used,
        is_complete=False,
    )