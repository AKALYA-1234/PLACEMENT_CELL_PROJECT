from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ImportLog(Base):
    __tablename__ = "import_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False, default="EXCEL")
    company_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True
    )
    drive_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("placement_drives.id", ondelete="CASCADE"), nullable=True, index=True
    )
    stage_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("placement_stages.id", ondelete="SET NULL"), nullable=True, index=True
    )
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    imported_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="SUCCESS")
    error_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    imported_by: Mapped[str | None] = mapped_column(String(150), nullable=True)
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    company = relationship("Company", back_populates="import_logs")
    drive = relationship("PlacementDrive", back_populates="import_logs")
    stage = relationship("PlacementStage", back_populates="import_logs")

    def __repr__(self) -> str:
        return f"<ImportLog(id={self.id}, file='{self.filename}', status='{self.status}')>"
