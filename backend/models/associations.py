from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


route_schools = Table(
    "route_schools",
    Base.metadata,
    Column("route_id", Integer, ForeignKey("routes.id"), primary_key=True),
    Column("school_id", Integer, ForeignKey("schools.id"), primary_key=True),
)


class StudentRunAssignment(Base):
    __tablename__ = "student_run_assignments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    run_id = Column(Integer, ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    stop_id = Column(Integer, ForeignKey("stops.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "run_id", name="uq_student_run_assignment"),
    )

    student = relationship("Student", back_populates="run_assignments")
    run = relationship("Run", back_populates="student_assignments")
    stop = relationship("Stop", back_populates="student_assignments")
