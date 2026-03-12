# -----------------------------------------------------------
# Student Bus Absence Router
# - Manage planned student no-ride records independently of incidents
# -----------------------------------------------------------
from datetime import date  # Query and payload date type

from fastapi import APIRouter, Depends, HTTPException, Query, status  # FastAPI router primitives
from sqlalchemy.exc import IntegrityError  # Database integrity errors
from sqlalchemy.orm import Session  # Database session type

from database import get_db  # Shared DB dependency
from backend.schemas.student_bus_absence import StudentBusAbsenceCreate, StudentBusAbsenceOut  # Planned absence schemas
from backend.schemas.run import RunType  # Reuse existing run type convention
from backend.models import student as student_model  # Student validation model
from backend.models.student_bus_absence import StudentBusAbsence  # Planned absence model
from backend.utils.db_errors import raise_conflict_if_unique  # Shared unique-conflict helper


router = APIRouter(prefix="/students", tags=["StudentBusAbsences"])  # Student-scoped planned absence routes


def _get_student_or_404(student_id: int, db: Session) -> student_model.Student:
    student = db.get(student_model.Student, student_id)  # Load student by ID
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")  # Stop when student is missing
    return student


@router.post(
    "/{student_id}/bus_absence",
    response_model=StudentBusAbsenceOut,
    status_code=status.HTTP_201_CREATED,
)
def create_student_bus_absence(
    student_id: int,
    payload: StudentBusAbsenceCreate,
    db: Session = Depends(get_db),
):
    _get_student_or_404(student_id, db)  # Validate student exists before creating absence

    try:
        absence = StudentBusAbsence(student_id=student_id, **payload.model_dump())  # Build planned absence row
        db.add(absence)  # Stage new absence
        db.commit()  # Persist absence
        db.refresh(absence)  # Reload generated fields
        return absence
    except IntegrityError as e:
        db.rollback()  # Clear failed transaction before translating error
        raise_conflict_if_unique(
            db,
            e,
            constraint_name="uq_student_bus_absence_student_date_run_type",
            sqlite_columns=("student_id", "date", "run_type"),
            detail="Student bus absence already exists for this date and run type",
        )
        raise HTTPException(status_code=400, detail="Integrity error")  # Fallback for non-unique integrity failures


@router.delete("/{student_id}/bus_absence", status_code=status.HTTP_204_NO_CONTENT)
def delete_student_bus_absence(
    student_id: int,
    absence_date: date = Query(..., alias="date"),
    run_type: RunType = Query(...),
    db: Session = Depends(get_db),
):
    _get_student_or_404(student_id, db)  # Validate student exists before deleting absence

    absence = (
        db.query(StudentBusAbsence)
        .filter(StudentBusAbsence.student_id == student_id)
        .filter(StudentBusAbsence.date == absence_date)
        .filter(StudentBusAbsence.run_type == run_type)
        .first()
    )  # Load matching planned absence

    if not absence:
        raise HTTPException(status_code=404, detail="Student bus absence not found")  # Only delete existing planned absences

    db.delete(absence)  # Remove planned absence
    db.commit()  # Persist deletion
    return None
