from fastapi import APIRouter
from app.http.api.demo import router as demo_router

api_router = APIRouter()

api_router.include_router(demo_router, tags=["demo"])
