from datetime import datetime, date
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PlacementStage(Base):
    __tablename__ = "placement_stages"
    __table_args__ = (
        UniqueConstraint("drive_id", "stage_order", name="uq_stage_drive_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    drive_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("placement_drives.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stage_order: Mapped[int] = mapped_column(Integer, nullable=False)
    stage_name: Mapped[str] = mapped_column(String(200), nullable=False)
    normalized_category: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PROGRESSION"
    )
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    stage_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    drive = relationship("PlacementDrive", back_populates="stages")
    stage_results = relationship("StudentStageResult", back_populates="stage", cascade="all, delete-orphan", lazy="selectin")
    import_logs = relationship("ImportLog", back_populates="stage", lazy="selectin")

    def __repr__(self) -> str:
        return f"<PlacementStage(id={self.id}, drive={self.drive_id}, name='{self.stage_name}', order={self.stage_order})>"
