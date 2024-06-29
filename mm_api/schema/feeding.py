from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from mm_api.schema.weight import WeightRead


class FeedingBase(BaseModel):
    bird_id: UUID
    f_time: datetime
    food_type: str
    amount: float
    start_weight_id: UUID
    end_weight_id: UUID


class FeedingRead(FeedingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FeedingNestedWeight(FeedingRead):
    start_weight: Optional[WeightRead] = None
    end_weight: Optional[WeightRead] = None
