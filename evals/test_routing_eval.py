import asyncio

from tripmate.agents.orchestrator_agent import (
    run_orchestrator,
)


ROUTING_CASES = [
    {
        "query": (
            "What is the weather like "
            "in Dubai?"
        ),
        "expected": {
            "weather"
        },
    },
    {
        "query": (
            "Find hotels in Goa "
            "for my vacation."
        ),
        "expected": {
            "hotel"
        },
    },
    {
        "query": (
            "Find flights from Mumbai "
            "to Dubai."
        ),
        "expected": {
            "flight"
        },
    },
    {
        "query": (
            "What tourist attractions "
            "should I visit in Singapore?"
        ),
        "expected": {
            "places"
        },
    },
    {
        "query": (
            "Create an itinerary for "
            "my trip to Dubai."
        ),
        "expected": {
            "itinerary"
        },
    },
    {
        "query": (
            "Find hotels and tourist "
            "attractions in Dubai."
        ),
        "expected": {
            "hotel",
            "places",
        },
    },
    {
        "query": (
            "Plan a complete trip from "
            "Mumbai to Dubai including "
            "flights, hotels, weather, "
            "attractions and itinerary."
        ),
        "expected": {
            "flight",
            "hotel",
            "weather",
            "places",
            "itinerary",
        },
    },
]


async def main():

    passed = 0

    for index, case in enumerate(
        ROUTING_CASES,
        start=1,
    ):

        decision = await run_orchestrator(
            case["query"]
        )

        actual = set(
            decision.required_agents
        )

        expected = case["expected"]

        success = (
            actual == expected
        )

        if success:
            passed += 1

        print(
            "\n"
            f"Case {index}"
        )

        print(
            f"Query: {case['query']}"
        )

        print(
            f"Expected: "
            f"{sorted(expected)}"
        )

        print(
            f"Actual:   "
            f"{sorted(actual)}"
        )

        print(
            "Result: "
            + (
                "PASS"
                if success
                else "FAIL"
            )
        )

    total = len(
        ROUTING_CASES
    )

    accuracy = (
        passed / total
    ) * 100

    print(
        "\n"
        "-------------------------"
    )

    print(
        f"Passed: {passed}/{total}"
    )

    print(
        f"Routing Accuracy: "
        f"{accuracy:.2f}%"
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )