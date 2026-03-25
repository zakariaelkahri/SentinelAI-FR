from sqlalchemy import String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, TYPE_CHECKING
import uuid

from app.core.database import Base

if TYPE_CHECKING:
    from .camera import Camera
    from .incident_report import IncidentReport


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    team_bio: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    snapshot_path: Mapped[str] = mapped_column(String(500), nullable=False)

    # Foreign Keys
    camera_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cameras.id"), nullable=False
    )

    # Relationships
    camera: Mapped["Camera"] = relationship("Camera", back_populates="alerts")
    incident_reports: Mapped[List["IncidentReport"]] = relationship(
        "IncidentReport", back_populates="alert", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, type='{self.type}', confidence={self.confidence_score})>"
