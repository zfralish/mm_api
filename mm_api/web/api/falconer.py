from fastapi import APIRouter, Depends

from mm_api.db.dao.falconer_dao import FalconerDAO
from mm_api.schema.falconer import FalconerCreate, FalconerRead
from mm_api.web.dependencies import is_authenticated

router = APIRouter(prefix="/falconer")


@router.get("/}")
async def get_falconer(
    falconer_dao: FalconerDAO = Depends(),
    user_id: str = Depends(is_authenticated),
) -> FalconerRead:
    return await falconer_dao.get_by_id(user_id)


@router.post("", status_code=201)
async def create_falconer(
    falconer: FalconerCreate,
    falconer_dao: FalconerDAO = Depends(),
) -> FalconerRead:
    return await falconer_dao.create(falconer)
