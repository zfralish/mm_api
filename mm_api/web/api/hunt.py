from typing import List

from fastapi import APIRouter, Depends

from mm_api.db.dao.hunt_dao import HuntDAO
from mm_api.schema.hunt import HuntBase, HuntRead
from mm_api.web.dependencies import is_authenticated

router = APIRouter(prefix="/hunt")


@router.get("/{hunt_id}")
async def get_hunt(
    hunt_id: str,
    hunt_dao: HuntDAO = Depends(),
) -> HuntRead:
    return await hunt_dao.get_by_id(hunt_id)


@router.post("", status_code=201)
async def create_hunt(
    hunt: HuntBase,
    hunt_dao: HuntDAO = Depends(),
) -> HuntRead:
    return await hunt_dao.create(hunt)


@router.post("/bulk", status_code=201)
async def create_bulk_hunt(
    hunts: List[HuntBase],
    hunt_dao: HuntDAO = Depends(),
) -> None:
    return await hunt_dao.bulk_create(hunts)


@router.get("/{bird_id}/filter-date")
async def filter_hunt_by_date(
    days: int,
    bird_id: str,
    hunt_dao: HuntDAO = Depends(),
) -> List[HuntRead]:
    return await hunt_dao.filter_by_bird_id_and_time(bird_id, days)
