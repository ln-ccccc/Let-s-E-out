from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from sqlalchemy import DateTime, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)

    type: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    screenshot_urls: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    contact: Mapped[str | None] = mapped_column(String, nullable=True)

    app_version: Mapped[str | None] = mapped_column(String, nullable=True)
    os: Mapped[str | None] = mapped_column(String, nullable=True)
    device: Mapped[str | None] = mapped_column(String, nullable=True)

    status: Mapped[Literal["received", "in_progress", "done"]] = mapped_column(
        String, nullable=False, server_default="received"
    )
    handled_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    handled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reply: Mapped[str | None] = mapped_column(Text, nullable=True)

