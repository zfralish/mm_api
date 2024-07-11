from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Insert

from mm_api.db.dependencies import get_db_session
from mm_api.db.models.weight_model import WeightModel
from mm_api.schema.feeding import FeedingRead
from mm_api.schema.weight import WeightCreate, WeightRead


class WeightDAO:
    """Class for accessing weight table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create(self, bird: WeightCreate) -> WeightRead:
        stmt = Insert(WeightModel).values(**bird.dict()).returning(WeightModel)
        result = await self.session.execute(stmt)
        return WeightRead.from_orm(result.scalar())

    async def get_all_weights_by_id(self, limit: int, offset: int) -> List[WeightModel]:
        raw_weights = await self.session.execute(
            select(WeightModel).limit(limit).offset(offset),
        )

        return list(raw_weights.scalars().fetchall())

    async def get_by_id(
        self,
        uid: Optional[str] = None,
    ) -> WeightRead:
        query = select(WeightModel)
        if uid:
            query = query.where(WeightModel.id == uid)
        rows = await self.session.execute(query)
        return WeightRead.from_orm(rows.scalar())

    async def filter_by_bird_id(
        self,
        b_id: Optional[str] = None,
    ) -> List[WeightRead]:
        query = select(WeightModel)
        if b_id:
            query = query.where(WeightModel.bird_id == b_id)
        rows = await self.session.execute(query)
        return [WeightRead.from_orm(row) for row in rows.scalars().fetchall()]

    async def bulk_create(self, weight: List[WeightCreate]) -> None:
        self.session.add_all([WeightModel(**w.dict()) for w in weight])
        await self.session.commit()
