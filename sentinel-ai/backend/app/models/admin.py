from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
import uuid

from app.core.database import Base

if TYPE_CHECKING:
    from .user import User


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="admin")

    def __repr__(self) -> str:
        return f"<Admin(id={self.id}, user_id={self.user_id})>"
