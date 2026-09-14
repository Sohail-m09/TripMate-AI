from fastapi import FastAPI

from tripmate.api.routes.trips import (
    router as trips_router,
)
from tripmate.api.routes.users import (
    router as users_router,
)

app = FastAPI(
    title="TripMate AI API",
    description=(
        "Backend API for the TripMate "
        "Agentic AI travel assistant."
    ),
    version="1.0.0",
)

app.include_router(
    trips_router
)

app.include_router(
    users_router
)

@app.get("/")
async def root() -> dict:

    return {
        "message": "TripMate AI API is running."
    }


@app.get("/health")
async def health_check() -> dict:

    return {
        "status": "healthy",
        "service": "tripmate-api",
    }