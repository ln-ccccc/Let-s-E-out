from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from sqlalchemy import DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    phone: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    nickname: Mapped[str] = mapped_column(String, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)

    home_province: Mapped[str | None] = mapped_column(String, nullable=True)
    home_city: Mapped[str | None] = mapped_column(String, nullable=True)
    spice_tolerance: Mapped[int | None] = mapped_column(nullable=True)
    flavor_preference: Mapped[Literal["light", "normal", "heavy"] | None] = mapped_column(
        String, nullable=True
    )
    taste_profile_visibility: Mapped[Literal["public", "private"]] = mapped_column(
        String, nullable=False, server_default="public"
    )

    role: Mapped[Literal["user", "admin"]] = mapped_column(
        String, nullable=False, server_default="user"
    )
    status: Mapped[Literal["active", "banned"]] = mapped_column(
        String, nullable=False, server_default="active"
    )
