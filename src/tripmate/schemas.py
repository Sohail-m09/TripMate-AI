from pydantic import BaseModel, Field


class TravelAgentResponse(BaseModel):
    answer: str = Field(
        description="Final answer returned to the user."
    )

    tools_used: list[str] = Field(
        default_factory=list,
        description="Names of tools used while processing the request."
    )

    is_complete: bool = Field(
        description="Whether the agent completed the user request successfully."
    )