from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from tripmate.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    trips: Mapped[list["Trip"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    user_query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    origin: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    destination: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    budget: Mapped[Decimal | None] = mapped_column(
        Numeric(
            precision=12,
            scale=2,
        ),
        nullable=True,
    )

    adults: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    children: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    itinerary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    final_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="trips",
    )