from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Insert

from mm_api.db.dependencies import get_db_session
from mm_api.db.models.training_model import TrainingModel
from mm_api.schema.training import TrainingBase, TrainingRead


class TrainingDAO:
    """Class for accessing training table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create(self, bird: TrainingBase) -> TrainingRead:
        stmt = Insert(TrainingModel).values(**bird.dict()).returning(TrainingModel)
        result = await self.session.execute(stmt)
        return TrainingRead.from_orm(result.scalar())

    async def get_all_trainings(self, limit: int, offset: int) -> List[TrainingModel]:
        raw_trainings = await self.session.execute(
            select(TrainingModel).limit(limit).offset(offset),
        )

        return list(raw_trainings.scalars().fetchall())

    async def get_by_id(
        self,
        uid: Optional[str] = None,
    ) -> TrainingRead:
        query = select(TrainingModel)
        if uid:
            query = query.where(TrainingModel.id == uid)
        rows = await self.session.execute(query)
        return TrainingRead.from_orm(rows.scalar())

    async def filter_by_bird_id(
        self,
        b_id: Optional[str] = None,
    ) -> List[TrainingRead]:
        query = select(TrainingModel)
        if b_id:
            query = query.where(TrainingModel.bird_id == b_id)
        rows = await self.session.execute(query)
        return [TrainingRead.from_orm(row) for row in rows.scalars().fetchall()]

    async def bulk_create(self, trainings: List[TrainingBase]) -> None:
        self.session.add_all([TrainingModel(**f.dict()) for f in trainings])
        await self.session.commit()
