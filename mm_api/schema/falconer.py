from datetime import datetime
from typing import Optional

from mew_mate_api.schemas.schema.bird import BirdRead
from pydantic import BaseModel


class FalconerBase(BaseModel):
    name: str
    permit_class: str
    permit_number: str


class FalconerCreate(FalconerBase):
    id: Optional[str] = None


class FalconerUpdate(FalconerBase):
    id: str


class FalconerRead(FalconerBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FalconerNestedBirds(FalconerRead):
    birds: Optional[list[BirdRead]]
