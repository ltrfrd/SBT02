# ===========================================================
# backend/schemas/run.py — BST Run Schemas
# -----------------------------------------------------------
# Pydantic models for Run creation and output responses.
# ===========================================================
from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional
from datetime import datetime

# -----------------------------------------------------------
# Run type enum: same values as in models/run.py
# -----------------------------------------------------------
class RunType(str, Enum):
    AM = "AM"
    MIDDAY = "MIDDAY"
    PM = "PM"
    EXTRA = "EXTRA"

# -----------------------------------------------------------
# Schema for creating a new run (POST request)
# -----------------------------------------------------------
class RunCreate(BaseModel):
    driver_id: int  # FK: driver assigned to the run
    route_id: int   # FK: route linked to this run
    run_type: RunType  # Enum: AM / MIDDAY / PM / EXTRA
    start_time: datetime  # Actual start time
    end_time: Optional[datetime] = None  # End time (nullable until run ends)

# -----------------------------------------------------------
# Schema for returning run data (GET response)
# -----------------------------------------------------------
class RunOut(BaseModel):
    id: int  # Auto-generated unique ID
    driver_id: int
    route_id: int
    run_type: RunType
    start_time: datetime
    end_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # ORM to schema conversion