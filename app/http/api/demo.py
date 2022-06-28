import logging

from fastapi import APIRouter

router = APIRouter(
    prefix="/demo"
)


@router.get("/")
async def index():
    return "demo index"


@router.get("/{demo_id}")
async def show(demo_id: str):
    logging.info("demo id is " + demo_id)
    return {"demo_id": demo_id}
