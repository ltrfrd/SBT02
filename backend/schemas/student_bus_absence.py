# -----------------------------------------------------------
# Student Bus Absence Schemas
# - Validate planned no-ride create and response payloads
# -----------------------------------------------------------
from datetime import date, datetime  # Date and timestamp types

from pydantic import BaseModel, ConfigDict  # Pydantic schema helpers

from backend.models.student_bus_absence import StudentBusAbsenceSource  # Shared absence source enum
from backend.schemas.run import RunType  # Reuse existing run type convention


class StudentBusAbsenceCreate(BaseModel):
    date: date  # Planned no-ride date
    run_type: RunType  # AM / MIDDAY / PM / EXTRA
    source: StudentBusAbsenceSource = StudentBusAbsenceSource.PARENT  # Defaults to parent-reported absence


class StudentBusAbsenceOut(BaseModel):
    id: int  # Absence identifier
    student_id: int  # Student receiving the planned absence
    date: date  # Planned no-ride date
    run_type: RunType  # AM / MIDDAY / PM / EXTRA
    source: StudentBusAbsenceSource  # Reporting source
    created_at: datetime  # Record creation timestamp

    model_config = ConfigDict(from_attributes=True)  # Enable ORM serialization
