from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.feedback import Feedback
from app.models.user import User

router = APIRouter()


class FeedbackIn(BaseModel):
    type: str
    message: str
    screenshotUrls: list[str] | None = None
    contact: str | None = None
    appVersion: str | None = None
    os: str | None = None
    device: str | None = None


class FeedbackOut(BaseModel):
    id: str
    status: str


@router.post("", response_model=FeedbackOut, status_code=201)
def create_feedback(
    payload: FeedbackIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> FeedbackOut:
    fb = Feedback(
        user_id=user.id,
        type=payload.type,
        message=payload.message,
        screenshot_urls=payload.screenshotUrls,
        contact=payload.contact,
        app_version=payload.appVersion,
        os=payload.os,
        device=payload.device,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return FeedbackOut(id=str(fb.id), status=fb.status)

