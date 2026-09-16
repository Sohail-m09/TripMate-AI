import asyncio

from tripmate.graph.nodes import (
    extract_trip_request,
)


EXTRACTION_CASES = [
    {
        "query": (
            "Plan a trip from Mumbai to Dubai "
            "from 10 November 2026 to "
            "15 November 2026 for 2 adults "
            "with a budget of ₹80,000."
        ),
        "expected": {
            "origin": "Mumbai",
            "destination": "Dubai",
            "start_date": "2026-11-10",
            "end_date": "2026-11-15",
            "budget": 80000.0,
            "adults": 2,
        },
    },

    {
        "query": (
            "I want to travel from Pune to Goa "
            "from 20 December 2026 to "
            "24 December 2026. "
            "It is for 1 adult."
        ),
        "expected": {
            "origin": "Pune",
            "destination": "Goa",
            "start_date": "2026-12-20",
            "end_date": "2026-12-24",
            "adults": 1,
        },
    },

    {
        "query": (
            "Plan a Delhi to Singapore trip "
            "for 2 adults and 1 child "
            "from 5 January 2027 to "
            "10 January 2027 with a "
            "budget of ₹1,20,000."
        ),
        "expected": {
            "origin": "Delhi",
            "destination": "Singapore",
            "start_date": "2027-01-05",
            "end_date": "2027-01-10",
            "budget": 120000.0,
            "adults": 2,
            "children": 1,
        },
    },

    {
        "query": (
            "Find hotels in Jaipur "
            "for 3 adults from "
            "1 November 2026 to "
            "4 November 2026."
        ),
        "expected": {
            "destination": "Jaipur",
            "start_date": "2026-11-01",
            "end_date": "2026-11-04",
            "adults": 3,
        },
    },

    {
        "query": (
            "What is the weather like "
            "in Tokyo?"
        ),
        "expected": {
            "destination": "Tokyo",
        },
    },

    {
        "query": (
            "Find a flight from Mumbai "
            "to Dubai on 18 February 2027."
        ),
        "expected": {
            "origin": "Mumbai",
            "destination": "Dubai",
            "start_date": "2027-02-18",
        },
    },

    {
        "query": (
            "Plan a trip to Bangkok "
            "for 2 adults."
        ),
        "expected": {
            "destination": "Bangkok",
            "adults": 2,

            # These were NOT supplied,
            # so the extractor should
            # not invent them.
            "start_date": None,
            "end_date": None,
            "budget": None,
        },
    },
]


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


async def main():

    passed_cases = 0

    total_fields = 0
    correct_fields = 0

    for index, case in enumerate(
        EXTRACTION_CASES,
        start=1,
    ):

        result = await extract_trip_request(
            case["query"]
        )

        actual = result.model_dump()

        expected = case[
            "expected"
        ]

        case_passed = True

        field_results = []

        for field, expected_value in (
            expected.items()
        ):

            actual_value = actual.get(
                field
            )

            matched = (
                normalize(actual_value)
                ==
                normalize(expected_value)
            )

            total_fields += 1

            if matched:
                correct_fields += 1
            else:
                case_passed = False

            field_results.append(
                {
                    "field": field,
                    "expected": expected_value,
                    "actual": actual_value,
                    "matched": matched,
                }
            )

        if case_passed:
            passed_cases += 1

        print(
            "\n"
            "================================"
        )

        print(
            f"Case {index}"
        )

        print(
            f"Query: {case['query']}"
        )

        print(
            "\nExtracted:"
        )

        print(
            actual
        )

        print(
            "\nField Comparison:"
        )

        for item in field_results:

            status = (
                "PASS"
                if item["matched"]
                else "FAIL"
            )

            print(
                f"{item['field']}: "
                f"expected="
                f"{item['expected']} | "
                f"actual="
                f"{item['actual']} | "
                f"{status}"
            )

        print(
            "\nCase Result: "
            + (
                "PASS"
                if case_passed
                else "FAIL"
            )
        )

    total_cases = len(
        EXTRACTION_CASES
    )

    case_accuracy = (
        passed_cases
        / total_cases
        * 100
    )

    field_accuracy = (
        correct_fields
        / total_fields
        * 100
    )

    print(
        "\n"
        "================================"
    )

    print(
        "FINAL EXTRACTION EVALUATION"
    )

    print(
        "================================"
    )

    print(
        f"Cases Passed: "
        f"{passed_cases}/{total_cases}"
    )

    print(
        f"Case Accuracy: "
        f"{case_accuracy:.2f}%"
    )

    print(
        f"Fields Correct: "
        f"{correct_fields}/{total_fields}"
    )

    print(
        f"Field Accuracy: "
        f"{field_accuracy:.2f}%"
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )