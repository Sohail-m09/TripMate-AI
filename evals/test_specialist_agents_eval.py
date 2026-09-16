import asyncio
import time

from tripmate.agents.flight_agent import (
    run_flight_agent,
)
from tripmate.agents.hotel_agent import (
    run_hotel_agent,
)
from tripmate.agents.weather_agent import (
    run_weather_agent,
)
from tripmate.agents.places_agent import (
    run_places_agent,
)


AGENT_CASES = [
    {
        "name": "Flight Agent",
        "runner": run_flight_agent,
        "query": (
            "Find flights from BOM to DXB "
            "departing on 2026-11-10 "
            "for 2 adults."
        ),
        "expected_tool": "find_flights",
    },

    {
        "name": "Hotel Agent",
        "runner": run_hotel_agent,
        "query": (
            "Find hotels in Dubai, UAE. "
            "Check-in date: 2026-11-10. "
            "Check-out date: 2026-11-15. "
            "Adults: 2. "
            "Children: 0."
        ),
        "expected_tool": "find_hotels",
    },

    {
        "name": "Weather Agent",
        "runner": run_weather_agent,
        "query": (
            "Get the current weather "
            "for Dubai, UAE."
        ),
        "expected_tool": "current_weather",
    },

    {
        "name": "Places Agent",
        "runner": run_places_agent,
        "query": (
            "Find tourist attractions "
            "in Dubai, UAE."
        ),
        "expected_tool": "find_places",
    },
]


async def main():

    tool_successes = 0
    completion_successes = 0
    answer_successes = 0

    results = []

    for case in AGENT_CASES:

        print(
            "\n"
            "================================"
        )

        print(
            case["name"]
        )

        print(
            "================================"
        )

        print(
            f"Query: {case['query']}"
        )

        start = time.perf_counter()

        try:

            response = await case[
                "runner"
            ](
                case["query"]
            )

            error = None

        except Exception as exc:

            response = None
            error = str(exc)

        latency = (
            time.perf_counter()
            - start
        )

        if response is None:

            print(
                f"ERROR: {error}"
            )

            results.append(
                {
                    "name": case["name"],
                    "tool_correct": False,
                    "answer_present": False,
                    "complete": False,
                    "latency": latency,
                }
            )

            continue

        expected_tool = case[
            "expected_tool"
        ]

        tool_correct = (
            expected_tool
            in response.tools_used
        )

        answer_present = bool(
            response.answer
            and response.answer.strip()
        )

        complete = (
            response.is_complete
        )

        if tool_correct:
            tool_successes += 1

        if answer_present:
            answer_successes += 1

        if complete:
            completion_successes += 1

        results.append(
            {
                "name": case["name"],
                "tool_correct": tool_correct,
                "answer_present": answer_present,
                "complete": complete,
                "latency": latency,
            }
        )

        print(
            f"Expected Tool: "
            f"{expected_tool}"
        )

        print(
            f"Tools Used: "
            f"{response.tools_used}"
        )

        print(
            f"Tool Selection: "
            + (
                "PASS"
                if tool_correct
                else "FAIL"
            )
        )

        print(
            f"Answer Present: "
            + (
                "PASS"
                if answer_present
                else "FAIL"
            )
        )

        print(
            f"Agent Complete: "
            f"{complete}"
        )

        print(
            f"Latency: "
            f"{latency:.2f} seconds"
        )

        print(
            "\nAnswer:"
        )

        print(
            response.answer
        )

    total = len(
        AGENT_CASES
    )

    tool_accuracy = (
        tool_successes
        / total
        * 100
    )

    answer_accuracy = (
        answer_successes
        / total
        * 100
    )

    completion_rate = (
        completion_successes
        / total
        * 100
    )

    print(
        "\n"
        "================================"
    )

    print(
        "SPECIALIST AGENT EVALUATION"
    )

    print(
        "================================"
    )

    print(
        f"Correct Tool Usage: "
        f"{tool_successes}/{total}"
    )

    print(
        f"Tool Accuracy: "
        f"{tool_accuracy:.2f}%"
    )

    print(
        f"Answers Generated: "
        f"{answer_successes}/{total}"
    )

    print(
        f"Answer Rate: "
        f"{answer_accuracy:.2f}%"
    )

    print(
        f"Agents Complete: "
        f"{completion_successes}/{total}"
    )

    print(
        f"Completion Rate: "
        f"{completion_rate:.2f}%"
    )

    print(
        "\nLatency:"
    )

    for result in results:

        print(
            f"{result['name']}: "
            f"{result['latency']:.2f}s"
        )


if __name__ == "__main__":

    asyncio.run(
        main()
    )