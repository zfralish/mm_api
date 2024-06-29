from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mm_api.db.dependencies import get_db_session
from mm_api.db.models.hunt_model import HuntModel
from mm_api.schema.hunt import HuntBase


class HuntDAO:
    """Class for accessing hunt table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_hunt_model(self, hunt: HuntBase) -> None:
        self.session.add(HuntModel(**hunt.dict()))

    async def get_all_hunts(self, limit: int, offset: int) -> List[HuntModel]:
        raw_hunts = await self.session.execute(
            select(HuntModel).limit(limit).offset(offset),
        )

        return list(raw_hunts.scalars().fetchall())

    async def filter(
        self,
        uid: Optional[str] = None,
    ) -> List[HuntModel]:
        query = select(HuntModel)
        if uid:
            query = query.where(HuntModel.id == uid)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
