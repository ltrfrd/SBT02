from .driver import router as driver_router
from .school import router as school_router
from .student import router as student_router
from .route import router as route_router
from .stop import router as stop_router
from .run import router as run_router
from .payroll import router as payroll_router
from .report import router as report_router
from .student_run_assignment import router as student_run_assignment_router

__all__ = [
    "driver_router",
    "school_router",
    "student_router",
    "route_router",
    "stop_router",
    "run_router",
    "payroll_router",
    "report_router",
    "student_run_assignment_router",
]
