from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.core.settings import get_settings


def create_access_token(user_id: uuid.UUID, role: str) -> str:
    settings = get_settings()
    now = datetime.now(tz=UTC)
    exp = now + timedelta(minutes=settings.jwt_expires_minutes)
    payload = {"sub": str(user_id), "role": role, "iat": int(now.timestamp()), "exp": exp}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

