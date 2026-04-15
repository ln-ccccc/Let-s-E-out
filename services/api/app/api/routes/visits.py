from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import Select, and_, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.place import Place
from app.models.user import User
from app.models.visit import Visit

router = APIRouter()


class TasteProfileOut(BaseModel):
    homeProvince: str | None
    homeCity: str | None
    spiceTolerance: int | None
    flavorPreference: str | None
    visibility: str


class AuthorOut(BaseModel):
    id: str
    nickname: str
    avatarUrl: str | None
    tasteProfile: TasteProfileOut


class PlaceBriefOut(BaseModel):
    id: str
    name: str
    city: str
    area: str | None


class VisitOut(BaseModel):
    id: str
    authorId: str
    author: AuthorOut
    place: PlaceBriefOut
    createdAt: str
    updatedAt: str
    visitedOn: date | None
    dayPart: str
    publishStatus: str
    highlights: str
    pitfalls: str
    revisitIntent: str
    recommendedItems: list[str] = Field(default_factory=list)
    avoidItems: list[str] = Field(default_factory=list)
    scenarios: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    photoUrls: list[str] = Field(default_factory=list)
    rating: int | None = None
    pricePerPerson: int | None = None
    queueMinutes: int | None = None


class PageOut(BaseModel):
    items: list[VisitOut]
    nextCursor: str | None


class VisitCreateIn(BaseModel):
    placeId: str
    visitedOn: date | None = None
    dayPart: str
    publishStatus: str = "private"
    rating: int | None = None
    pricePerPerson: int | None = None
    queueMinutes: int | None = None
    highlights: str
    pitfalls: str
    revisitIntent: str
    recommendedItems: list[str] | None = None
    avoidItems: list[str] | None = None
    scenarios: list[str] | None = None
    tags: list[str] | None = None
    photoUrls: list[str] | None = None


class VisitPatchIn(BaseModel):
    visitedOn: date | None = None
    dayPart: str | None = None
    publishStatus: str | None = None
    rating: int | None = None
    pricePerPerson: int | None = None
    queueMinutes: int | None = None
    highlights: str | None = None
    pitfalls: str | None = None
    revisitIntent: str | None = None
    recommendedItems: list[str] | None = None
    avoidItems: list[str] | None = None
    scenarios: list[str] | None = None
    tags: list[str] | None = None
    photoUrls: list[str] | None = None


def to_visit_out(visit: Visit, author: User, place: Place) -> VisitOut:
    return VisitOut(
        id=str(visit.id),
        authorId=str(visit.author_id),
        author=AuthorOut(
            id=str(author.id),
            nickname=author.nickname,
            avatarUrl=author.avatar_url,
            tasteProfile=TasteProfileOut(
                homeProvince=author.home_province,
                homeCity=author.home_city,
                spiceTolerance=author.spice_tolerance,
                flavorPreference=author.flavor_preference,
                visibility=author.taste_profile_visibility,
            ),
        ),
        place=PlaceBriefOut(
            id=str(place.id),
            name=place.name,
            city=place.city,
            area=place.area,
        ),
        createdAt=visit.created_at.isoformat(),
        updatedAt=visit.updated_at.isoformat(),
        visitedOn=visit.visited_on,
        dayPart=visit.day_part,
        publishStatus=visit.publish_status,
        highlights=visit.highlights,
        pitfalls=visit.pitfalls,
        revisitIntent=visit.revisit_intent,
        recommendedItems=visit.recommended_items or [],
        avoidItems=visit.avoid_items or [],
        scenarios=visit.scenarios or [],
        tags=visit.tags or [],
        photoUrls=visit.photo_urls or [],
        rating=visit.rating,
        pricePerPerson=visit.price_per_person,
        queueMinutes=visit.queue_minutes,
    )


@router.post("", response_model=VisitOut, status_code=201)
def create_visit(
    payload: VisitCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> VisitOut:
    try:
        place_id = uuid.UUID(payload.placeId)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="VALIDATION_ERROR")

    place = db.get(Place, place_id)
    if place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")

    visit = Visit(
        author_id=user.id,
        place_id=place.id,
        visited_on=payload.visitedOn,
        day_part=payload.dayPart,
        publish_status=payload.publishStatus,
        rating=payload.rating,
        price_per_person=payload.pricePerPerson,
        queue_minutes=payload.queueMinutes,
        highlights=payload.highlights,
        pitfalls=payload.pitfalls,
        revisit_intent=payload.revisitIntent,
        recommended_items=payload.recommendedItems,
        avoid_items=payload.avoidItems,
        scenarios=payload.scenarios,
        tags=payload.tags,
        photo_urls=payload.photoUrls,
    )
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return to_visit_out(visit, user, place)


