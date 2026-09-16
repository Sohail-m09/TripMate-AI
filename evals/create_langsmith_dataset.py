from dotenv import load_dotenv
from langsmith import Client

load_dotenv()
client = Client()

DATASET_NAME = (
    "TripMate Evaluation Dataset v1"
)


examples = [

    # ===================================
    # ROUTING EXAMPLES
    # ===================================

    {
        "inputs": {
            "evaluation_type": "routing",
            "query": (
                "What is the weather like "
                "in Dubai?"
            ),
        },
        "outputs": {
            "expected_agents": [
                "weather"
            ],
        },
    },

    {
        "inputs": {
            "evaluation_type": "routing",
            "query": (
                "Find hotels in Goa."
            ),
        },
        "outputs": {
            "expected_agents": [
                "hotel"
            ],
        },
    },

    {
        "inputs": {
            "evaluation_type": "routing",
            "query": (
                "Find flights from Mumbai "
                "to Dubai."
            ),
        },
        "outputs": {
            "expected_agents": [
                "flight"
            ],
        },
    },

    {
        "inputs": {
            "evaluation_type": "routing",
            "query": (
                "Find attractions to visit "
                "in Singapore."
            ),
        },
        "outputs": {
            "expected_agents": [
                "places"
            ],
        },
    },

    {
        "inputs": {
            "evaluation_type": "routing",
            "query": (
                "Plan a complete trip from "
                "Mumbai to Dubai including "
                "flights, hotels, weather, "
                "attractions and itinerary."
            ),
        },
        "outputs": {
            "expected_agents": [
                "flight",
                "hotel",
                "weather",
                "places",
                "itinerary",
            ],
        },
    },

    # ===================================
    # EXTRACTION EXAMPLES
    # ===================================

    {
        "inputs": {
            "evaluation_type": (
                "extraction"
            ),
            "query": (
                "Plan a trip from Mumbai "
                "to Dubai from 10 November "
                "2026 to 15 November 2026 "
                "for 2 adults with a budget "
                "of ₹80,000."
            ),
        },

        "outputs": {
            "origin": "Mumbai",
            "destination": "Dubai",
            "start_date": "2026-11-10",
            "end_date": "2026-11-15",
            "budget": 80000.0,
            "adults": 2,
        },
    },

    {
        "inputs": {
            "evaluation_type": (
                "extraction"
            ),
            "query": (
                "Plan a Delhi to Singapore "
                "trip for 2 adults and "
                "1 child from 5 January 2027 "
                "to 10 January 2027 with a "
                "budget of ₹1,20,000."
            ),
        },

        "outputs": {
            "origin": "Delhi",
            "destination": (
                "Singapore"
            ),
            "start_date": "2027-01-05",
            "end_date": "2027-01-10",
            "budget": 120000.0,
            "adults": 2,
            "children": 1,
        },
    },

    {
        "inputs": {
            "evaluation_type": (
                "extraction"
            ),
            "query": (
                "Plan a trip to Bangkok "
                "for 2 adults."
            ),
        },

        "outputs": {
            "destination": "Bangkok",
            "adults": 2,
            "start_date": None,
            "end_date": None,
            "budget": None,
        },
    },

    # ===================================
    # GROUNDING EXAMPLES
    # ===================================

    {
        "inputs": {
            "evaluation_type": (
                "grounding"
            ),

            "query": (
                "Create a Dubai itinerary "
                "using the supplied travel "
                "information."
            ),

            "flight_info": (
                "Flight: Emirates EK501. "
                "Route: BOM to DXB. "
                "Price: ₹20,000 per adult."
            ),

            "hotel_info": (
                "Hotel: Marina Stay Dubai. "
                "Price: ₹6,000 per night."
            ),

            "weather_info": (
                "Dubai weather: sunny, "
                "32°C."
            ),

            "places_info": (
                "Burj Khalifa, Dubai Mall, "
                "Dubai Frame."
            ),
        },

        "outputs": {
            "minimum_grounding_score": 0.80,
            "serious_contradictions": 0,
        },
    },

    {
        "inputs": {
            "evaluation_type": (
                "grounding"
            ),

            "query": (
                "Create a Dubai itinerary. "
                "Do not invent flight details."
            ),

            "flight_info": None,

            "hotel_info": (
                "Hotel: Creek View Hotel."
            ),

            "weather_info": (
                "Clear skies, 30°C."
            ),

            "places_info": (
                "Dubai Frame and Dubai Mall."
            ),
        },

        "outputs": {
            "minimum_grounding_score": 0.80,
            "serious_contradictions": 0,
        },
    },

    {
        "inputs": {
            "evaluation_type": (
                "grounding"
            ),

            "query": (
                "Create an itinerary for "
                "my current Dubai trip."
            ),

            "hotel_info": (
                "Current hotel: "
                "Marina Stay Dubai."
            ),

            "weather_info": (
                "Current Dubai weather: "
                "31°C and sunny."
            ),

            "places_info": (
                "Burj Khalifa and Dubai Mall."
            ),

            "memory_context": (
                "Previous trip: Mumbai -> Goa. "
                "Hotel: Beach Inn Goa."
            ),
        },

        "outputs": {
            "minimum_grounding_score": 0.80,
            "serious_contradictions": 0,
        },
    },
]


def main():

    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description=(
            "Evaluation dataset for TripMate "
            "routing, structured extraction, "
            "and itinerary grounding."
        ),
    )

    for example in examples:

        client.create_example(
            dataset_id=dataset.id,
            inputs=example["inputs"],
            outputs=example["outputs"],
        )

    print(
        f"Created dataset: "
        f"{DATASET_NAME}"
    )

    print(
        f"Examples added: "
        f"{len(examples)}"
    )


if __name__ == "__main__":

    main()