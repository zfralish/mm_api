# flake8: noqa: F821

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mm_api.db.base import Base


class BirdModel(Base):
    __tablename__ = "birds"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4())
    falconer_id: Mapped[str] = mapped_column(ForeignKey("falconers.id"))
    name: Mapped[str]
    gender: Mapped[str]
    species: Mapped[str]
    trap_date: Mapped[datetime] = mapped_column(server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
    falconer: Mapped["FalconerModel"] = relationship(  # type: ignore
        back_populates="birds",
    )
    weights: Mapped[Optional[List["WeightModel"]]] = relationship(  # type: ignore
        back_populates="bird",
        cascade="all, delete",
    )
    hunts: Mapped[Optional[List["HuntModel"]]] = relationship(  # type: ignore
        back_populates="bird",
        cascade="all, delete",
    )
    trainings: Mapped[Optional[List["TrainingModel"]]] = relationship(  # type: ignore
        back_populates="bird",
        cascade="all, delete",
    )
    feedings: Mapped[Optional[List["FeedingModel"]]] = relationship(  # type: ignore
        back_populates="bird",
        cascade="all, delete",
    )
