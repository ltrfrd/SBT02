# -----------------------------------------------------------
# Report Router Compatibility
# - Keep legacy imports working while attendance becomes the app layer
# -----------------------------------------------------------
from .attendance import router  # Re-export attendance router during the rename phase


__all__ = ["router"]  # Preserve legacy router export
