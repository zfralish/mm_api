from fastapi import APIRouter, Depends

from mm_api.db.dao.falconer_dao import FalconerDAO
from mm_api.schema.falconer import FalconerCreate, FalconerRead

router = APIRouter(prefix="/falconer")


@router.get("/{falconer_id}")
async def get_falconer(
    falconer_id: str,
    falconer_dao: FalconerDAO = Depends(),
) -> FalconerRead:
    return await falconer_dao.get_by_id(falconer_id)


@router.post("", status_code=201)
async def create_falconer(
    falconer: FalconerCreate,
    falconer_dao: FalconerDAO = Depends(),
) -> FalconerRead:
    return await falconer_dao.create(falconer)
