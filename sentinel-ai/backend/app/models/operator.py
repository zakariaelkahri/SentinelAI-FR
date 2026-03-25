from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
import uuid

from app.core.database import Base

if TYPE_CHECKING:
    from .user import User
    from .camera import Camera


class Operator(Base):
    __tablename__ = "operators"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="operator")
    cameras: Mapped[List["Camera"]] = relationship(
        "Camera", back_populates="operator", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Operator(id={self.id}, user_id={self.user_id})>"
