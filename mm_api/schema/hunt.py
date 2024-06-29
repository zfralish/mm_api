from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from mm_api.schema.weight import WeightRead


class HuntBase(BaseModel):
    prey_type: str
    prey_count: int
    notes: Optional[str] = None
    start_weight_id: Optional[UUID] = None
    end_weight_id: Optional[UUID] = None
    start_time: datetime
    end_time: datetime
    bird_id: UUID


class HuntRead(HuntBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HuntNestedWeight(HuntRead):
    start_weight: Optional[WeightRead] = None
    end_weight: Optional[WeightRead] = None
