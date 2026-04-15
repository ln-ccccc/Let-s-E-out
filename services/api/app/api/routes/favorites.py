from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Select, and_, delete, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_current_user, get_db
from app.api.routes.visits import VisitOut, to_visit_out
from app.models.favorite import Favorite
from app.models.place import Place
from app.models.user import User
from app.models.visit import Visit

router = APIRouter()


class FavoriteIn(BaseModel):
    visitId: str


class FavoriteOut(BaseModel):
    userId: str
    visitId: str
    createdAt: str


class PageOut(BaseModel):
    items: list[VisitOut]
    nextCursor: str | None


@router.post("", response_model=FavoriteOut, status_code=201)
def create_favorite(
    payload: FavoriteIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> FavoriteOut:
    try:
        visit_id = uuid.UUID(payload.visitId)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="VALIDATION_ERROR")

    visit = db.get(Visit, visit_id)
    if visit is None or visit.is_deleted or visit.publish_status != "public":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")

    fav = Favorite(user_id=user.id, visit_id=visit.id)
    db.add(fav)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        fav = db.get(Favorite, {"user_id": user.id, "visit_id": visit.id})
        if fav is None:
            raise
    else:
        db.refresh(fav)
    return FavoriteOut(userId=str(fav.user_id), visitId=str(fav.visit_id), createdAt=fav.created_at.isoformat())


@router.delete("/{visitId}", status_code=204)
def delete_favorite(
    visitId: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    try:
        visit_id = uuid.UUID(visitId)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")

    stmt = delete(Favorite).where(and_(Favorite.user_id == user.id, Favorite.visit_id == visit_id))
    db.execute(stmt)
    db.commit()
    return None


@router.get("", response_model=PageOut)
def list_my_favorites(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PageOut:
    stmt: Select[tuple[Visit, User, Place]] = (
        select(Visit, User, Place)
        .join(Favorite, Favorite.visit_id == Visit.id)
        .join(User, User.id == Visit.author_id)
        .join(Place, Place.id == Visit.place_id)
        .where(and_(Favorite.user_id == user.id, Visit.is_deleted.is_(False)))
        .order_by(Favorite.created_at.desc())
    )
    rows = db.execute(stmt).all()
    items = [to_visit_out(v, a, p) for v, a, p in rows]
    return PageOut(items=items, nextCursor=None)
