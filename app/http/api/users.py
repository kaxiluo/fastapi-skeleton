from fastapi import APIRouter, Depends

from app.http import deps
from app.http.deps import get_db
from app.models.user import User
from app.schemas.user import UserDetail

router = APIRouter(
    prefix="/users"
)


@router.get("/me", response_model=UserDetail, dependencies=[Depends(get_db)])
def me(auth_user: User = Depends(deps.get_auth_user)):
    """
    当前登录用户信息
    """
    return auth_user
