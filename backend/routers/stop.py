from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from backend.deps.admin import require_admin
from backend.models import stop as stop_model
from backend.models import run as run_model
from backend.models.stop import Stop
from backend.schemas.stop import StopCreate, StopOut, StopUpdate, StopReorder
from backend.utils.db_errors import raise_conflict_if_unique


router = APIRouter(prefix="/stops", tags=["Stops"])

SHIFT_OFFSET = 100000


def shift_block_up(db: Session, run_id: int, start_seq: int, end_seq: int) -> None:
    if start_seq > end_seq:
        return

    db.execute(
        update(stop_model.Stop)
        .where(stop_model.Stop.run_id == run_id)
        .where(stop_model.Stop.sequence >= start_seq)
        .where(stop_model.Stop.sequence <= end_seq)
        .values(sequence=stop_model.Stop.sequence + SHIFT_OFFSET)
        .execution_options(synchronize_session=False)
    )

    db.execute(
        update(stop_model.Stop)
        .where(stop_model.Stop.run_id == run_id)
        .where(stop_model.Stop.sequence >= start_seq + SHIFT_OFFSET)
        .where(stop_model.Stop.sequence <= end_seq + SHIFT_OFFSET)
        .values(sequence=stop_model.Stop.sequence - SHIFT_OFFSET + 1)
        .execution_options(synchronize_session=False)
    )


def shift_block_down(db: Session, run_id: int, start_seq: int, end_seq: int) -> None:
    if start_seq > end_seq:
        return

    db.execute(
        update(stop_model.Stop)
        .where(stop_model.Stop.run_id == run_id)
        .where(stop_model.Stop.sequence >= start_seq)
        .where(stop_model.Stop.sequence <= end_seq)
        .values(sequence=stop_model.Stop.sequence + SHIFT_OFFSET)
        .execution_options(synchronize_session=False)
    )

    db.execute(
        update(stop_model.Stop)
        .where(stop_model.Stop.run_id == run_id)
        .where(stop_model.Stop.sequence >= start_seq + SHIFT_OFFSET)
        .where(stop_model.Stop.sequence <= end_seq + SHIFT_OFFSET)
        .values(sequence=stop_model.Stop.sequence - SHIFT_OFFSET - 1)
        .execution_options(synchronize_session=False)
    )


def normalize_run_sequences(db: Session, run_id: int) -> None:
    offset = 100000

    stops = (
        db.query(Stop)
        .filter(Stop.run_id == run_id)
        .order_by(Stop.sequence.asc())
        .all()
    )

    if not stops:
        return

    desired_by_id = {s.id: idx + 1 for idx, s in enumerate(stops)}
    if all(s.sequence == desired_by_id[s.id] for s in stops):
        return

    for s in stops:
        s.sequence = s.sequence + offset
    db.flush()

    for s in stops:
        s.sequence = desired_by_id[s.id]
    db.flush()


