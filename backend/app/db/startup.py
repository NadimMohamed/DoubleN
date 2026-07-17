"""Startup schema validation.

Verifies that all tables (and critical columns) required by the
application actually exist in the database before FastAPI starts
accepting traffic.

This exists because Alembic migrations run as a separate step in the
Dockerfile CMD (`alembic upgrade head`). If that step fails silently,
or the database is ever reset without resetting `alembic_version`, the
app would otherwise start up "successfully" and then fail on every
request that touches the database (market data -> analysis -> trading
-> positions), producing cascading 503s that are hard to diagnose.

This check is intentionally read-only: it inspects the schema via
SQLAlchemy's `inspect()` API and never creates, alters, or migrates
anything. If the schema is incomplete, it raises so the container
fails fast with a clear log message instead of serving requests
against a broken database.
"""

from __future__ import annotations

from typing import Iterable

import structlog
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncEngine

log = structlog.get_logger(__name__)


# Table name -> columns that must exist on that table.
REQUIRED_TABLES: dict[str, tuple[str, ...]] = {
    "alembic_version": (),
    "users": ("id", "email", "username", "created_at"),
    "positions": ("id", "user_id", "symbol", "status", "side"),
    "notifications": (),
    "exchange_connections": (),
}


class SchemaValidationError(RuntimeError):
    """Raised when the database schema is missing required tables/columns."""


def _inspect_schema(sync_conn) -> tuple[list[str], dict[str, tuple[str, ...]]]:
    """Synchronous helper (run via `run_sync`) that returns the list of
    existing table names and a map of table -> existing column names.
    """
    inspector = inspect(sync_conn)
    table_names = inspector.get_table_names()

    columns_by_table: dict[str, tuple[str, ...]] = {}
    for table in table_names:
        if table in REQUIRED_TABLES:
            columns_by_table[table] = tuple(
                col["name"] for col in inspector.get_columns(table)
            )

    return table_names, columns_by_table


async def verify_schema_on_startup(engine: AsyncEngine) -> None:
    """Verify required tables/columns exist. Raises SchemaValidationError
    (and logs exactly what's missing) if the schema is incomplete.
    """
    missing: list[str] = []
    present: list[str] = []

    async with engine.connect() as conn:
        table_names, columns_by_table = await conn.run_sync(_inspect_schema)

    existing_tables = set(table_names)

    for table, required_columns in REQUIRED_TABLES.items():
        if table not in existing_tables:
            missing.append(f"table '{table}' not found")
            continue

        existing_columns = set(columns_by_table.get(table, ()))
        missing_columns: Iterable[str] = (
            col for col in required_columns if col not in existing_columns
        )
        table_missing_columns = list(missing_columns)
        if table_missing_columns:
            for col in table_missing_columns:
                missing.append(
                    f"column '{col}' not found on table '{table}'"
                )
        else:
            present.append(table)

    if missing:
        log.error(
            "app.startup.schema_validation_failed",
            missing=missing,
        )
        raise SchemaValidationError(
            "Database schema validation failed on startup: "
            + "; ".join(missing)
        )

    summary = ", ".join(f"\u2713 {table}" for table in REQUIRED_TABLES)
    log.info(f"Schema validation: {summary}")
