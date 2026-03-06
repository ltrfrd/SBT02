from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from backend import schemas
from backend.models import run as run_model
from backend.models import driver as driver_model
from backend.models import route as route_model
from backend.models import stop as stop_model
from backend.schemas.run import RunStart, RunOut
from backend.schemas.stop import StopOut


router = APIRouter(prefix="/runs", tags=["Runs"])


@router.post("/", response_model=schemas.RunOut, status_code=status.HTTP_201_CREATED)
def create_run(run: RunStart, db: Session = Depends(get_db)):
    driver = db.get(driver_model.Driver, run.driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    route = db.get(route_model.Route, run.route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    new_run = run_model.Run(**run.model_dump(), start_time=datetime.now(timezone.utc).replace(tzinfo=None))
    db.add(new_run)
    db.commit()
    db.refresh(new_run)
    return new_run


@router.post("/start", response_model=RunOut)
def start_run(run: RunStart, db: Session = Depends(get_db)):
    driver = db.get(driver_model.Driver, run.driver_id)
    route = db.get(route_model.Route, run.route_id)

    if not driver or not route:
        raise HTTPException(status_code=404, detail="Driver or Route not found")

    new_run = run_model.Run(
        driver_id=run.driver_id,
        route_id=run.route_id,
        run_type=run.run_type,
        start_time=datetime.now(timezone.utc).replace(tzinfo=None),
    )

    db.add(new_run)
    db.commit()
    db.refresh(new_run)
    return new_run


@router.post("/end", response_model=schemas.RunOut)
def end_run(run_id: int, db: Session = Depends(get_db)):
    run = db.get(run_model.Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.end_time:
        raise HTTPException(status_code=400, detail="Run already ended")

    run.end_time = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    db.refresh(run)
    return run


@router.get("/", response_model=List[schemas.RunOut])
def get_all_runs(db: Session = Depends(get_db)):
    return db.query(run_model.Run).all()


@router.get("/{run_id}", response_model=schemas.RunOut)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.get(run_model.Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/{run_id}/stops", response_model=List[StopOut])
def get_run_stops(run_id: int, db: Session = Depends(get_db)):
    run = db.get(run_model.Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return (
        db.query(stop_model.Stop)
        .filter(stop_model.Stop.run_id == run_id)
        .order_by(stop_model.Stop.sequence.asc())
        .all()
    )
