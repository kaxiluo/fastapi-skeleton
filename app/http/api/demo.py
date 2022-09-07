from fastapi import APIRouter

from app.models.user import User

router = APIRouter(
    prefix="/demo"
)


@router.get("/")
async def index():
    return "demo index"


@router.get("/db")
async def db():
    User.create(username='fake_user1')


@router.get("/{demo_id}")
async def show(demo_id: str):
    return {"demo_id": demo_id}
