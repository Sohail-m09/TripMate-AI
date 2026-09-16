import asyncio

from pydantic import (
    BaseModel,
    Field,
)

from tripmate.agents.itinerary_agent import (
    run_itinerary_agent,
)

from tripmate.llm.model import (
    get_gemini_model,
)


# -------------------------------------------------
# Judge schema
# -------------------------------------------------

class GroundingEvaluation(BaseModel):

    grounding_score: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "How strongly the itinerary's factual "
            "claims are supported by the supplied "
            "travel information."
        ),
    )

    coverage_score: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "How well the itinerary uses the "
            "important supplied travel information."
        ),
    )

    unsupported_claims: list[str] = Field(
        default_factory=list,
        description=(
            "Specific factual claims that are not "
            "supported by the supplied context."
        ),
    )

    contradictions: list[str] = Field(
        default_factory=list,
        description=(
            "Claims that contradict the supplied "
            "travel information."
        ),
    )

    passed: bool

    reasoning: str


# -------------------------------------------------
# Controlled evaluation cases
# -------------------------------------------------

CASES = [
    {
        "name": "Complete grounded context",

        "user_query": (
            "Create a 3-day Dubai itinerary "
            "using the supplied travel information."
        ),

        "flight_info": (
            "Flight: Emirates EK501. "
            "Route: BOM to DXB. "
            "Departure: 10:00. "
            "Arrival: 12:00. "
            "Price: ₹20,000 per adult."
        ),

        "hotel_info": (
            "Hotel: Marina Stay Dubai. "
            "Price: ₹6,000 per night. "
            "Rating: 4.4/5."
        ),

        "weather_info": (
            "Dubai weather: sunny with "
            "a daytime temperature of 32°C."
        ),

        "places_info": (
            "Available attractions: "
            "Burj Khalifa, Dubai Mall, "
            "and Dubai Frame."
        ),

        "memory_context": None,
    },

    {
        "name": "Missing flight information",

        "user_query": (
            "Create a 2-day Dubai itinerary. "
            "Flight information is unavailable, "
            "so do not invent flight details."
        ),

        "flight_info": None,

        "hotel_info": (
            "Hotel: Creek View Hotel. "
            "Price: ₹5,500 per night."
        ),

        "weather_info": (
            "Weather: clear skies, 30°C."
        ),

        "places_info": (
            "Available attractions: "
            "Dubai Frame and Dubai Mall."
        ),

        "memory_context": None,
    },

    {
        "name": "Current trip versus memory",

        "user_query": (
            "Create an itinerary for my "
            "current Dubai trip."
        ),

        "flight_info": None,

        "hotel_info": (
            "Current hotel: Marina Stay Dubai."
        ),

        "weather_info": (
            "Current Dubai weather: 31°C "
            "and sunny."
        ),

        "places_info": (
            "Current attractions: "
            "Burj Khalifa and Dubai Mall."
        ),

        "memory_context": (
            "Previous Trip:\n"
            "Route: Mumbai -> Goa\n"
            "Hotel: Beach Inn Goa\n"
            "Budget: ₹30,000"
        ),
    },
]


# -------------------------------------------------
# LLM-as-judge
# -------------------------------------------------

async def evaluate_grounding(
    case,
    itinerary,
):

    model = get_gemini_model()

    judge = model.with_structured_output(
        GroundingEvaluation
    )

    evidence = f"""
CURRENT USER REQUEST:
{case["user_query"]}

FLIGHT INFORMATION:
{case["flight_info"] or "Not available."}

HOTEL INFORMATION:
{case["hotel_info"] or "Not available."}

WEATHER INFORMATION:
{case["weather_info"] or "Not available."}

PLACES INFORMATION:
{case["places_info"] or "Not available."}

PREVIOUS TRIP MEMORY:
{case["memory_context"] or "Not available."}

GENERATED ITINERARY:
{itinerary}
"""

    prompt = f"""
You are evaluating the grounding quality of
a travel itinerary.

Evaluate the generated itinerary only against
the supplied evidence.

Rules:

1. Specific factual claims about flights,
   hotels, prices, weather, attractions, or
   previous trips should be supported by the
   supplied information.

2. Do not penalize reasonable planning choices
   such as suggesting a morning or evening
   activity. Those are itinerary decisions,
   not factual provider claims.

3. If information is unavailable, the itinerary
   must not invent specific provider details.

4. Previous-trip memory is supporting context.
   It must not replace or contradict current-trip
   information.

5. grounding_score:
   1.0 means factual claims are fully grounded.
   0.0 means major unsupported information exists.

6. coverage_score:
   1.0 means the important supplied information
   was used well.

7. passed should be true only when:
   - grounding_score >= 0.80
   - there are no serious contradictions.

Evidence and itinerary:

{evidence}
"""

    return await judge.ainvoke(
        prompt
    )


async def main():

    passed = 0

    grounding_scores = []
    coverage_scores = []

    for index, case in enumerate(
        CASES,
        start=1,
    ):

        print(
            "\n"
            "================================"
        )

        print(
            f"Case {index}: "
            f"{case['name']}"
        )

        print(
            "================================"
        )

        response = await run_itinerary_agent(
            user_query=case[
                "user_query"
            ],
            flight_info=case[
                "flight_info"
            ],
            hotel_info=case[
                "hotel_info"
            ],
            weather_info=case[
                "weather_info"
            ],
            places_info=case[
                "places_info"
            ],
            memory_context=case[
                "memory_context"
            ],
        )

        itinerary = response.answer

        print(
            "\nGenerated Itinerary:\n"
        )

        print(
            itinerary
        )

        evaluation = (
            await evaluate_grounding(
                case,
                itinerary,
            )
        )

        grounding_scores.append(
            evaluation.grounding_score
        )

        coverage_scores.append(
            evaluation.coverage_score
        )

        if evaluation.passed:
            passed += 1

        print(
            "\nEvaluation:"
        )

        print(
            f"Grounding Score: "
            f"{evaluation.grounding_score:.2f}"
        )

        print(
            f"Coverage Score: "
            f"{evaluation.coverage_score:.2f}"
        )

        print(
            f"Unsupported Claims: "
            f"{evaluation.unsupported_claims}"
        )

        print(
            f"Contradictions: "
            f"{evaluation.contradictions}"
        )

        print(
            "Result: "
            + (
                "PASS"
                if evaluation.passed
                else "FAIL"
            )
        )

        print(
            f"Reasoning: "
            f"{evaluation.reasoning}"
        )

    total = len(
        CASES
    )

    average_grounding = (
        sum(grounding_scores)
        / total
    )

    average_coverage = (
        sum(coverage_scores)
        / total
    )

    pass_rate = (
        passed
        / total
        * 100
    )

    print(
        "\n"
        "================================"
    )

    print(
        "ITINERARY GROUNDING EVALUATION"
    )

    print(
        "================================"
    )

    print(
        f"Cases Passed: "
        f"{passed}/{total}"
    )

    print(
        f"Pass Rate: "
        f"{pass_rate:.2f}%"
    )

    print(
        f"Average Grounding Score: "
        f"{average_grounding:.2f}"
    )

    print(
        f"Average Coverage Score: "
        f"{average_coverage:.2f}"
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )