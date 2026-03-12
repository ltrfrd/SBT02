from .driver import router as driver_router
from .school import router as school_router
from .student import router as student_router
from .route import router as route_router
from .stop import router as stop_router
from .run import router as run_router
from .dispatch import router as dispatch_router
from .attendance import router as attendance_router
report_router = attendance_router  # Backward-compatible alias during the rename phase
from .student_run_assignment import router as student_run_assignment_router
from .student_bus_absence import router as student_bus_absence_router

__all__ = [
    "driver_router",
    "school_router",
    "student_router",
    "route_router",
    "stop_router",
    "run_router",
    "dispatch_router",
    "attendance_router",
    "report_router",
    "student_run_assignment_router",
    "student_bus_absence_router",
]
