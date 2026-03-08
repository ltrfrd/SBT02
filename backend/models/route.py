# =============================================================================
# backend/models/route.py — Route Model
# -----------------------------------------------------------------------------
# Represents a school bus route in the system.
#
# Relationships:
#   Route → Driver (optional assignment)
#   Route → Schools (many-to-many)
#   Route → Runs (one-to-many)
#   Route → Students (view-only legacy reference)
#
# Data flow in the system:
#   Route → Runs → Stops
#
# Notes:
#   - Runs represent actual operational trips (AM / PM).
#   - Stops belong to runs, not directly to routes.
#   - Students are assigned to runs dynamically using StudentRunAssignment.
# =============================================================================

# -------------------------------------------------------------------------
# SQLAlchemy imports
# -------------------------------------------------------------------------
from sqlalchemy import Column, Integer, String, ForeignKey  # Table column types and FK
from sqlalchemy.orm import relationship                     # ORM relationship mapping

# -------------------------------------------------------------------------
# Project imports
# -------------------------------------------------------------------------
from database import Base                                   # Declarative base for models
from .associations import route_schools                     # Many-to-many association table


# =============================================================================
# Route Model
# =============================================================================
class Route(Base):

    # ---------------------------------------------------------------------
    # Table name
    # ---------------------------------------------------------------------
    __tablename__ = "routes"                                # Database table name

    # ---------------------------------------------------------------------
    # Primary Key
    # ---------------------------------------------------------------------
    id = Column(Integer, primary_key=True, index=True)      # Unique route identifier

    # ---------------------------------------------------------------------
    # Route Identification Fields
    # ---------------------------------------------------------------------
    route_number = Column(String(50), nullable=False)       # Public route number (ex: "102A")
    unit_number = Column(String(50), nullable=True)         # Bus unit number (optional)
    num_runs = Column(Integer, nullable=True)               # Number of runs assigned to route

    # ---------------------------------------------------------------------
    # Driver Assignment
    # ---------------------------------------------------------------------
    driver_id = Column(
        Integer,
        ForeignKey("drivers.id", ondelete="SET NULL"),      # If driver removed → keep route
        nullable=True                                       # Driver assignment optional
    )

    # ---------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------

    # Driver relationship
    driver = relationship(
        "Driver",
        back_populates="routes"                             # Linked from Driver.routes
    )

    # Schools served by this route
    schools = relationship(
        "School",
        secondary=route_schools,                            # Many-to-many via association table
        back_populates="routes"
    )

    # Runs belonging to this route
    runs = relationship(
        "Run",
        back_populates="route",                             # Linked from Run.route
        cascade="all, delete-orphan",                       # Delete runs if route removed
        passive_deletes=True                                # Use DB-level ON DELETE
    )

    # Legacy student relationship (read-only)
    students = relationship(
        "Student",
        viewonly=True                                       # Not used for runtime assignment
    )