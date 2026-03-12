# ===========================================================
# backend/schemas/dispatch.py — BST Dispatch Schemas
# -----------------------------------------------------------
# Handles dispatch workdays and charter time input.
# ===========================================================
from datetime import date, time
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


# -----------------------------------------------------------
# PayrollCreate
# - Create or update a dispatch-backed work entry
# -----------------------------------------------------------
class PayrollCreate(BaseModel):
    driver_id: int  # FK: driver submitting
    work_date: date  # Workday date
    charter_start: Optional[time] = None  # Charter start time
    charter_end: Optional[time] = None  # Charter end time
    approved: Optional[bool] = False  # Default not verified


# -----------------------------------------------------------
# PayrollOut
# - Return dispatch work entry data
# -----------------------------------------------------------
class PayrollOut(BaseModel):
    id: int
    driver_id: int
    work_date: date
    charter_start: Optional[time] = None
    charter_end: Optional[time] = None
    charter_hours: Decimal
    approved: bool

    model_config = ConfigDict(from_attributes=True)
