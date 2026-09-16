import asyncio

from dotenv import load_dotenv
from langsmith import Client
from pydantic import (
    BaseModel,
    Field,
)

from tripmate.agents.orchestrator_agent import (
    run_orchestrator,
)
from tripmate.agents.itinerary_agent import (
    run_itinerary_agent,
)
from tripmate.graph.nodes import (
    extract_trip_request,
)
from tripmate.llm.model import (
    get_gemini_model,
)


load_dotenv()


DATASET_NAME = (
    "TripMate Evaluation Dataset v1"
)


# =================================================
# Grounding judge schema
# =================================================

class GroundingEvaluation(BaseModel):

    grounding_score: float = Field(
        ge=0.0,
        le=1.0,
    )

    coverage_score: float = Field(
        ge=0.0,
        le=1.0,
    )

    unsupported_claims: list[str] = Field(
        default_factory=list
    )

    contradictions: list[str] = Field(
        default_factory=list
    )

    reasoning: str


# =================================================
# Target function
# =================================================

async def tripmate_target(
    inputs: dict,
) -> dict:

    evaluation_type = inputs[
        "evaluation_type"
    ]

    query = inputs[
        "query"
    ]

    # ---------------------------------------------
    # Routing
    # ---------------------------------------------

    if evaluation_type == "routing":

        decision = await run_orchestrator(
            query
        )

        return {
            "evaluation_type": "routing",
            "actual_agents": (
                decision.required_agents
            ),
        }

    # ---------------------------------------------
    # Extraction
    # ---------------------------------------------

    if evaluation_type == "extraction":

        result = await extract_trip_request(
            query
        )

        return {
            "evaluation_type": "extraction",
            "extracted": result.model_dump(),
        }

    # ---------------------------------------------
    # Grounding
    # ---------------------------------------------

    if evaluation_type == "grounding":

        response = await run_itinerary_agent(
            user_query=query,

            flight_info=inputs.get(
                "flight_info"
            ),

            hotel_info=inputs.get(
                "hotel_info"
            ),

            weather_info=inputs.get(
                "weather_info"
            ),

            places_info=inputs.get(
                "places_info"
            ),

            memory_context=inputs.get(
                "memory_context"
            ),
        )

        return {
            "evaluation_type": "grounding",
            "itinerary": response.answer,
        }

    raise ValueError(
        f"Unknown evaluation type: "
        f"{evaluation_type}"
    )


# =================================================
# Helpers
# =================================================

def normalize(
    value,
):

    if isinstance(
        value,
        str,
    ):
        return value.strip().lower()

    if isinstance(
        value,
        float,
    ):
        return round(
            value,
            2,
        )

    return value


# =================================================
# Evaluator
# =================================================

