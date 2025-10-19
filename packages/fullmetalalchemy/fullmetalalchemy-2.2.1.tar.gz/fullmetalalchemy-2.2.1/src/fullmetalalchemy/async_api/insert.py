"""Async insert operations for FullmetalAlchemy.

This module provides async/await versions of insert operations.
"""

import typing as _t

import sqlalchemy as _sa
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from fullmetalalchemy._internal import query_builders, validators
from fullmetalalchemy.types import Record


async def insert_records(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[Record],
    engine: _t.Optional[AsyncEngine] = None,
) -> None:
    """Insert records into table asynchronously.

    Parameters
    ----------
    table : Union[Table, str]
        Table object or table name.
    records : Sequence[Record]
        Records to insert.
    engine : Optional[AsyncEngine]
        Async database engine.

    Examples
    --------
    >>> import asyncio
    >>> from fullmetalalchemy import async_api
    >>>
    >>> async def main():
    ...     engine = async_api.create_async_engine('sqlite+aiosqlite:///data.db')
    ...     table = await async_api.get_table('users', engine)
    ...     records = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
    ...     await async_api.insert.insert_records(table, records, engine)
    >>> asyncio.run(main())
    """
    if isinstance(table, str):
        raise NotImplementedError("String table names require async get_table - coming soon")

    # Validate input
    validators.validate_records(records)

    if not records:
        return

    # Build insert statement using shared logic
    stmt = query_builders.build_insert_stmt(table, records)

    if engine is None:
        raise ValueError("engine parameter required for async operations")

    # Execute async
    async with engine.begin() as conn:
        await conn.execute(stmt)


async def insert_from_table(
    source_table: _t.Union[_sa.Table, str],
    dest_table: _t.Union[_sa.Table, str],
    engine: _t.Optional[AsyncEngine] = None,
) -> None:
    """Insert records from one table to another asynchronously.

    Parameters
    ----------
    source_table : Union[Table, str]
        Source table to copy from.
    dest_table : Union[Table, str]
        Destination table to insert into.
    engine : Optional[AsyncEngine]
        Async database engine.
    """
    if isinstance(source_table, str) or isinstance(dest_table, str):
        raise NotImplementedError("String table names require async get_table - coming soon")

    if engine is None:
        raise ValueError("engine parameter required for async operations")

    # Build insert from select statement
    stmt = dest_table.insert().from_select(source_table.columns.keys(), _sa.select(source_table))

    # Execute async
    async with engine.begin() as conn:
        await conn.execute(stmt)


async def insert_records_bulk(
    table: _t.Union[_sa.Table, str], records: _t.Sequence[Record], session: AsyncSession
) -> None:
    """Insert records using bulk insert with async session.

    Parameters
    ----------
    table : Union[Table, str]
        Table object or table name.
    records : Sequence[Record]
        Records to insert.
    session : AsyncSession
        Async SQLAlchemy session.
    """
    if isinstance(table, str):
        raise NotImplementedError("String table names require async get_table - coming soon")

    validators.validate_records(records)

    if not records:
        return

    # Build insert statement using shared logic
    stmt = query_builders.build_insert_stmt(table, records)

    # Execute with session
    await session.execute(stmt)
