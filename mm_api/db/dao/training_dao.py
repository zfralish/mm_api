from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mm_api.db.dependencies import get_db_session
from mm_api.db.models.training_model import TrainingModel
from mm_api.schema.training import TrainingBase


class TrainingDAO:
    """Class for accessing training table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_training_model(self, training: TrainingBase) -> None:
        self.session.add(TrainingModel(**training.dict()))

    async def get_all_trainings(self, limit: int, offset: int) -> List[TrainingModel]:
        raw_trainings = await self.session.execute(
            select(TrainingModel).limit(limit).offset(offset),
        )

        return list(raw_trainings.scalars().fetchall())

    async def filter(
        self,
        uid: Optional[str] = None,
    ) -> List[TrainingModel]:
        query = select(TrainingModel)
        if uid:
            query = query.where(TrainingModel.id == uid)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
