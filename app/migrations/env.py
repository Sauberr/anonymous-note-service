import sys
import asyncio
from logging.config import fileConfig
from os.path import abspath, dirname

from sqlalchemy.ext.asyncio import create_async_engine

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))

from alembic import context

from app.core.config import settings
from app.core.models.base import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = str(settings.db.url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """Run migrations asynchronously."""
    # Get the database URL from settings
    db_url = str(settings.db.url)

    # Create an async engine
    engine = create_async_engine(db_url)

    # Connect to the database
    async with engine.begin() as connection:
        # Run migrations inside a transaction
        await connection.run_sync(do_run_migrations)

    # Close the engine
    await engine.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Run async migrations in an event loop
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()