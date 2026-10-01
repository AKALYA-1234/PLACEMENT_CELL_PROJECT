from datetime import datetime
from sqlalchemy import String, Float, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        Index("idx_student_dept_year", "department", "academic_year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    register_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    mobile_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    accommodation_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cgpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    academic_year: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    registrations = relationship("StudentRegistration", back_populates="student", cascade="all, delete-orphan", lazy="selectin")
    stage_results = relationship("StudentStageResult", back_populates="student", cascade="all, delete-orphan", lazy="selectin")
    placements = relationship("Placement", back_populates="student", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, reg='{self.register_number}', name='{self.full_name}')>"
