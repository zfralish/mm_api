from typing import List

from fastapi import APIRouter, Depends

from mm_api.db.dao.training_dao import TrainingDAO
from mm_api.schema.training import TrainingBase, TrainingRead
from mm_api.web.dependencies import is_authenticated

router = APIRouter(prefix="/training")


@router.get("/{training_id}")
async def get_training(
    training_id: str,
    training_dao: TrainingDAO = Depends(),
) -> TrainingRead:
    return await training_dao.get_by_id(training_id)


@router.post("", status_code=201)
async def create_training(
    training: TrainingBase,
    training_dao: TrainingDAO = Depends(),
) -> TrainingRead:
    return await training_dao.create(training)


@router.post("/bulk", status_code=201)
async def create_bulk_training(
    trainings: List[TrainingBase],
    training_dao: TrainingDAO = Depends(),
) -> None:
    return await training_dao.bulk_create(trainings)
