from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StudentStageResult(Base):
    __tablename__ = "student_stage_results"
    __table_args__ = (
        UniqueConstraint("stage_id", "student_id", name="uq_stage_student_result"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stage_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("placement_stages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    registration_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("student_registrations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="QUALIFIED"
    )  # QUALIFIED, DISQUALIFIED, ABSENT
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    remarks: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    stage = relationship("PlacementStage", back_populates="stage_results")
    student = relationship("Student", back_populates="stage_results")
    registration = relationship("StudentRegistration", back_populates="stage_results")

    def __repr__(self) -> str:
        return f"<StudentStageResult(id={self.id}, stage={self.stage_id}, student={self.student_id}, status='{self.status}')>"
