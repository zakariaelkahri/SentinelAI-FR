from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import uuid
import enum

from app.core.database import Base

if TYPE_CHECKING:
    from .role import Role
    from .operator import Operator
    from .admin import Admin
    from .supervisor import Supervisor


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Foreign Keys
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)

    # Relationships
    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="raise")

    # One-to-one relationships with user types
    operator: Mapped[Optional["Operator"]] = relationship(
        "Operator", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    admin: Mapped[Optional["Admin"]] = relationship(
        "Admin", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    supervisor: Mapped[Optional["Supervisor"]] = relationship(
        "Supervisor", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', status='{self.status}')>"
