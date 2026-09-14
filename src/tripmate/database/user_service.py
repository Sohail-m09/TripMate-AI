from tripmate.database.connection import (
    AsyncSessionLocal,
)
from tripmate.database.repositories import (
    create_user,
    get_user_by_email,
    get_user_by_id,
)


async def register_user(
    name: str,
    email: str,
) -> dict:

    async with AsyncSessionLocal() as session:

        existing_user = await get_user_by_email(
            session=session,
            email=email,
        )

        if existing_user is not None:
            raise ValueError(
                "A user with this email already exists."
            )

        user = await create_user(
            session=session,
            name=name,
            email=email,
        )

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": (
                user.created_at.isoformat()
                if user.created_at
                else None
            ),
        }


async def get_user(
    user_id: int,
) -> dict | None:

    async with AsyncSessionLocal() as session:

        user = await get_user_by_id(
            session=session,
            user_id=user_id,
        )

        if user is None:
            return None

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": (
                user.created_at.isoformat()
                if user.created_at
                else None
            ),
        }

async def get_user_by_email_address(
    email: str,
) -> dict | None:

    async with AsyncSessionLocal() as session:

        user = await get_user_by_email(
            session=session,
            email=email,
        )

        if user is None:
            return None

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": (
                user.created_at.isoformat()
                if user.created_at
                else None
            ),
        }