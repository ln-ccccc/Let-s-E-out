from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from sqlalchemy import DateTime, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    reporter_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)

    target_type: Mapped[Literal["visit"]] = mapped_column(String, nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)

    reason: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[Literal["open", "triaged", "resolved", "rejected"]] = mapped_column(
        String, nullable=False, server_default="open"
    )
    handled_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    handled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)

