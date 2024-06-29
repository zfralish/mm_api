from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mm_api.db.dependencies import get_db_session
from mm_api.db.models.bird_model import BirdModel
from mm_api.schema.bird import BirdCreate


class BirdDAO:
    """Class for accessing bird table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_bird_model(self, bird: BirdCreate) -> None:
        self.session.add(BirdModel(**bird.dict()))

    async def get_all_birds(self, limit: int, offset: int) -> List[BirdModel]:
        raw_birds = await self.session.execute(
            select(BirdModel).limit(limit).offset(offset),
        )

        return list(raw_birds.scalars().fetchall())

    async def filter(
        self,
        falconer_id: Optional[str] = None,
    ) -> List[BirdModel]:
        query = select(BirdModel)
        if falconer_id:
            query = query.where(BirdModel.falconer_id == falconer_id)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
