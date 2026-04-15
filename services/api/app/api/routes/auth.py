from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.settings import get_settings
from app.models.auth_otp import AuthOtp
from app.models.user import User
from app.security.tokens import create_access_token

router = APIRouter()


class RequestOtpIn(BaseModel):
    phone: str = Field(min_length=6, max_length=32)


class RequestOtpOut(BaseModel):
    ok: bool
    expiresIn: int


class VerifyOtpIn(BaseModel):
    phone: str = Field(min_length=6, max_length=32)
    code: str = Field(min_length=4, max_length=8)


class VerifyOtpOut(BaseModel):
    accessToken: str


@router.post("/request-otp", response_model=RequestOtpOut)
def request_otp(payload: RequestOtpIn, db: Session = Depends(get_db)) -> RequestOtpOut:
    now = datetime.now(tz=UTC)
    expires_at = now + timedelta(minutes=5)
    otp = AuthOtp(phone=payload.phone, expires_at=expires_at)
    db.add(otp)
    db.commit()
    return RequestOtpOut(ok=True, expiresIn=300)


@router.post("/verify-otp", response_model=VerifyOtpOut)
def verify_otp(payload: VerifyOtpIn, db: Session = Depends(get_db)) -> VerifyOtpOut:
    settings = get_settings()
    if settings.env != "development":
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="NOT_IMPLEMENTED")

    if payload.code != "000000":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="INVALID_CODE")

    user = db.scalar(select(User).where(User.phone == payload.phone))
    if user is None:
        user = User(phone=payload.phone, nickname="新用户")
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id, user.role)
    return VerifyOtpOut(accessToken=token)

