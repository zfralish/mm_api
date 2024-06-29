from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mm_api.db.dependencies import get_db_session
from mm_api.db.models.falconer_model import FalconerModel
from mm_api.schema.falconer import FalconerCreate


class FalconerDAO:
    """Class for accessing falconer table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_falconer_model(self, falconer: FalconerCreate) -> None:
        self.session.add(FalconerModel(**falconer.dict()))

    async def get_all_falconers(self, limit: int, offset: int) -> List[FalconerModel]:
        raw_falconers = await self.session.execute(
            select(FalconerModel).limit(limit).offset(offset),
        )

        return list(raw_falconers.scalars().fetchall())

    async def filter(
        self,
        uid: Optional[str] = None,
    ) -> List[FalconerModel]:
        query = select(FalconerModel)
        if uid:
            query = query.where(FalconerModel.id == uid)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