@router.get("/mine", response_model=PageOut)
def list_my_visits(
    q: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    city: str | None = None,
    area: str | None = None,
    category: str | None = None,
    publishStatus: str | None = None,
    revisitIntent: str | None = None,
    dayPart: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PageOut:
    stmt: Select[tuple[Visit, Place]] = (
        select(Visit, Place)
        .join(Place, Place.id == Visit.place_id)
        .where(and_(Visit.author_id == user.id, Visit.is_deleted.is_(False)))
        .order_by(Visit.created_at.desc())
        .limit(limit)
    )
    if q:
        stmt = stmt.where(Place.name.ilike(f"%{q}%"))
    if city:
        stmt = stmt.where(Place.city == city)
    if area:
        stmt = stmt.where(Place.area == area)
    if category:
        stmt = stmt.where(Place.category == category)
    if publishStatus:
        stmt = stmt.where(Visit.publish_status == publishStatus)
    if revisitIntent:
        stmt = stmt.where(Visit.revisit_intent == revisitIntent)
    if dayPart:
        stmt = stmt.where(Visit.day_part == dayPart)

    rows = db.execute(stmt).all()
    author = user
    items = [to_visit_out(v, author, p) for v, p in rows]
    return PageOut(items=items, nextCursor=None)


def _load_visit(
    visit_id: uuid.UUID, db: Session, viewer: User
) -> tuple[Visit, User, Place]:
    stmt = (
        select(Visit, User, Place)
        .join(User, User.id == Visit.author_id)
        .join(Place, Place.id == Visit.place_id)
        .where(and_(Visit.id == visit_id, Visit.is_deleted.is_(False)))
    )
    row = db.execute(stmt).one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")

    visit, author, place = row
    if visit.publish_status != "public" and visit.author_id != viewer.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    return visit, author, place


@router.get("/{visitId}", response_model=VisitOut)
def get_visit(
    visitId: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> VisitOut:
    try:
        visit_id = uuid.UUID(visitId)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
    visit, author, place = _load_visit(visit_id, db, user)
    return to_visit_out(visit, author, place)


@router.patch("/{visitId}", response_model=VisitOut)
def patch_visit(
    visitId: str,
    payload: VisitPatchIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> VisitOut:
    try:
        visit_id = uuid.UUID(visitId)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")

    visit = db.get(Visit, visit_id)
    if visit is None or visit.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
    if visit.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")

    if payload.visitedOn is not None:
        visit.visited_on = payload.visitedOn
    if payload.dayPart is not None:
        visit.day_part = payload.dayPart
    if payload.publishStatus is not None:
        visit.publish_status = payload.publishStatus
    if payload.rating is not None:
        visit.rating = payload.rating
    if payload.pricePerPerson is not None:
        visit.price_per_person = payload.pricePerPerson
    if payload.queueMinutes is not None:
        visit.queue_minutes = payload.queueMinutes
    if payload.highlights is not None:
        visit.highlights = payload.highlights
    if payload.pitfalls is not None:
        visit.pitfalls = payload.pitfalls
    if payload.revisitIntent is not None:
        visit.revisit_intent = payload.revisitIntent
    if payload.recommendedItems is not None:
        visit.recommended_items = payload.recommendedItems
    if payload.avoidItems is not None:
        visit.avoid_items = payload.avoidItems
    if payload.scenarios is not None:
        visit.scenarios = payload.scenarios
    if payload.tags is not None:
        visit.tags = payload.tags
    if payload.photoUrls is not None:
        visit.photo_urls = payload.photoUrls

    db.add(visit)
    db.commit()

    author = user
    place = db.get(Place, visit.place_id)
    if place is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL_ERROR")

    db.refresh(visit)
    return to_visit_out(visit, author, place)


@router.delete("/{visitId}", status_code=204)
def delete_visit(
    visitId: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    try:
        visit_id = uuid.UUID(visitId)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")

    visit = db.get(Visit, visit_id)
    if visit is None or visit.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
    if visit.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")

    visit.is_deleted = True
    db.add(visit)
    db.commit()
    return None

