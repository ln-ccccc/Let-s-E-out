from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, PrimaryKeyConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (PrimaryKeyConstraint("user_id", "visit_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    visit_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

