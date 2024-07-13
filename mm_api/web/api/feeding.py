from typing import List

from fastapi import APIRouter, Depends

from mm_api.db.dao.feeding_dao import FeedingDAO
from mm_api.schema.feeding import FeedingBase, FeedingRead
from mm_api.web.dependencies import is_authenticated

router = APIRouter(prefix="/feeding")


@router.get("/{feeding_id}")
async def get_feeding(
    feeding_id: str,
    feeding_dao: FeedingDAO = Depends(),
) -> FeedingRead:
    return await feeding_dao.get_by_id(feeding_id)


@router.post("", status_code=201)
async def create_feeding(
    feeding: FeedingBase,
    feeding_dao: FeedingDAO = Depends(),
) -> FeedingRead:
    return await feeding_dao.create(feeding)


@router.post("/bulk", status_code=201)
async def create_bulk_feeding(
    feedings: List[FeedingBase],
    feeding_dao: FeedingDAO = Depends(),
) -> None:
    return await feeding_dao.bulk_create(feedings)


@router.get("/{bird_id}/filter-date")
async def filter_feeding_by_date(
    days: int,
    bird_id: str,
    feeding_dao: FeedingDAO = Depends(),
) -> List[FeedingRead]:
    return await feeding_dao.filter_by_bird_id_and_time(bird_id, days)
