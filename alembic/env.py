from logging.config import fileConfig                                                     # Configure logging from alembic.ini
from sqlalchemy import engine_from_config, pool                                            # Engine builder + pooling
from alembic import context                                                               # Alembic migration context
import os                                                                                 # Path utilities
import sys                                                                                # Python path editing

config = context.config                                                                   # Alembic config object

if config.config_file_name is not None:                                                   # If alembic.ini exists
    fileConfig(config.config_file_name)                                                   # Load logging config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))           # Add repo root to import path

from database import Base                                                                 # Import Base from root database.py (your project style)

target_metadata = Base.metadata                                                           # Metadata used for autogenerate

def run_migrations_offline() -> None:                                                     # Offline mode (generate SQL)
    url = config.get_main_option("sqlalchemy.url")                                         # Read URL from alembic.ini
    context.configure(                                                                    # Configure offline context
        url=url,                                                                          # Database URL
        target_metadata=target_metadata,                                                   # Model metadata
        literal_binds=True,                                                               # Render values inline
        dialect_opts={"paramstyle": "named"},                                              # Named params
    )
    with context.begin_transaction():                                                     # Start transaction block
        context.run_migrations()                                                          # Run migrations

def run_migrations_online() -> None:                                                      # Online mode (apply to DB)
    connectable = engine_from_config(                                                     # Build engine from alembic.ini
        config.get_section(config.config_ini_section),                                     # Read config section
        prefix="sqlalchemy.",                                                             # Only sqlalchemy.* keys
        poolclass=pool.NullPool,                                                          # No pooling for migrations
    )
    with connectable.connect() as connection:                                             # Connect to DB
        context.configure(                                                                # Configure online context
            connection=connection,                                                        # Live connection
            target_metadata=target_metadata,                                               # Model metadata
        )
        with context.begin_transaction():                                                 # Start transaction block
            context.run_migrations()                                                      # Run migrations

if context.is_offline_mode():                                                             # If offline
    run_migrations_offline()                                                              # Run offline migrations
else:                                                                                     # Otherwise
    run_migrations_online()                                                               # Run online migrations