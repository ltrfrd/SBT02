# ===========================================================
# alembic/env.py — SBT Migration Environment
# -----------------------------------------------------------
# Connects Alembic to SQLAlchemy models and handles migrations.
# ===========================================================

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# -----------------------------------------------------------
# 1. Load Alembic configuration object
# -----------------------------------------------------------
config = context.config

# Interpret the .ini file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -----------------------------------------------------------
# 2. Ensure backend folder is importable
# -----------------------------------------------------------
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from backend.database import Base, settings  # type: ignore

# -----------------------------------------------------------
# 3. Provide model metadata for 'autogenerate'
# -----------------------------------------------------------
target_metadata = Base.metadata

# -----------------------------------------------------------
# 4. Read database URL dynamically from .env
# -----------------------------------------------------------
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# -----------------------------------------------------------
# 5. Migration helper functions
# -----------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (generates SQL scripts)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# -----------------------------------------------------------
# 6. Entry point
# -----------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
