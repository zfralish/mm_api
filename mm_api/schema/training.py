from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from mm_api.schema.weight import WeightRead


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
