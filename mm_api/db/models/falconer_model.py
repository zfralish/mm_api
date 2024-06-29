# flake8: noqa: F821

from datetime import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mm_api.db.base import Base


class FalconerModel(Base):
    __tablename__ = "falconers"
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    permit_class: Mapped[str]
    permit_number: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
    birds: Mapped[Optional[List["BirdModel"]]] = relationship(  # type: ignore
        back_populates="falconer",
        cascade="all, delete",
    )
