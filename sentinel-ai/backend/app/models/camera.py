from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, TYPE_CHECKING
import uuid
import enum

from app.core.database import Base

if TYPE_CHECKING:
    from .operator import Operator
    from .alert import Alert


class CameraStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rtsp_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[CameraStatus] = mapped_column(
        SQLEnum(CameraStatus), default=CameraStatus.OFFLINE, nullable=False
    )

    # Foreign Keys
    operator_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("operators.id"), nullable=True
    )

    # Relationships
    operator: Mapped[Optional["Operator"]] = relationship(
        "Operator", back_populates="cameras"
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert", back_populates="camera", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Camera(id={self.id}, name='{self.name}', status='{self.status}')>"
