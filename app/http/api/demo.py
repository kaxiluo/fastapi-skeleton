import logging

from fastapi import APIRouter

from app.models import models
from app.providers import database

router = APIRouter(
    prefix="/demo"
)


@router.get("/")
async def index():
    return "demo index"


@router.get("/db")
async def db():
    database.db.create_tables([models.User])
    models.User.create(username='fastapi', email='fastapi@fastapi.com')
    models.User.create(username='kaxiluo', email='kaxiluo@kaxiluo.com')
    return "demo db"


@router.get("/db_query")
async def db_query():
    users = models.User.select()
    return list(users)


@router.get("/{demo_id}")
async def show(demo_id: str):
    logging.info("demo id is " + demo_id)
    return {"demo_id": demo_id}
