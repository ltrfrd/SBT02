# -----------------------------------------------------------
# Attendance Generator
# - Provide attendance-layer summaries using the existing report logic
# -----------------------------------------------------------
from sqlalchemy.orm import Session  # Database session type
from datetime import date  # Date filter type
from backend.models import (  # Existing summary data sources
    driver as driver_model,
    route as route_model,
    run as run_model,
    dispatch as dispatch_model,
    associations as assoc_model,
    student as student_model,
)


def driver_summary(db: Session, driver_id: int) -> dict:
    drv = db.get(driver_model.Driver, driver_id)  # Load driver
    if not drv:
        return {"error": "Driver not found"}  # Return stable missing-driver payload

    total_runs = (
        db.query(run_model.Run).filter(run_model.Run.driver_id == driver_id).count()
    )  # Count runs assigned to this driver

    total_charter_hours = (
        db.query(dispatch_model.Payroll)
        .filter(dispatch_model.Payroll.driver_id == driver_id)
        .with_entities(dispatch_model.Payroll.charter_hours)
        .all()
    )  # Load payroll hour fragments for this driver

    total_hours = sum(float(h[0]) for h in total_charter_hours if h[0])  # Sum non-null charter hours

    approved = (
        db.query(dispatch_model.Payroll)
        .filter(
            dispatch_model.Payroll.driver_id == driver_id,
            dispatch_model.Payroll.approved.is_(True),
        )
        .count()
    )  # Count approved payroll days

    pending = (
        db.query(dispatch_model.Payroll)
        .filter(
            dispatch_model.Payroll.driver_id == driver_id,
            dispatch_model.Payroll.approved.is_(False),
        )
        .count()
    )  # Count pending payroll days

    return {
        "driver_id": driver_id,
        "driver_name": drv.name,
        "total_runs": total_runs,
        "charter_hours": round(total_hours, 2),
        "approved_days": approved,
        "pending_days": pending,
    }  # Preserve existing payload shape


def route_summary(db: Session, route_id: int) -> dict:
    r = db.get(route_model.Route, route_id)  # Load route
    if not r:
        return {"error": "Route not found"}  # Return stable missing-route payload

    schools_list = [{"id": s.id, "name": s.name} for s in r.schools]  # Serialize assigned schools

    stops_list = []
    for run in r.runs:
        run_stops = sorted(run.stops, key=lambda st: st.sequence)  # Keep stable stop order
        for st in run_stops:
            stops_list.append(
                {
                    "id": st.id,
                    "run_id": run.id,
                    "sequence": st.sequence,
                    "type": st.type.value,
                }
            )  # Preserve existing stop payload shape

    route_run_ids = [run.id for run in r.runs]  # Collect child run IDs once
    assignments = []
    if route_run_ids:
        assignments = (
            db.query(assoc_model.StudentRunAssignment)
            .filter(assoc_model.StudentRunAssignment.run_id.in_(route_run_ids))
            .all()
        )  # Load runtime student assignments for the route

    students_by_id = {}
    for assignment in assignments:
        student = db.get(student_model.Student, assignment.student_id)  # Resolve assigned student
        if not student or student.id in students_by_id:
            continue  # Keep unique serialized students only
        students_by_id[student.id] = {
            "id": student.id,
            "name": student.name,
            "grade": student.grade,
        }

    students_list = list(students_by_id.values())  # Convert unique student map back to list
    total_runs = db.query(run_model.Run).filter(run_model.Run.route_id == route_id).count()  # Count route runs

    return {
        "route_id": route_id,
        "route_number": r.route_number,
        "unit_number": r.unit_number,
        "num_runs": r.num_runs,
        "driver_id": r.driver_id,
        "schools": schools_list,
        "stops": stops_list,
        "students": students_list,
        "total_runs": total_runs,
    }  # Preserve existing payload shape


def payroll_summary(db: Session, start: date, end: date) -> list:
    records = (
        db.query(dispatch_model.Payroll)
        .filter(
            dispatch_model.Payroll.work_date >= start,
            dispatch_model.Payroll.work_date <= end,
        )
        .all()
    )  # Load payroll rows inside the requested range

    summary = []
    for r in records:
        summary.append(
            {
                "driver_id": r.driver_id,
                "work_date": r.work_date,
                "charter_hours": float(r.charter_hours or 0),
                "approved": r.approved,
            }
        )  # Preserve existing payroll summary row shape
    return summary


def generate_attendance(
    db: Session,
    attendance_type: str,
    ref_id: int = None,
    start: date = None,
    end: date = None,
):
    if attendance_type == "driver" and ref_id:
        return driver_summary(db, ref_id)  # Return driver attendance summary
    if attendance_type == "route" and ref_id:
        return route_summary(db, ref_id)  # Return route attendance summary
    if attendance_type == "payroll" and start and end:
        return payroll_summary(db, start, end)  # Return payroll attendance summary
    return {"error": "Invalid attendance type or parameters"}  # Preserve error-style contract


generate_report = generate_attendance  # Backward-compatible alias during the rename phase
