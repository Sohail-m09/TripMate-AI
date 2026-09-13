import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from tripmate.config import DATABASE_URL


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():

    async with AsyncSessionLocal() as session:
        yield session


async def test_database_connection() -> None:

    async with engine.connect() as connection:

        await connection.execute(
            text("SELECT 1")
        )

        print(
            "PostgreSQL connection successful."
        )


async def main() -> None:

    await test_database_connection()

    await engine.dispose()


if __name__ == "__main__":

    asyncio.run(main())