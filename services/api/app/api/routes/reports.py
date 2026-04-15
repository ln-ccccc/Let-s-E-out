from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.report import Report
from app.models.user import User
from app.models.visit import Visit

router = APIRouter()


class ReportIn(BaseModel):
    targetType: str = "visit"
    targetId: str
    reason: str
    description: str | None = None


class ReportOut(BaseModel):
    id: str
    status: str


@router.post("", response_model=ReportOut, status_code=201)
def create_report(
    payload: ReportIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ReportOut:
    if payload.targetType != "visit":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="VALIDATION_ERROR")
    try:
        target_id = uuid.UUID(payload.targetId)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="VALIDATION_ERROR")

    visit = db.get(Visit, target_id)
    if visit is None or visit.is_deleted or visit.publish_status != "public":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")

    report = Report(
        reporter_id=user.id,
        target_type="visit",
        target_id=visit.id,
        reason=payload.reason,
        description=payload.description,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return ReportOut(id=str(report.id), status=report.status)

