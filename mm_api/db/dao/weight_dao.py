from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mm_api.db.dependencies import get_db_session
from mm_api.db.models.weight_model import WeightModel
from mm_api.schema.weight import WeightCreate


class WeightDAO:
    """Class for accessing weight table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_weight_model(self, weight: WeightCreate) -> None:
        self.session.add(WeightModel(**weight.dict()))

    async def get_all_weights(self, limit: int, offset: int) -> List[WeightModel]:
        raw_weights = await self.session.execute(
            select(WeightModel).limit(limit).offset(offset),
        )

        return list(raw_weights.scalars().fetchall())

    async def filter(
        self,
        uid: Optional[str] = None,
    ) -> List[WeightModel]:
        query = select(WeightModel)
        if uid:
            query = query.where(WeightModel.id == uid)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
