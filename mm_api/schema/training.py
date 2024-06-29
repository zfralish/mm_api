from datetime import datetime
from typing import Optional
from uuid import UUID

from mew_mate_api.schemas.schema.weight import WeightRead
from pydantic import BaseModel


class TrainingBase(BaseModel):
    bird_id: UUID
    start_time: datetime
    end_time: datetime
    training_type: str
    notes: str
    performance: int
    start_weight_id: Optional[UUID] = None
    end_weight_id: Optional[UUID] = None


class TrainingRead(TrainingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrainingNestedWeight(TrainingRead):
    start_weight: Optional[WeightRead] = None
    end_weight: Optional[WeightRead] = None