@router.get("/validate/{run_id}")
def validate_run_sequences(
    run_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    stops = (
        db.query(stop_model.Stop)
        .filter(stop_model.Stop.run_id == run_id)
        .order_by(stop_model.Stop.sequence.asc())
        .all()
    )

    if not stops:
        return {
            "run_id": run_id,
            "valid": True,
            "message": "No stops found (empty run).",
        }

    sequences = [s.sequence for s in stops]
    expected = list(range(1, len(stops) + 1))

    duplicates = len(sequences) != len(set(sequences))
    gaps = sequences != expected

    return {
        "run_id": run_id,
        "valid": not duplicates and not gaps,
        "total_stops": len(stops),
        "sequences": sequences,
        "expected": expected,
        "has_duplicates": duplicates,
        "has_gaps": gaps,
    }


@router.post("/normalize/{run_id}")
def force_normalize_run(
    run_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    try:
        normalize_run_sequences(db, run_id)
        db.commit()

        stops = (
            db.query(stop_model.Stop)
            .filter(stop_model.Stop.run_id == run_id)
            .order_by(stop_model.Stop.sequence.asc())
            .all()
        )

        return {
            "run_id": run_id,
            "status": "normalized",
            "total_stops": len(stops),
            "sequences": [s.sequence for s in stops],
        }
    except IntegrityError as e:
        db.rollback()
        raise_conflict_if_unique(
            db,
            e,
            constraint_name="uq_stops_run_sequence",
            sqlite_columns=("run_id", "sequence"),
            detail="Stop sequence conflict for this run",
        )
        raise HTTPException(status_code=400, detail="Integrity error")


@router.post("/", response_model=StopOut, status_code=201)
def create_stop(payload: StopCreate, db: Session = Depends(get_db)):
    try:
        run = db.get(run_model.Run, payload.run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")

        max_seq = (
            db.query(func.max(stop_model.Stop.sequence))
            .filter(stop_model.Stop.run_id == payload.run_id)
            .scalar()
        )
        max_seq = max_seq or 0

        if payload.sequence is None:
            seq = max_seq + 1
        else:
            target = max(1, min(payload.sequence, max_seq + 1))
            if target <= max_seq:
                shift_block_up(db, payload.run_id, target, max_seq)
            db.expire_all()
            seq = target

        data = payload.model_dump()
        data["sequence"] = seq

        if not data.get("name") and data.get("address"):
            data["name"] = data["address"]
        if not data.get("name"):
            data["name"] = f"Stop {seq}"

        stop = stop_model.Stop(**data)
        db.add(stop)
        db.commit()
        db.refresh(stop)
        return stop

    except IntegrityError as e:
        db.rollback()
        raise_conflict_if_unique(
            db,
            e,
            constraint_name="uq_stops_run_sequence",
            sqlite_columns=("run_id", "sequence"),
            detail="Stop sequence conflict for this run",
        )
        raise HTTPException(status_code=400, detail="Integrity error")


@router.get("/", response_model=List[StopOut])
def get_stops(run_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(stop_model.Stop)

    if run_id is not None:
        query = query.filter(stop_model.Stop.run_id == run_id)

    query = query.order_by(stop_model.Stop.sequence.asc())
    return query.all()


@router.put("/{stop_id}", response_model=StopOut)
def update_stop(
    stop_id: int, stop_in: StopUpdate, db: Session = Depends(get_db)
):
    stop = db.get(stop_model.Stop, stop_id)
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")

    updates = stop_in.model_dump(exclude_none=True)
    for key, value in updates.items():
        setattr(stop, key, value)

    db.commit()
    db.refresh(stop)
    return stop


@router.delete("/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stop(stop_id: int, db: Session = Depends(get_db)):
    try:
        stop = db.get(stop_model.Stop, stop_id)
        if not stop:
            raise HTTPException(status_code=404, detail="Stop not found")

        run_id = stop.run_id

        db.delete(stop)
        db.flush()

        normalize_run_sequences(db, run_id)

        db.commit()
        return None

    except IntegrityError as e:
        db.rollback()
        raise_conflict_if_unique(
            db,
            e,
            constraint_name="uq_stops_run_sequence",
            sqlite_columns=("run_id", "sequence"),
            detail="Stop sequence conflict for this run",
        )
        raise HTTPException(status_code=400, detail="Integrity error")


@router.put("/{stop_id}/reorder", response_model=StopOut)
def reorder_stop(
    stop_id: int, payload: StopReorder, db: Session = Depends(get_db)
):
    try:
        stop = db.get(stop_model.Stop, stop_id)
        if not stop:
            raise HTTPException(status_code=404, detail="Stop not found")

        run_id = stop.run_id
        old_seq = stop.sequence

        max_seq = (
            db.query(func.max(stop_model.Stop.sequence))
            .filter(stop_model.Stop.run_id == run_id)
            .scalar()
        ) or 0

        new_seq = max(1, min(payload.new_sequence, max_seq))

        if new_seq == old_seq:
            return stop

        offset = 100000
        stop.sequence = stop.sequence + offset
        db.flush()

        if new_seq < old_seq:
            shift_block_up(db, run_id, new_seq, old_seq - 1)
        else:
            shift_block_down(db, run_id, old_seq + 1, new_seq)

        db.expire_all()

        stop = db.get(stop_model.Stop, stop_id)
        stop.sequence = new_seq

        db.commit()
        db.refresh(stop)
        return stop

    except IntegrityError as e:
        db.rollback()
        raise_conflict_if_unique(
            db,
            e,
            constraint_name="uq_stops_run_sequence",
            sqlite_columns=("run_id", "sequence"),
            detail="Stop sequence conflict for this run",
        )
        raise HTTPException(status_code=400, detail="Integrity error")
