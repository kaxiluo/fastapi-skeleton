from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = User

    async def get_by_username(self, username: str) -> User | None:
        return await self.get_or_none(username=username)

    async def get_by_cellphone(self, cellphone: str) -> User | None:
        return await self.get_or_none(cellphone=cellphone)
