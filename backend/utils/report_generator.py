# -----------------------------------------------------------
# Report Generator Compatibility
# - Preserve legacy imports while attendance becomes the app layer
# -----------------------------------------------------------
from .attendance_generator import (  # Re-export attendance-layer helpers during the rename phase
    driver_summary,
    route_summary,
    payroll_summary,
    generate_attendance,
    generate_report,
)


__all__ = [
    "driver_summary",
    "route_summary",
    "payroll_summary",
    "generate_attendance",
    "generate_report",
]  # Preserve legacy helper exports
