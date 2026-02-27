# ===========================================================
# backend/schemas/stop.py — SBT Stop Schemas
# -----------------------------------------------------------
# Pydantic models for Stop creation and output responses.
# Stops are identified primarily by sequence number.
# ===========================================================

from pydantic import BaseModel, ConfigDict
from enum import Enum



# -----------------------------------------------------------
# Stop type enum: pickup or dropoff
# -----------------------------------------------------------
class StopType(str, Enum):
    PICKUP = "pickup"
    DROPOFF = "dropoff"

# -----------------------------------------------------------
# Schema for creating a stop (POST request)
# -----------------------------------------------------------
class StopCreate(BaseModel):
    sequence: int            # Stop number in the route (1, 2, 3...)
    type: StopType           # Either pickup or dropoff
    route_id: int            # FK: route this stop belongs to

    name: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
# -----------------------------------------------------------
# Schema for returning stop data (GET response)
# -----------------------------------------------------------
class StopOut(BaseModel):
    id: int                  # Auto-generated unique ID
    sequence: int            # Stop number on the route
    type: StopType           # pickup/dropoff
    route_id: int            # Linked route ID
    name: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    model_config = ConfigDict(from_attributes=True)
