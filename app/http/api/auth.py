import logging

from fastapi import APIRouter

router = APIRouter(
    prefix="/auth"
)


@router.post("/token")
async def token():
    return "token"
