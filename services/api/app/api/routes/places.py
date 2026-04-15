from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.place import Place
from app.models.user import User

router = APIRouter()


class PlaceOut(BaseModel):
    id: str
    name: str
    city: str
    area: str | None
    address: str | None
    category: str | None


class PageOut(BaseModel):
    items: list[PlaceOut]
    nextCursor: str | None


class PlaceCreateIn(BaseModel):
    name: str
    city: str
    area: str | None = None
    address: str | None = None
    category: str | None = None


def to_place_out(place: Place) -> PlaceOut:
    return PlaceOut(
        id=str(place.id),
        name=place.name,
        city=place.city,
        area=place.area,
        address=place.address,
        category=place.category,
    )


@router.get("/search", response_model=PageOut)
def search_places(
    q: str = Query(min_length=1),
    city: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PageOut:
    stmt: Select[tuple[Place]] = select(Place)
    if city is not None:
        stmt = stmt.where(Place.city == city)
    stmt = stmt.where(Place.name.ilike(f"%{q}%")).order_by(Place.created_at.desc()).limit(limit)
    items = [to_place_out(p) for p in db.scalars(stmt).all()]
    return PageOut(items=items, nextCursor=None)


@router.post("", response_model=PlaceOut, status_code=201)
def create_place(
    payload: PlaceCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PlaceOut:
    place = Place(
        created_by=user.id,
        name=payload.name,
        city=payload.city,
        area=payload.area,
        address=payload.address,
        category=payload.category,
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    return to_place_out(place)

