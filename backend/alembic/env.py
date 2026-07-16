import asyncio
from logging.config import fileConfig
from sqlalchemy import inspect, pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.core.config import settings
from app.db.session import Base
import app.models  # noqa: F401 — ensures all models are imported for autogenerate

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def _clear_stale_version_record(connection: Connection) -> None:
    """Remove the stale alembic_version row left over from the old,
    overly-long '003_add_exchange_connections_table' revision id.

    That revision was renamed to '003_exchanges' to avoid overflowing
    the alembic_version.version_num column, but any database that had
    already run the old migration will still have the old id stored.
    If left in place, Alembic won't recognize it as a known revision
    and migrations will fail before they even start.
    """
    inspector = inspect(connection)
    if "alembic_version" not in inspector.get_table_names():
        return

    connection.execute(
        text("DELETE FROM alembic_version WHERE version_num = :version_num"),
        {"version_num": "003_add_exchange_connections_table"},
    )


def do_run_migrations(connection: Connection) -> None:
    _clear_stale_version_record(connection)
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
