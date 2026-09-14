from fastapi import (
    APIRouter,
    HTTPException,
)
from tripmate.api.schemas import (
    AgentResultResponse,
    SavedTripResponse,
    TripHistoryResponse,
    TripPlanRequest,
    TripPlanResponse,
)
from tripmate.graph.builder import (
    compile_travel_graph,
)
from tripmate.database.trip_history import (
    get_saved_trip,
    get_trip_history,
)
from tripmate.database.user_service import (
    get_user,
)

router = APIRouter(
    prefix="/trips",
    tags=["Trips"],
)


travel_graph = compile_travel_graph()


@router.post(
    "/plan",
    response_model=TripPlanResponse,
)
async def plan_trip(
    request: TripPlanRequest,
) -> TripPlanResponse:

    # -----------------------------------
    # Validate user before running agents
    # -----------------------------------

    try:

        user = await get_user(
            user_id=request.user_id
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to validate user: "
                f"{exc}"
            ),
        ) from exc

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    # -----------------------------------
    # Prepare LangGraph state
    # -----------------------------------

    initial_state = {
        "user_id": request.user_id,
        "user_query": request.user_query,
        "completed_agents": [],
        "failed_agents": [],
    }

    # -----------------------------------
    # Execute agentic workflow
    # -----------------------------------

    try:

        result = await travel_graph.ainvoke(
            initial_state
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Trip planning workflow failed: "
                f"{exc}"
            ),
        ) from exc

    # -----------------------------------
    # Extract routing information
    # -----------------------------------

    routing_decision = result.get(
        "routing_decision"
    )

    flight_result = result.get(
        "flight_result"
    )

    hotel_result = result.get(
        "hotel_result"
    )

    weather_result = result.get(
        "weather_result"
    )

    places_result = result.get(
        "places_result"
    )

    required_agents = []

    if routing_decision is not None:

        required_agents = (
            routing_decision.required_agents
        )

    # -----------------------------------
    # Build clean API response
    # -----------------------------------

    return TripPlanResponse(

        final_response=result.get(
            "final_response"
        ),

        itinerary=result.get(
            "itinerary"
        ),

        flight_result=(
            AgentResultResponse(
                answer=flight_result.answer,
                tools_used=flight_result.tools_used,
                is_complete=flight_result.is_complete,
            )
            if flight_result
            else None
        ),

        hotel_result=(
            AgentResultResponse(
                answer=hotel_result.answer,
                tools_used=hotel_result.tools_used,
                is_complete=hotel_result.is_complete,
            )
            if hotel_result
            else None
        ),

        weather_result=(
            AgentResultResponse(
                answer=weather_result.answer,
                tools_used=weather_result.tools_used,
                is_complete=weather_result.is_complete,
            )
            if weather_result
            else None
        ),

        places_result=(
            AgentResultResponse(
                answer=places_result.answer,
                tools_used=places_result.tools_used,
                is_complete=places_result.is_complete,
            )
            if places_result
            else None
        ),

        required_agents=required_agents,

        completed_agents=result.get(
            "completed_agents",
            [],
        ),

        failed_agents=result.get(
            "failed_agents",
            [],
        ),

        memory_loaded=result.get(
            "memory_loaded",
            False,
        ),

        trip_saved=result.get(
            "trip_saved",
            False,
        ),

        saved_trip_id=result.get(
            "saved_trip_id"
        ),
    )

@router.get(
    "/history/{user_id}",
    response_model=TripHistoryResponse,
)
async def trip_history(
    user_id: int,
) -> TripHistoryResponse:

    if user_id <= 0:

        raise HTTPException(
            status_code=400,
            detail=(
                "user_id must be greater than 0."
            ),
        )

    # Check whether the user exists

    try:

        user = await get_user(
            user_id=user_id
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to validate user: "
                f"{exc}"
            ),
        ) from exc

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    # Retrieve trip history

    try:

        trips = await get_trip_history(
            user_id=user_id
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve trip history: "
                f"{exc}"
            ),
        ) from exc

    return TripHistoryResponse(
        user_id=user_id,
        total_trips=len(trips),
        trips=trips,
    )


@router.get(
    "/{trip_id}",
    response_model=SavedTripResponse,
)
async def saved_trip(
    trip_id: int,
) -> SavedTripResponse:

    if trip_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="trip_id must be greater than 0.",
        )

    try:

        trip = await get_saved_trip(
            trip_id=trip_id
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve saved trip: "
                f"{exc}"
            ),
        ) from exc

    if trip is None:

        raise HTTPException(
            status_code=404,
            detail="Trip not found.",
        )

    return SavedTripResponse(
        **trip
    )