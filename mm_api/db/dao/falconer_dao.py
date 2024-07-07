from typing import List, Optional

from fastapi import Depends
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from mm_api.db.dependencies import get_db_session
from mm_api.db.models import FalconerModel
from mm_api.schema.falconer import FalconerCreate, FalconerRead


class FalconerDAO:
    """Class for accessing falconer table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create(self, falconer: FalconerCreate) -> FalconerRead:
        stmt = (
            insert(FalconerModel)
            .values(**falconer.dict())
            .returning(
                FalconerModel,
            )
        )
        result = await self.session.execute(stmt)
        return FalconerRead.from_orm(result.scalar())

    async def get_all(self, limit: int, offset: int) -> List[FalconerRead]:
        raw_falconers = await self.session.execute(
            select(FalconerModel).limit(limit).offset(offset),
        )

        return [
            FalconerRead.from_orm(falconer)
            for falconer in raw_falconers.scalars().fetchall()
        ]

    async def get_by_id(
        self,
        uid: Optional[str] = None,
    ) -> FalconerRead:
        query = select(FalconerModel)
        if uid:
            query = query.where(FalconerModel.id == uid)
        row = await self.session.execute(query)
        return FalconerRead.from_orm(row.scalars().first())
