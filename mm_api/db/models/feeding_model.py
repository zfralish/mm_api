# flake8: noqa: F821

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mm_api.db.base import Base


class FeedingModel(Base):
    __tablename__ = "feedings"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    bird_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("birds.id"))
    f_time: Mapped[datetime] = mapped_column(server_default=func.now())
    food_type: Mapped[str]
    amount: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
    bird: Mapped["BirdModel"] = relationship(back_populates="feedings")  # type: ignore
    start_weight_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("weights.id"),
    )
    end_weight_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("weights.id"))
    start_weight: Mapped[Optional["WeightModel"]] = relationship(  # type: ignore
        back_populates="start_feeding",
        cascade="all, delete",
        foreign_keys=[start_weight_id],
    )
    end_weight: Mapped[Optional["WeightModel"]] = relationship(  # type: ignore
        back_populates="end_feeding",
        cascade="all, delete",
        foreign_keys=[end_weight_id],
    )
