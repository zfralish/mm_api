from typing import List, Optional

from fastapi import Depends
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from mm_api.db.dependencies import get_db_session
from mm_api.db.models.bird_model import BirdModel
from mm_api.schema.bird import BirdCreate, BirdRead


class BirdDAO:
    """Class for accessing bird table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create(self, bird: BirdCreate) -> BirdRead:
        stmt = insert(BirdModel).values(**bird.dict()).returning(BirdModel)
        result = await self.session.execute(stmt)
        return BirdRead.from_orm(result.scalar())

    async def get_all(self, limit: int, offset: int) -> List[BirdRead]:
        raw_birds = await self.session.execute(
            select(BirdModel).limit(limit).offset(offset),
        )

        return [BirdRead.from_orm(bird) for bird in raw_birds.scalars().fetchall()]

    async def get_by_id(
        self,
        uid: Optional[str] = None,
    ) -> BirdRead:
        query = select(BirdModel)
        if uid:
            query = query.where(BirdModel.id == uid)
        row = await self.session.execute(query)
        return BirdRead.from_orm(row.scalar())

    async def get_by_falconer_id(
        self,
        falconer_id: str,
    ) -> List[BirdRead]:
        raw_birds = await self.session.execute(
            select(BirdModel).where(BirdModel.falconer_id == falconer_id),
        )
        return [BirdRead.from_orm(bird) for bird in raw_birds.scalars().fetchall()]
