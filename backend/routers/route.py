# ===========================================================
# backend/routers/route.py — BST Route Router
# -----------------------------------------------------------
# Handles CRUD for bus routes and manages linked schools.
# ===========================================================
from fastapi import APIRouter, Depends, HTTPException, status  # FastAPI imports
from sqlalchemy.orm import Session  # DB session handling
from typing import List  # For list responses
from database import get_db  # DB dependency
from backend import schemas  # Pydantic schemas
from backend.models import route as route_model  # Route model
from backend.models import school as school_model  # School model
from backend.models import driver as driver_model  # Driver model

# -----------------------------------------------------------
# Router setup
# -----------------------------------------------------------
router = APIRouter(
    prefix="/routes",  # Base path for routes
    tags=["Routes"]    # Swagger section name
)

# -----------------------------------------------------------
# POST /routes → Create new route
# -----------------------------------------------------------
@router.post("/", response_model=schemas.RouteOut, status_code=status.HTTP_201_CREATED)
def create_route(route: schemas.RouteCreate, db: Session = Depends(get_db)):
    """Create a new bus route and optionally link schools."""
    # Validate driver if assigned
    if route.driver_id:
        driver = db.get(driver_model.Driver, route.driver_id)
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
    # Create route record
    new_route = route_model.Route(
        route_number=route.route_number,
        unit_number=route.unit_number or "Unassigned",
        num_runs=route.num_runs or 2,
        driver_id=route.driver_id,
    )
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    # Link schools if provided
    if route.school_ids:
        schools = db.query(school_model.School).filter(
            school_model.School.id.in_(route.school_ids)
        ).all()
        new_route.schools = schools
        db.commit()
    db.refresh(new_route)
    return new_route

# -----------------------------------------------------------
# GET /routes → Retrieve all routes
# -----------------------------------------------------------
@router.get("/", response_model=List[schemas.RouteOut])
def get_routes(db: Session = Depends(get_db)):
    """List all bus routes."""
    return db.query(route_model.Route).all()

# -----------------------------------------------------------
# GET /routes/{route_id} → Retrieve specific route
# -----------------------------------------------------------
@router.get("/{route_id}", response_model=schemas.RouteOut)
def get_route(route_id: int, db: Session = Depends(get_db)):
    """Get details for a single route."""
    route = db.get(route_model.Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route

# -----------------------------------------------------------
# PUT /routes/{route_id} → Update route info
# -----------------------------------------------------------
@router.put("/{route_id}", response_model=schemas.RouteOut)
def update_route(route_id: int, route_in: schemas.RouteCreate, db: Session = Depends(get_db)):
    """Modify route details such as driver or assigned schools."""
    route = db.get(route_model.Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    # Update core fields
    for key, value in route_in.model_dump(exclude_unset=True).items():
        if hasattr(route, key):
            setattr(route, key, value)
    db.commit()
    # Update school associations if provided
    if route_in.school_ids is not None:
        schools = db.query(school_model.School).filter(
            school_model.School.id.in_(route_in.school_ids)
        ).all()
        route.schools = schools
        db.commit()
    db.refresh(route)
    return route

# -----------------------------------------------------------
# DELETE /routes/{route_id} → Delete a route
# -----------------------------------------------------------
@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(route_id: int, db: Session = Depends(get_db)):
    """Delete a route and unlink associated schools."""
    route = db.get(route_model.Route, route_id)
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
    """List all schools connected to a route."""
    route = db.get(route_model.Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return [
        {"id": s.id, "name": s.name, "address": s.address}
        for s in route.schools
    ]