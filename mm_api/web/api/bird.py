from typing import List

from fastapi import APIRouter, Depends

from mm_api.db.dao.bird_dao import BirdDAO
from mm_api.schema.bird import BirdCreate, BirdRead

router = APIRouter(prefix="/bird")


@router.get("/{bird_id}")
async def get_bird(bird_id: str, bird_dao: BirdDAO = Depends()) -> BirdRead:
    return await bird_dao.get_by_id(bird_id)


@router.post("", status_code=201)
async def create_bird(bird: BirdCreate, bird_dao: BirdDAO = Depends()) -> BirdRead:
    return await bird_dao.create(bird)


@router.get("/falconer/{falconer_id}")
async def get_birds_by_falconer_id(
    falconer_id: str,
    bird_dao: BirdDAO = Depends(),
) -> List[BirdRead]:
    return await bird_dao.get_by_falconer_id(falconer_id)
