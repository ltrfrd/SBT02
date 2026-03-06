from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from backend.models.associations import StudentRunAssignment
from backend.models import student as student_model
from backend.models import run as run_model
from backend.models import stop as stop_model
from backend.schemas.student_run_assignment import (
    StudentRunAssignmentCreate,
    StudentRunAssignmentOut,
)
from backend.utils.db_errors import raise_conflict_if_unique


router = APIRouter(prefix="/student-run-assignments", tags=["StudentRunAssignments"])


@router.post("/", response_model=StudentRunAssignmentOut, status_code=status.HTTP_201_CREATED)
def create_assignment(payload: StudentRunAssignmentCreate, db: Session = Depends(get_db)):
    student = db.get(student_model.Student, payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    run = db.get(run_model.Run, payload.run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    stop = db.get(stop_model.Stop, payload.stop_id)
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")

    if stop.run_id != payload.run_id:
        raise HTTPException(status_code=400, detail="Stop does not belong to run")

    try:
        assignment = StudentRunAssignment(**payload.model_dump())
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment
    except IntegrityError as e:
        db.rollback()
        raise_conflict_if_unique(
            db,
            e,
            constraint_name="uq_student_run_assignment",
            sqlite_columns=("student_id", "run_id"),
            detail="Student is already assigned for this run",
        )
        raise HTTPException(status_code=400, detail="Integrity error")


@router.get("/", response_model=List[StudentRunAssignmentOut])
def list_assignments(
    run_id: int | None = None,
    student_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(StudentRunAssignment)
    if run_id is not None:
        query = query.filter(StudentRunAssignment.run_id == run_id)
    if student_id is not None:
        query = query.filter(StudentRunAssignment.student_id == student_id)
    return query.all()


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.get(StudentRunAssignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(assignment)
    db.commit()
    return None
