from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import Select, and_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.routes.visits import VisitOut, to_visit_out
from app.models.place import Place
from app.models.user import User
from app.models.visit import Visit

router = APIRouter()


class PageOut(BaseModel):
    items: list[VisitOut]
    nextCursor: str | None


@router.get("/visits", response_model=PageOut)
def list_public_visits(
    limit: int = Query(default=20, ge=1, le=100),
    city: str | None = None,
    area: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PageOut:
    stmt: Select[tuple[Visit, User, Place]] = (
        select(Visit, User, Place)
        .join(User, User.id == Visit.author_id)
        .join(Place, Place.id == Visit.place_id)
        .where(and_(Visit.publish_status == "public", Visit.is_deleted.is_(False)))
        .order_by(Visit.created_at.desc())
        .limit(limit)
    )
    if city:
        stmt = stmt.where(Place.city == city)
    if area:
        stmt = stmt.where(Place.area == area)
    if category:
        stmt = stmt.where(Place.category == category)

    rows = db.execute(stmt).all()
    items = [to_visit_out(v, a, p) for v, a, p in rows]
    return PageOut(items=items, nextCursor=None)