async def tripmate_evaluator(
    inputs: dict,
    outputs: dict,
    reference_outputs: dict,
):

    evaluation_type = inputs[
        "evaluation_type"
    ]

    # ---------------------------------------------
    # ROUTING EVALUATION
    # ---------------------------------------------

    if evaluation_type == "routing":

        expected = set(
            reference_outputs[
                "expected_agents"
            ]
        )

        actual = set(
            outputs[
                "actual_agents"
            ]
        )

        correct = (
            actual == expected
        )

        return [
            {
                "key": "overall_score",
                "score": 1 if correct else 0,
            },
            {
                "key": "routing_exact_match",
                "score": 1 if correct else 0,
                "comment": (
                    f"Expected: "
                    f"{sorted(expected)} | "
                    f"Actual: "
                    f"{sorted(actual)}"
                ),
            },
        ]

    # ---------------------------------------------
    # EXTRACTION EVALUATION
    # ---------------------------------------------

    if evaluation_type == "extraction":

        actual = outputs[
            "extracted"
        ]

        total_fields = len(
            reference_outputs
        )

        correct_fields = 0

        mismatches = []

        for (
            field,
            expected_value,
        ) in reference_outputs.items():

            actual_value = actual.get(
                field
            )

            if (
                normalize(actual_value)
                ==
                normalize(expected_value)
            ):
                correct_fields += 1

            else:

                mismatches.append(
                    (
                        f"{field}: "
                        f"expected="
                        f"{expected_value}, "
                        f"actual="
                        f"{actual_value}"
                    )
                )

        field_accuracy = (
            correct_fields
            / total_fields
        )

        exact_match = (
            correct_fields
            == total_fields
        )

        return [
            {
                "key": "overall_score",
                "score": (
                    1
                    if exact_match
                    else 0
                ),
            },
            {
                "key": "extraction_exact_match",
                "score": (
                    1
                    if exact_match
                    else 0
                ),
            },
            {
                "key": "extraction_field_accuracy",
                "score": field_accuracy,
                "comment": (
                    "All expected fields matched."
                    if not mismatches
                    else " | ".join(
                        mismatches
                    )
                ),
            },
        ]

    # ---------------------------------------------
    # GROUNDING EVALUATION
    # ---------------------------------------------

    if evaluation_type == "grounding":

        model = get_gemini_model()

        judge = (
            model.with_structured_output(
                GroundingEvaluation
            )
        )

        itinerary = outputs[
            "itinerary"
        ]

        evidence = f"""
CURRENT USER REQUEST:
{inputs["query"]}

FLIGHT INFORMATION:
{inputs.get("flight_info") or "Not available."}

HOTEL INFORMATION:
{inputs.get("hotel_info") or "Not available."}

WEATHER INFORMATION:
{inputs.get("weather_info") or "Not available."}

PLACES INFORMATION:
{inputs.get("places_info") or "Not available."}

PREVIOUS TRIP MEMORY:
{inputs.get("memory_context") or "Not available."}

GENERATED ITINERARY:
{itinerary}
"""

        prompt = f"""
You are evaluating the grounding quality
of a generated travel itinerary.

Evaluate it only against the supplied
evidence.

Rules:

1. Specific factual claims about flights,
hotels, prices, weather, attractions or
previous trips must be supported.

2. Do not penalize reasonable itinerary
planning choices.

3. If information is unavailable, the
itinerary must not invent specific
provider details.

4. Previous-trip memory must not replace
or contradict current-trip information.

5. grounding_score ranges from 0.0 to 1.0.

6. coverage_score ranges from 0.0 to 1.0.

Evidence:

{evidence}
"""

        evaluation = await judge.ainvoke(
            prompt
        )

        minimum_score = (
            reference_outputs[
                "minimum_grounding_score"
            ]
        )

        serious_contradictions = (
            len(
                evaluation.contradictions
            )
        )

        passed = (
            evaluation.grounding_score
            >= minimum_score
            and serious_contradictions
            <= reference_outputs[
                "serious_contradictions"
            ]
        )

        comment = (
            f"{evaluation.reasoning} | "
            f"Unsupported claims: "
            f"{evaluation.unsupported_claims} | "
            f"Contradictions: "
            f"{evaluation.contradictions}"
        )

        return [
            {
                "key": "overall_score",
                "score": (
                    1
                    if passed
                    else 0
                ),
            },
            {
                "key": "grounding_score",
                "score": (
                    evaluation.grounding_score
                ),
                "comment": comment,
            },
            {
                "key": "coverage_score",
                "score": (
                    evaluation.coverage_score
                ),
            },
        ]

    raise ValueError(
        f"Unknown evaluation type: "
        f"{evaluation_type}"
    )


# =================================================
# Run experiment
# =================================================

async def main():

    client = Client()

    results = await client.aevaluate(
        tripmate_target,

        data=DATASET_NAME,

        evaluators=[
            tripmate_evaluator
        ],

        experiment_prefix=(
            "tripmate-baseline-v1"
        ),

        max_concurrency=2,

        metadata={
            "version": "baseline-v1",
            "project": "TripMate-AI",
            "model_provider": "Google Gemini",
        },
    )

    print(
        "\nExperiment completed."
    )

    print(
        results
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )