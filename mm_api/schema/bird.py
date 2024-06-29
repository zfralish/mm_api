from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from mm_api.schema.feeding import FeedingRead
from mm_api.schema.hunt import HuntRead
from mm_api.schema.training import TrainingRead
from mm_api.schema.weight import WeightRead


class BirdBase(BaseModel):
    falconer_id: str
    name: str
    gender: str
    species: str
    trap_date: datetime


class BirdCreate(BirdBase):
    id: Optional[UUID] = None


class BirdUpdate(BirdBase):
    id: UUID


class BirdRead(BirdBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BirdNestedChildren(BirdRead):
    weights: Optional[list[WeightRead]] = None
    hunts: Optional[list[HuntRead]] = None
    trainings: Optional[list[TrainingRead]] = None
    feedings: Optional[list[FeedingRead]] = None
