from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import Select, and_, select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.models.feedback import Feedback
from app.models.report import Report
from app.models.user import User

router = APIRouter()


class ReportItem(BaseModel):
    id: str
    createdAt: str
    reporterId: str
    targetType: str
    targetId: str
    reason: str
    description: str | None
    status: str
    handledBy: str | None
    handledAt: str | None
    resolution: str | None


class FeedbackItem(BaseModel):
    id: str
    createdAt: str
    userId: str | None
    type: str
    message: str
    status: str
    handledBy: str | None
    handledAt: str | None
    reply: str | None


class PageOut(BaseModel):
    items: list
    nextCursor: str | None


class ReportPatchIn(BaseModel):
    status: str | None = None
    resolution: str | None = None


class FeedbackPatchIn(BaseModel):
    status: str | None = None
    reply: str | None = None


@router.get("/reports", response_model=PageOut)
def list_reports(
    status_: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> PageOut:
    stmt: Select[tuple[Report]] = select(Report).order_by(Report.created_at.desc()).limit(limit)
    if status_:
        stmt = stmt.where(Report.status == status_)
    items = [
        ReportItem(
            id=str(r.id),
            createdAt=r.created_at.isoformat(),
            reporterId=str(r.reporter_id),
            targetType=r.target_type,
            targetId=str(r.target_id),
            reason=r.reason,
            description=r.description,
            status=r.status,
            handledBy=str(r.handled_by) if r.handled_by else None,
            handledAt=r.handled_at.isoformat() if r.handled_at else None,
            resolution=r.resolution,
        )
        for r in db.scalars(stmt).all()
    ]
    return PageOut(items=items, nextCursor=None)


@router.patch("/reports/{reportId}", response_model=ReportItem)
def patch_report(
    reportId: str,
    payload: ReportPatchIn,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> ReportItem:
    try:
        report_id = uuid.UUID(reportId)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")

    report = db.get(Report, report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")

    if payload.status is not None:
        report.status = payload.status
    if payload.resolution is not None:
        report.resolution = payload.resolution
    report.handled_by = admin.id
    report.handled_at = datetime.now(tz=UTC)

    db.add(report)
    db.commit()
    db.refresh(report)
    return ReportItem(
        id=str(report.id),
        createdAt=report.created_at.isoformat(),
        reporterId=str(report.reporter_id),
        targetType=report.target_type,
        targetId=str(report.target_id),
        reason=report.reason,
        description=report.description,
        status=report.status,
        handledBy=str(report.handled_by) if report.handled_by else None,
        handledAt=report.handled_at.isoformat() if report.handled_at else None,
        resolution=report.resolution,
    )


@router.get("/feedbacks", response_model=PageOut)
def list_feedbacks(
    status_: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> PageOut:
    stmt: Select[tuple[Feedback]] = select(Feedback).order_by(Feedback.created_at.desc()).limit(limit)
    if status_:
        stmt = stmt.where(Feedback.status == status_)
    items = [
        FeedbackItem(
            id=str(f.id),
            createdAt=f.created_at.isoformat(),
            userId=str(f.user_id) if f.user_id else None,
            type=f.type,
            message=f.message,
            status=f.status,
            handledBy=str(f.handled_by) if f.handled_by else None,
            handledAt=f.handled_at.isoformat() if f.handled_at else None,
            reply=f.reply,
        )
        for f in db.scalars(stmt).all()
    ]
    return PageOut(items=items, nextCursor=None)


@router.patch("/feedbacks/{feedbackId}", response_model=FeedbackItem)
def patch_feedback(
    feedbackId: str,
    payload: FeedbackPatchIn,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> FeedbackItem:
    try:
        feedback_id = uuid.UUID(feedbackId)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")

    fb = db.get(Feedback, feedback_id)
    if fb is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")

    if payload.status is not None:
        fb.status = payload.status
    if payload.reply is not None:
        fb.reply = payload.reply
    fb.handled_by = admin.id
    fb.handled_at = datetime.now(tz=UTC)

    db.add(fb)
    db.commit()
    db.refresh(fb)
    return FeedbackItem(
        id=str(fb.id),
        createdAt=fb.created_at.isoformat(),
        userId=str(fb.user_id) if fb.user_id else None,
        type=fb.type,
        message=fb.message,
        status=fb.status,
        handledBy=str(fb.handled_by) if fb.handled_by else None,
        handledAt=fb.handled_at.isoformat() if fb.handled_at else None,
        reply=fb.reply,
    )

