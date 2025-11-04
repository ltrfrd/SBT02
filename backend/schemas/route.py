# ===========================================================
# backend/schemas/route.py — BST Route Schemas
# -----------------------------------------------------------
# Pydantic models for Route creation and output responses.
# ===========================================================
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

# -----------------------------------------------------------
# Schema for creating a new route (POST request)
# -----------------------------------------------------------
class RouteCreate(BaseModel):
    route_number: str  # e.g., "12A"
    driver_id: Optional[int] = None  # Optional assigned driver
    unit_number: Optional[str] = None  # Bus or vehicle ID
    num_runs: Optional[int] = 2  # Default = 2 (AM + PM), can be 1, 3, 4+
    school_ids: Optional[List[int]] = None  # List of linked school IDs

# -----------------------------------------------------------
# Schema for reading route data (GET response)
# -----------------------------------------------------------
class RouteOut(BaseModel):
    id: int  # Auto-generated route ID
    route_number: str
    driver_id: Optional[int] = None
    unit_number: Optional[str] = None
    num_runs: Optional[int] = 2
    school_ids: Optional[List[int]] = None  # Associated schools

    model_config = ConfigDict(from_attributes=True)  # ORM to schema conversion