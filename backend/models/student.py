from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    grade = Column(String(10))
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"))
    stop_id = Column(Integer, ForeignKey("stops.id"))
    notification_distance_meters = Column(Integer, default=500)

    school = relationship("School", back_populates="students")
    route = relationship("Route", back_populates="students")
    stop = relationship("Stop", back_populates="students")
    run_assignments = relationship(
        "StudentRunAssignment",
        back_populates="student",
        cascade="all, delete-orphan",
    )
