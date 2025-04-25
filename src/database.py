from typing import Any

from sqlalchemy import (
    Column,
    CursorResult,
    Float,
    Insert,
    Integer,
    MetaData,
    Select,
    String,
    Table,
    Update,
)
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from src.config import settings
from src.constants import DB_NAMING_CONVENTION

DATABASE_URL = str(settings.DATABASE_ASYNC_URL)

engine = create_async_engine(
    DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    pool_recycle=settings.DATABASE_POOL_TTL,
    pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)


cars = Table(
    "cars",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("brand", String(50), nullable=False),
    Column("model", String(50), nullable=False),
    Column("year", Integer, nullable=False),
    Column("engine", String(20), nullable=True),
    Column("fuel_type", String(20), nullable=True),
    Column("color", String(30), nullable=True),
    Column("mileage", Integer, nullable=True),
    Column("doors", Integer, nullable=True),
    Column("transmission", String(20), nullable=True),
    Column("price", Float, nullable=True),
)


async def fetch_one(
    select_query: Select | Insert | Update,
    connection: AsyncConnection | None = None,
    commit_after: bool = False,
) -> dict[str, Any] | None:
    if not connection:
        async with engine.connect() as connection:
            cursor = await _execute_query(select_query, connection, commit_after)
            return cursor.first()._asdict() if cursor.rowcount > 0 else None

    cursor = await _execute_query(select_query, connection, commit_after)
    return cursor.first()._asdict() if cursor.rowcount > 0 else None


async def fetch_all(
    select_query: Select | Insert | Update,
    connection: AsyncConnection | None = None,
    commit_after: bool = False,
) -> list[dict[str, Any]]:
    if not connection:
        async with engine.connect() as connection:
            cursor = await _execute_query(select_query, connection, commit_after)
            return [r._asdict() for r in cursor.all()]

    cursor = await _execute_query(select_query, connection, commit_after)
    return [r._asdict() for r in cursor.all()]


async def execute(
    query: Insert | Update,
    connection: AsyncConnection = None,
    commit_after: bool = False,
) -> None:
    if not connection:
        async with engine.connect() as connection:
            await _execute_query(query, connection, commit_after)
            return

    await _execute_query(query, connection, commit_after)


async def _execute_query(
    query: Select | Insert | Update,
    connection: AsyncConnection,
    commit_after: bool = False,
) -> CursorResult:
    result = await connection.execute(query)
    if commit_after:
        await connection.commit()

    return result


async def get_db_connection() -> AsyncConnection:
    connection = await engine.connect()
    try:
        yield connection
    finally:
        await connection.close()
