from datetime import datetime, date
from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Placement(Base):
    __tablename__ = "placements"
    __table_args__ = (
        UniqueConstraint("drive_id", "student_id", name="uq_placement_drive_student"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    drive_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("placement_drives.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    registration_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("student_registrations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    stage_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("placement_stages.id", ondelete="SET NULL"), nullable=True, index=True
    )
    package_ctc: Mapped[float | None] = mapped_column(Float, nullable=True)
    offer_letter_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    offer_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="OFFERED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    drive = relationship("PlacementDrive", back_populates="placements")
    student = relationship("Student", back_populates="placements")
    registration = relationship("StudentRegistration", back_populates="placement")
    stage = relationship("PlacementStage")

    def __repr__(self) -> str:
        return f"<Placement(id={self.id}, drive={self.drive_id}, student={self.student_id}, status='{self.status}')>"
