from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mm_api.db.dependencies import get_db_session
from mm_api.db.models.feeding_model import FeedingModel
from mm_api.schema.feeding import FeedingBase


class FeedingDAO:
    """Class for accessing feeding table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_feeding_model(self, feeding: FeedingBase) -> None:
        self.session.add(FeedingModel(**feeding.dict()))

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
