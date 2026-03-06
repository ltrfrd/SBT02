from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db

from backend.models.route import Route
from backend.models.school import School
from backend.schemas.route import RouteCreate, RouteOut


router = APIRouter(prefix="/routes", tags=["Routes"])


@router.post("/", response_model=RouteOut)
def create_route(route: RouteCreate, db: Session = Depends(get_db)):
    payload = route.model_dump(exclude_unset=True)
    school_ids = payload.pop("school_ids", [])
    db_route = Route(**payload)
    db.add(db_route)
    db.commit()
    db.refresh(db_route)

    if school_ids:
        db_route.schools = db.query(School).filter(School.id.in_(school_ids)).all()
        db.commit()
        db.refresh(db_route)

    return db_route


@router.get("/", response_model=List[RouteOut])
def get_routes(db: Session = Depends(get_db)):
    return db.query(Route).all()


@router.get("/{route_id}", response_model=RouteOut)
def get_route(route_id: int, db: Session = Depends(get_db)):
    route = db.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.put("/{route_id}", response_model=RouteOut)
def update_route(route_id: int, route_in: RouteCreate, db: Session = Depends(get_db)):
    route = db.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    update_data = route_in.model_dump(exclude_unset=True)
    school_ids = update_data.pop("school_ids", None)

    for key, value in update_data.items():
        setattr(route, key, value)

    db.commit()

    if school_ids is not None:
        route.schools = db.query(School).filter(School.id.in_(school_ids)).all()
        db.commit()

    db.refresh(route)
    return route


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(route_id: int, db: Session = Depends(get_db)):
    route = db.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    db.delete(route)
    db.commit()
    return None


@router.get("/{route_id}/schools", response_model=List[dict])
def get_route_schools(route_id: int, db: Session = Depends(get_db)):
    route = db.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    return [{"id": s.id, "name": s.name, "address": s.address} for s in route.schools]
