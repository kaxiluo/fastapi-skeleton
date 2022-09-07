from fastapi import APIRouter
from app.http.api.demo import router as demo_router
from app.http.api.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(demo_router, tags=["demo"])

api_router.include_router(auth_router, tags=["auth"])
