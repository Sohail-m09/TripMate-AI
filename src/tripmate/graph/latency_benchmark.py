import asyncio
from time import perf_counter

from tripmate.agents.flight_agent import (
    run_flight_agent,
)
from tripmate.agents.hotel_agent import (
    run_hotel_agent,
)
from tripmate.agents.orchestrator_agent import (
    run_orchestrator,
)
from tripmate.agents.places_agent import (
    run_places_agent,
)
from tripmate.agents.weather_agent import (
    run_weather_agent,
)


AGENT_RUNNERS = {
    "flight": run_flight_agent,
    "hotel": run_hotel_agent,
    "weather": run_weather_agent,
    "places": run_places_agent,
}


async def run_sequential_agents(
    user_query: str,
    selected_agents: list[str],
) -> tuple[float, dict]:

    results = {}

    start_time = perf_counter()

    for agent_name in selected_agents:

        runner = AGENT_RUNNERS[
            agent_name
        ]

        try:
            result = await runner(
                user_query
            )

            results[agent_name] = result

        except Exception as exc:
            results[agent_name] = exc

    end_time = perf_counter()

    duration = (
        end_time - start_time
    )

    return duration, results


async def run_parallel_agents(
    user_query: str,
    selected_agents: list[str],
) -> tuple[float, dict]:

    start_time = perf_counter()

    tasks = [
        AGENT_RUNNERS[agent_name](
            user_query
        )
        for agent_name in selected_agents
    ]

    outputs = await asyncio.gather(
        *tasks,
        return_exceptions=True,
    )

    end_time = perf_counter()

    duration = (
        end_time - start_time
    )

    results = dict(
        zip(
            selected_agents,
            outputs,
        )
    )

    return duration, results


def print_agent_status(
    results: dict,
) -> None:

    for agent_name, result in results.items():

        if isinstance(
            result,
            Exception,
        ):
            print(
                f"{agent_name}: FAILED "
                f"({result})"
            )

        else:
            print(
                f"{agent_name}: "
                f"is_complete="
                f"{result.is_complete}"
            )


async def main() -> None:

    user_query = (
        "Plan travel information for a Goa trip. "
        "Find flights from BOM to GOI "
        "on 2026-10-10. "
        "Find hotels in Goa from "
        "2026-10-10 to 2026-10-15 "
        "for 2 adults. "
        "Check the current weather in "
        "Goa, India. "
        "Find tourist attractions "
        "to visit in Goa."
    )

    decision = await run_orchestrator(
        user_query
    )

    selected_agents = [
        agent
        for agent in decision.required_agents
        if agent in AGENT_RUNNERS
    ]

    print(
        "\n=== ROUTING DECISION ==="
    )

    print(
        decision.model_dump()
    )

    print(
        "\n=== AGENTS SELECTED "
        "FOR BENCHMARK ==="
    )

    print(
        selected_agents
    )

    if len(selected_agents) < 2:

        print(
            "\nAt least two independent "
            "agents are required for a "
            "parallel latency comparison."
        )

        return

    print(
        "\n=== SEQUENTIAL RUN ==="
    )

    sequential_time, sequential_results = (
        await run_sequential_agents(
            user_query,
            selected_agents,
        )
    )

    print_agent_status(
        sequential_results
    )

    print(
        f"\nSequential time: "
        f"{sequential_time:.2f} seconds"
    )

    print(
        "\n=== PARALLEL RUN ==="
    )

    parallel_time, parallel_results = (
        await run_parallel_agents(
            user_query,
            selected_agents,
        )
    )

    print_agent_status(
        parallel_results
    )

    print(
        f"\nParallel time: "
        f"{parallel_time:.2f} seconds"
    )

    if parallel_time > 0:

        speedup = (
            sequential_time
            / parallel_time
        )

        improvement = (
            (
                sequential_time
                - parallel_time
            )
            / sequential_time
        ) * 100

        print(
            "\n=== LATENCY COMPARISON ==="
        )

        print(
            f"Speedup: "
            f"{speedup:.2f}x"
        )

        print(
            f"Latency reduction: "
            f"{improvement:.2f}%"
        )


if __name__ == "__main__":
    asyncio.run(main())