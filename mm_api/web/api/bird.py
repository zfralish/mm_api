from typing import List

from fastapi import APIRouter, Depends

from mm_api.db.dao import bird_dao
from mm_api.db.dao.bird_dao import BirdDAO
from mm_api.db.dao.feeding_dao import FeedingDAO
from mm_api.db.dao.hunt_dao import HuntDAO
from mm_api.db.dao.training_dao import TrainingDAO
from mm_api.db.dao.weight_dao import WeightDAO
from mm_api.schema.bird import BirdCreate, BirdNestedChildren, BirdRead
from mm_api.web.dependencies import is_authenticated

router = APIRouter(prefix="/bird")


@router.get("/{bird_id}")
async def get_bird(bird_id: str, bird_dao: BirdDAO = Depends()) -> BirdRead:
    return await bird_dao.get_by_id(bird_id)


@router.post("", status_code=201)
async def create_bird(bird: BirdCreate, bird_dao: BirdDAO = Depends()) -> BirdRead:
    return await bird_dao.create(bird)


@router.get("")
async def get_birds_by_falconer_id(
    user_id: str = Depends(is_authenticated),
    bird_dao: BirdDAO = Depends(),
) -> List[BirdRead]:
    return await bird_dao.get_by_falconer_id(user_id)


@router.get("/{bird_id}/dashboard")
async def get_dashboard_info(
    bird_id: str,
    user_id: str = Depends(is_authenticated),
    bird_dao: BirdDAO = Depends(),
    weight_dao: WeightDAO = Depends(),
    training_dao: TrainingDAO = Depends(),
    hunt_dao: HuntDAO = Depends(),
    feeding: FeedingDAO = Depends(),
) -> BirdNestedChildren:
    bird = await bird_dao.get_by_id(bird_id)
    bird = BirdNestedChildren(**bird.dict())
    bird.weights = await weight_dao.filter_by_bird_id(bird_id)
    bird.trainings = await training_dao.filter_by_bird_id(bird_id)
    bird.hunts = await hunt_dao.filter_by_bird_id(bird_id)
    bird.feedings = await feeding.filter_by_bird_id(bird_id)
    return bird
