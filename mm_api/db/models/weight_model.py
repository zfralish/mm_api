# flake8: noqa: F821

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mm_api.db.base import Base


class WeightModel(Base):
    __tablename__ = "weights"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    bird_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("birds.id"))
    weight: Mapped[float]
    w_time: Mapped[datetime] = mapped_column(server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
    bird: Mapped["BirdModel"] = relationship(back_populates="weights")  # type: ignore
    start_hunt: Mapped["HuntModel"] = relationship(  # type: ignore
        back_populates="start_weight",
        foreign_keys="HuntModel.start_weight_id",
    )
    end_hunt: Mapped["HuntModel"] = relationship(  # type: ignore
        back_populates="end_weight",
        foreign_keys="HuntModel.end_weight_id",
    )
    start_training: Mapped[Optional["TrainingModel"]] = relationship(  # type: ignore
        back_populates="start_weight",
        foreign_keys="TrainingModel.start_weight_id",
    )
    end_training: Mapped[Optional["TrainingModel"]] = relationship(  # type: ignore
        back_populates="end_weight",
        foreign_keys="TrainingModel.end_weight_id",
    )
    start_feeding: Mapped[Optional["FeedingModel"]] = relationship(  # type: ignore
        back_populates="start_weight",
        foreign_keys="FeedingModel.start_weight_id",
    )
    end_feeding: Mapped[Optional["FeedingModel"]] = relationship(  # type: ignore
        back_populates="end_weight",
        foreign_keys="FeedingModel.end_weight_id",
    )
