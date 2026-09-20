from fastapi import APIRouter

from app.http.api import auth, demo, health, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(demo.router, tags=["demo"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, tags=["users"])
