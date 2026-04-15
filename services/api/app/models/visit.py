from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Literal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Integer,
    JSON,
    String,
    Uuid,
    false,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    author_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    place_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)

    visited_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    day_part: Mapped[Literal["breakfast", "lunch", "dinner", "late_night", "other"]] = (
        mapped_column(String, nullable=False)
    )
    publish_status: Mapped[Literal["private", "public", "unlisted"]] = mapped_column(
        String, nullable=False, server_default="private"
    )

    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_per_person: Mapped[int | None] = mapped_column(Integer, nullable=True)
    queue_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    highlights: Mapped[str] = mapped_column(String, nullable=False)
    pitfalls: Mapped[str] = mapped_column(String, nullable=False)
    revisit_intent: Mapped[Literal["yes", "maybe", "no"]] = mapped_column(
        String, nullable=False
    )

    recommended_items: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    avoid_items: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    scenarios: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    photo_urls: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=false()
    )
