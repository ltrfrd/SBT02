# ===========================================================
# backend/schemas/__init__.py — SBT Schemas Index
# -----------------------------------------------------------
# Centralized import hub for all Pydantic schemas.
# Routers and modules can import from here instead of each file.
# ===========================================================

# -----------------------------------------------------------
# Import each schema module explicitly
# -----------------------------------------------------------
from .driver import DriverCreate, DriverOut          # Driver request/response
from .school import SchoolCreate, SchoolOut          # School request/response
from .student import StudentCreate, StudentOut       # Student request/response
from .route import RouteCreate, RouteOut             # Route request/response
from .stop import StopCreate, StopOut                # Stop request/response
from .run import RunCreate, RunOut                   # Run request/response
from .payroll import PayrollCreate, PayrollOut       # Payroll (view + charter)

# -----------------------------------------------------------
# Control what is exported when using 'from backend.schemas import *'
# -----------------------------------------------------------
__all__ = [
    "DriverCreate", "DriverOut",
    "SchoolCreate", "SchoolOut",
    "StudentCreate", "StudentOut",
    "RouteCreate", "RouteOut",
    "StopCreate", "StopOut",
    "RunCreate", "RunOut",
    "PayrollCreate", "PayrollOut",
]
