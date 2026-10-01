from datetime import datetime, date
from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PlacementDrive(Base):
    __tablename__ = "placement_drives"
    __table_args__ = (
        UniqueConstraint("company_id", "drive_name", "academic_year", name="uq_drive_company_name_year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    drive_name: Mapped[str] = mapped_column(String(200), nullable=False)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    job_role: Mapped[str | None] = mapped_column(String(150), nullable=True)
    ctc_lpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    drive_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    company = relationship("Company", back_populates="drives")
    stages = relationship(
        "PlacementStage", back_populates="drive", cascade="all, delete-orphan", lazy="selectin",
        order_by="PlacementStage.stage_order"
    )
    registrations = relationship("StudentRegistration", back_populates="drive", cascade="all, delete-orphan", lazy="selectin")
    placements = relationship("Placement", back_populates="drive", cascade="all, delete-orphan", lazy="selectin")
    import_logs = relationship("ImportLog", back_populates="drive", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self) -> str:
        return f"<PlacementDrive(id={self.id}, drive_name='{self.drive_name}', year='{self.academic_year}')>"
