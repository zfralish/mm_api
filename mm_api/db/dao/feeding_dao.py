from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Insert

from mm_api.db.dependencies import get_db_session
from mm_api.db.models.feeding_model import FeedingModel
from mm_api.schema.feeding import FeedingBase, FeedingRead


class FeedingDAO:
    """Class for accessing feeding table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create(self, bird: FeedingBase) -> FeedingRead:
        stmt = Insert(FeedingModel).values(**bird.dict()).returning(FeedingModel)
        result = await self.session.execute(stmt)
        return FeedingRead.from_orm(result.scalar())

    async def get_all_feedings(self, limit: int, offset: int) -> List[FeedingModel]:
        raw_feedings = await self.session.execute(
            select(FeedingModel).limit(limit).offset(offset),
        )

        return list(raw_feedings.scalars().fetchall())

    async def filter(
        self,
        uid: Optional[str] = None,
    ) -> List[FeedingModel]:
        query = select(FeedingModel)
        if uid:
            query = query.where(FeedingModel.id == uid)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())

    async def filter_by_bird_id(
        self,
        b_id: Optional[str] = None,
    ) -> List[FeedingRead]:
        query = select(FeedingModel)
        if b_id:
            query = query.where(FeedingModel.bird_id == b_id)
        rows = await self.session.execute(query)
        return [FeedingRead.from_orm(row) for row in rows.scalars().fetchall()]

    async def get_by_id(
        self,
        id: str,
    ) -> FeedingRead:
        query = select(FeedingModel)
        if id:
            query = query.where(FeedingModel.id == id)
        rows = await self.session.execute(query)
        return FeedingRead.from_orm(rows.scalar())

    async def bulk_create(self, feeding: List[FeedingBase]) -> None:
        self.session.add_all([FeedingModel(**f.dict()) for f in feeding])
        await self.session.commit()
