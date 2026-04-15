from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User

router = APIRouter()


class TasteProfile(BaseModel):
    model_config = {"populate_by_name": True}

    homeProvince: str | None = Field(default=None, alias="home_province")
    homeCity: str | None = Field(default=None, alias="home_city")
    spiceTolerance: int | None = Field(default=None, alias="spice_tolerance")
    flavorPreference: str | None = Field(default=None, alias="flavor_preference")
    visibility: str = Field(alias="taste_profile_visibility")


class MeOut(BaseModel):
    model_config = {"populate_by_name": True}

    id: str
    nickname: str
    avatarUrl: str | None = Field(default=None, alias="avatar_url")
    tasteProfile: TasteProfile
    role: str


class TasteProfileIn(BaseModel):
    homeProvince: str | None = None
    homeCity: str | None = None
    spiceTolerance: int | None = None
    flavorPreference: str | None = None
    visibility: str | None = None


class MePatchIn(BaseModel):
    nickname: str | None = None
    avatarUrl: str | None = None
    tasteProfile: TasteProfileIn | None = None


def to_me_out(user: User) -> MeOut:
    return MeOut(
        id=str(user.id),
        nickname=user.nickname,
        avatar_url=user.avatar_url,
        tasteProfile=TasteProfile(
            home_province=user.home_province,
            home_city=user.home_city,
            spice_tolerance=user.spice_tolerance,
            flavor_preference=user.flavor_preference,
            taste_profile_visibility=user.taste_profile_visibility,
        ),
        role=user.role,
    )


@router.get("/me", response_model=MeOut)
def get_me(user: User = Depends(get_current_user)) -> MeOut:
    return to_me_out(user)


@router.patch("/me", response_model=MeOut)
def patch_me(
    payload: MePatchIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MeOut:
    if payload.nickname is not None:
        user.nickname = payload.nickname
    if payload.avatarUrl is not None:
        user.avatar_url = payload.avatarUrl
    if payload.tasteProfile is not None:
        tp = payload.tasteProfile
        if tp.homeProvince is not None:
            user.home_province = tp.homeProvince
        if tp.homeCity is not None:
            user.home_city = tp.homeCity
        if tp.spiceTolerance is not None:
            user.spice_tolerance = tp.spiceTolerance
        if tp.flavorPreference is not None:
            user.flavor_preference = tp.flavorPreference
        if tp.visibility is not None:
            user.taste_profile_visibility = tp.visibility

    db.add(user)
    db.commit()
    db.refresh(user)
    return to_me_out(user)

