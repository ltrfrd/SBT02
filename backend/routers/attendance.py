# -----------------------------------------------------------
# Attendance Router
# - Expose attendance-layer endpoints using the existing report behavior
# -----------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException, status  # FastAPI components
from sqlalchemy.orm import Session  # Database session type
from datetime import date  # Date filter type

from database import get_db  # Shared DB dependency
from backend.utils import attendance_generator  # Attendance utility functions


router = APIRouter(
    prefix="/reports",  # Keep existing path stable during the rename phase
    tags=["Attendance"],  # Rename outward-facing API label
)


@router.get("/driver/{driver_id}", status_code=status.HTTP_200_OK)
def get_driver_attendance(driver_id: int, db: Session = Depends(get_db)):
    """Return work summary for one driver."""  # Behavior unchanged during rename
    attendance = attendance_generator.driver_summary(db, driver_id)  # Build driver attendance payload
    if "error" in attendance:
        raise HTTPException(status_code=404, detail=attendance["error"])  # Preserve missing-resource behavior
    return attendance


@router.get("/route/{route_id}", status_code=status.HTTP_200_OK)
def get_route_attendance(route_id: int, db: Session = Depends(get_db)):
    """Return detailed attendance summary for one route."""  # Outward wording updated only
    attendance = attendance_generator.route_summary(db, route_id)  # Build route attendance payload
    if "error" in attendance:
        raise HTTPException(status_code=404, detail=attendance["error"])  # Preserve missing-resource behavior
    return attendance


@router.get("/payroll", status_code=status.HTTP_200_OK)
def get_payroll_attendance(start: date, end: date, db: Session = Depends(get_db)):
    """Return payroll summary for all drivers within the given date range."""  # Behavior unchanged during rename
    attendance = attendance_generator.payroll_summary(db, start, end)  # Build payroll attendance payload
    if not attendance:
        raise HTTPException(status_code=404, detail="No payroll records found in range")  # Preserve empty-range behavior
    return {
        "date_range": {"start": start, "end": end},
        "total_records": len(attendance),
        "records": attendance,
    }  # Preserve existing response payload shape


__all__ = ["router"]  # Export router explicitly
