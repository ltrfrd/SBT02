"""stops add route_id sequence index

Revision ID: f216358c4479
Revises: 20260228_uniq_stop_route_seq
Create Date: 2026-03-02 04:14:34.024945

"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = 'f216358c4479'
down_revision = '20260228_uniq_stop_route_seq'
branch_labels = None
depends_on = None


# ===========================================================  # Section header
# Stops: add route_id + sequence index                          # Migration purpose
# ===========================================================  # Section header

from alembic import op  # Alembic operations API

def upgrade() -> None:  # Apply migration
    op.create_index(  # Create DB index
        "ix_stops_route_id_sequence",  # Index name
        "stops",  # Table name
        ["route_id", "sequence"],  # Indexed columns (order matters)
        unique=False,  # Non-unique index
    )  # End create_index

def downgrade() -> None:  # Revert migration
    op.drop_index(  # Drop DB index
        "ix_stops_route_id_sequence",  # Index name
        table_name="stops",  # Table name
    )  # End drop_index