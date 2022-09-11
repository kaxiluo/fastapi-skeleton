from fastapi import APIRouter

from app.models.user import User
from app.services.auth import hashing

router = APIRouter(
    prefix="/demo"
)


@router.get("/")
async def index():
    return "demo index"


@router.get("/db_test")
async def db_test():
    password = hashing.get_password_hash("123456")
    user = User.create(username='fake_user_by_db_test_1', password=password)
    return user


@router.get("/{demo_id}")
async def show(demo_id: str):
    return {"demo_id": demo_id}
