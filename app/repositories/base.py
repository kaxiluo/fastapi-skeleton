from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base


class BaseRepository:
    model: type[Base]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, pk: int):
        return await self.session.get(self.model, pk)

    async def get_or_none(self, **kwargs):
        stmt = select(self.model).where(*(getattr(self.model, k) == v for k, v in kwargs.items()))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, **kwargs):
        stmt = select(self.model)
        if kwargs:
            stmt = stmt.where(*(getattr(self.model, k) == v for k, v in kwargs.items()))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **kwargs):
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj, **kwargs):
        for key, value in kwargs.items():
            setattr(obj, key, value)
        await self.session.flush()
        # refresh 回填 server 端字段（如 updated_at 的 ON UPDATE）
        await self.session.refresh(obj)
        return obj
