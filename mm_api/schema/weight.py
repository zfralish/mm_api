from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class WeightBase(BaseModel):
    bird_id: UUID
    weight: float
    w_time: datetime


class WeightCreate(WeightBase):
    id: Optional[UUID] = None


class WeightRead(WeightBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
