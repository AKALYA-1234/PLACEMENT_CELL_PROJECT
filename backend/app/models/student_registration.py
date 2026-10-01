from datetime import datetime
from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StudentRegistration(Base):
    __tablename__ = "student_registrations"
    __table_args__ = (
        UniqueConstraint("drive_id", "student_id", name="uq_student_drive_reg"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    drive_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("placement_drives.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    registration_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    drive = relationship("PlacementDrive", back_populates="registrations")
    student = relationship("Student", back_populates="registrations")
    stage_results = relationship("StudentStageResult", back_populates="registration", cascade="all, delete-orphan", lazy="selectin")
    placement = relationship("Placement", back_populates="registration", uselist=False, cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self) -> str:
        return f"<StudentRegistration(id={self.id}, student={self.student_id}, drive={self.drive_id})>"
