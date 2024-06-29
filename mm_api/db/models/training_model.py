# flake8: noqa: F821

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mm_api.db.base import Base


class TrainingModel(Base):
    __tablename__ = "trainings"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    bird_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("birds.id"))
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    training_type: Mapped[str]
    notes: Mapped[str] = mapped_column(nullable=True)
    performance: Mapped[int] = mapped_column(default=5)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
    start_weight_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("weights.id"),
    )
    end_weight_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("weights.id"))
    start_weight: Mapped[Optional["WeightModel"]] = relationship(  # type: ignore
        back_populates="start_training",
        cascade="all, delete",
        foreign_keys=[start_weight_id],
    )
    end_weight: Mapped[Optional["WeightModel"]] = relationship(  # type: ignore
        back_populates="end_training",
        cascade="all, delete",
        foreign_keys=[end_weight_id],
    )
    bird: Mapped[Optional["BirdModel"]] = relationship(  # type: ignore
        back_populates="trainings",
    )
