# ===========================================================
# backend/routers/route.py — BST Route Router (CLEAN + FIXED)
# ===========================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db

from backend.models.route import Route
from backend.models.school import School
from backend.schemas.route import RouteCreate, RouteOut

# -----------------------------------------------------------
# Router setup
# -----------------------------------------------------------
router = APIRouter(
    prefix="/routes",
    tags=["Routes"]
)

# -----------------------------------------------------------
# POST /routes → Create new route
# -----------------------------------------------------------
@router.post("/", response_model=RouteOut)
def create_route(route: RouteCreate, db: Session = Depends(get_db)):
    db_route = Route(**route.model_dump(exclude_unset=True))
    db.add(db_route)
    db.commit()
    db.refresh(db_route)

    if route.school_ids:
        db_route.schools = db.query(School).filter(School.id.in_(route.school_ids)).all()
        db.commit()
        db.refresh(db_route)

    return db_route


# -----------------------------------------------------------
# GET /routes → Retrieve all routes
# -----------------------------------------------------------
@router.get("/", response_model=List[RouteOut])
def get_routes(db: Session = Depends(get_db)):
    return db.query(Route).all()


# -----------------------------------------------------------
# GET /routes/{route_id} → Retrieve specific route
# -----------------------------------------------------------
@router.get("/{route_id}", response_model=RouteOut)
def get_route(route_id: int, db: Session = Depends(get_db)):
    route = db.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


# -----------------------------------------------------------
# PUT /routes/{route_id} → Update route info
# -----------------------------------------------------------
@router.put("/{route_id}", response_model=RouteOut)
def update_route(route_id: int, route_in: RouteCreate, db: Session = Depends(get_db)):
    route = db.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    # Update only provided fields
    for key, value in route_in.model_dump(exclude_unset=True).items():
        setattr(route, key, value)

    db.commit()

    # Update school relationships if included
    if route_in.school_ids is not None:
        route.schools = db.query(School).filter(School.id.in_(route_in.school_ids)).all()
        db.commit()

    db.refresh(route)
    return route


# -----------------------------------------------------------
# DELETE /routes/{route_id} → Delete a route
# -----------------------------------------------------------
@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(route_id: int, db: Session = Depends(get_db)):
    route = db.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    db.delete(route)
    db.commit()
    return None


# -----------------------------------------------------------
# GET /routes/{route_id}/schools → View assigned schools
# -----------------------------------------------------------
@router.get("/{route_id}/schools", response_model=List[dict])
def get_route_schools(route_id: int, db: Session = Depends(get_db)):
    route = db.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    return [{"id": s.id, "name": s.name, "address": s.address} for s in route.schools]
