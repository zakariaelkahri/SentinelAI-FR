from sqlalchemy import String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
import uuid
import enum

from app.core.database import Base

if TYPE_CHECKING:
    from .alert import Alert


class IncidentStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    ai_description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[IncidentStatus] = mapped_column(
        SQLEnum(IncidentStatus), default=IncidentStatus.PENDING, nullable=False
    )

    # Foreign Keys
    alert_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("alerts.id"), nullable=False
    )

    # Relationships
    alert: Mapped["Alert"] = relationship("Alert", back_populates="incident_reports")

    def __repr__(self) -> str:
        return f"<IncidentReport(id={self.id}, type='{self.type}', status='{self.status}')>"
