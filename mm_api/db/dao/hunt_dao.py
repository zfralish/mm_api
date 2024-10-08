from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Insert

from mm_api.db.dependencies import get_db_session
from mm_api.db.models.hunt_model import HuntModel
from mm_api.schema.hunt import HuntBase, HuntRead


class HuntDAO:
    """Class for accessing hunt table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create(self, bird: HuntBase) -> HuntRead:
        stmt = Insert(HuntModel).values(**bird.dict()).returning(HuntModel)
        result = await self.session.execute(stmt)
        return HuntRead.from_orm(result.scalar())

    async def get_all_hunts(self, limit: int, offset: int) -> List[HuntModel]:
        raw_hunts = await self.session.execute(
            select(HuntModel).limit(limit).offset(offset),
        )

        return list(raw_hunts.scalars().fetchall())

    async def get_by_id(
        self,
        uid: Optional[str] = None,
    ) -> HuntRead:
        query = select(HuntModel)
        if uid:
            query = query.where(HuntModel.id == uid)
        rows = await self.session.execute(query)
        return HuntRead.from_orm(rows.scalar())

    async def filter_by_bird_id_and_time(
        self,
        b_id: Optional[str] = None,
        days: Optional[int] = None,
    ) -> List[HuntRead]:
        query = select(HuntModel)

        conditions = []

        if b_id:
            conditions.append(HuntModel.bird_id == b_id)

        if days:
            start_date = datetime.now() - timedelta(days=days)
            conditions.append(HuntModel.start_time >= start_date)

        if conditions:
            query = query.where(and_(*conditions))

        rows = await self.session.execute(query)
        return [HuntRead.from_orm(row) for row in rows.scalars().fetchall()]

    async def bulk_create(self, hunts: List[HuntBase]) -> None:
        self.session.add_all([HuntModel(**f.dict()) for f in hunts])
        await self.session.commit()
