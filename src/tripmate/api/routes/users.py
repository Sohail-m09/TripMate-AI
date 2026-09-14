from fastapi import (
    APIRouter,
    HTTPException,
)

from tripmate.api.schemas import (
    UserCreateRequest,
    UserResponse,
)
from tripmate.database.user_service import (
    get_user,
    get_user_by_email_address,
    register_user,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
)
async def create_new_user(
    request: UserCreateRequest,
) -> UserResponse:

    try:

        user = await register_user(
            name=request.name,
            email=request.email,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to create user: "
                f"{exc}"
            ),
        ) from exc

    return UserResponse(
        **user
    )

@router.get(
    "/by-email",
    response_model=UserResponse,
)
async def get_user_by_email_endpoint(
    email: str,
) -> UserResponse:

    try:

        user = await get_user_by_email_address(
            email=email
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve user: "
                f"{exc}"
            ),
        ) from exc

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return UserResponse(
        **user
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user_details(
    user_id: int,
) -> UserResponse:

    if user_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="user_id must be greater than 0.",
        )

    try:

        user = await get_user(
            user_id=user_id
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve user: "
                f"{exc}"
            ),
        ) from exc

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return UserResponse(
        **user
    )