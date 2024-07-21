from typing import List

from fastapi import APIRouter, Depends

from mm_api.db.dao.weight_dao import WeightDAO
from mm_api.schema.weight import WeightCreate, WeightRead
from mm_api.web.dependencies import is_authenticated

router = APIRouter(prefix="/weight")


@router.get("/{weight_id}")
async def get_weight(
    weight_id: str,
    weight_dao: WeightDAO = Depends(),
) -> WeightRead:
    return await weight_dao.get_by_id(weight_id)


@router.post("", status_code=201)
async def create_weight(
    weight: WeightCreate,
    weight_dao: WeightDAO = Depends(),
) -> WeightRead:
    return await weight_dao.create(weight)


@router.post("/bulk", status_code=201)
async def create_bulk_weight(
    weights: List[WeightCreate],
    weight_dao: WeightDAO = Depends(),
) -> None:
    return await weight_dao.bulk_create(weights)


@router.get("/{bird_id}/filter-date")
async def filter_weight_by_date(
    bird_id: str,
    days: int = 30,
    weight_dao: WeightDAO = Depends(),
) -> List[WeightRead]:
    weights = await weight_dao.filter_by_bird_id_and_time(bird_id, days)
    print(len(weights))
    return weights
