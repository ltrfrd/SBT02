# -----------------------------------------------------------
# Student Bus Absence Helpers
# - Reuse planned no-ride filtering for run assignment queries
# -----------------------------------------------------------
from sqlalchemy.orm import Query, Session  # SQLAlchemy query helpers

from backend.models.associations import StudentRunAssignment  # Runtime assignment model
from backend.models.run import Run  # Operational run model
from backend.models.student_bus_absence import StudentBusAbsence  # Planned absence model


def has_student_bus_absence(student_id: int, run: Run, db: Session) -> bool:
    run_date = run.start_time.date() if run.start_time else None  # Derive planned absence date from run start
    if run_date is None:
        return False  # Runs without a date cannot match a planned absence

    return (
        db.query(StudentBusAbsence)
        .filter(StudentBusAbsence.student_id == student_id)
        .filter(StudentBusAbsence.date == run_date)
        .filter(StudentBusAbsence.run_type == run.run_type)
        .first()
        is not None
    )  # Match planned absence by student + date + run type


def apply_run_absence_filter(query: Query, run: Run) -> Query:
    run_date = run.start_time.date() if run.start_time else None  # Derive run date once for consistent filtering
    if run_date is None:
        return query  # Leave query unchanged when run has no usable date

    absent_student_ids = (
        query.session.query(StudentBusAbsence.student_id)
        .filter(StudentBusAbsence.date == run_date)
        .filter(StudentBusAbsence.run_type == run.run_type)
    )  # Planned absences that apply to this run

    return query.filter(~StudentRunAssignment.student_id.in_(absent_student_ids))  # Exclude absent students from effective assignments
