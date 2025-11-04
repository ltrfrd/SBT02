from backend import routers
from backend.utils import report_generator


# ===========================================================
# backend/__init__.py — BST Backend Package Index
# -----------------------------------------------------------
# Re-exports main submodules for clean imports
# ===========================================================

# Re-export core submodules
from . import models
from . import schemas
from . import routers
from . import utils

# Optional: Export commonly used items directly
# from .models.driver import Driver
# from .schemas.driver import DriverOut

__all__ = [
    "models",
    "schemas",
    "routers",
    "utils",
]