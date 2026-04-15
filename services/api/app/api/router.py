from fastapi import APIRouter

from app.api.routes import admin, auth, feedbacks, favorites, me, places, public, reports, visits

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(me.router, tags=["me"])
api_router.include_router(places.router, prefix="/places", tags=["places"])
api_router.include_router(visits.router, prefix="/visits", tags=["visits"])
api_router.include_router(public.router, prefix="/public", tags=["public"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(feedbacks.router, prefix="/feedbacks", tags=["feedbacks"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

