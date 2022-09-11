from fastapi import APIRouter, Depends
from playhouse.shortcuts import model_to_dict

from app.http import deps
from app.models.user import User
from app.schemas.user import UserDetail

router = APIRouter(
    prefix="/users"
)


@router.get("/me", response_model=UserDetail)
def me(auth_user: User = Depends(deps.get_auth_user)):
    return model_to_dict(auth_user)
