"""Async delete operations for FullmetalAlchemy.

This module provides async/await versions of delete operations.
"""

import typing as _t

import sqlalchemy as _sa
from sqlalchemy.ext.asyncio import AsyncEngine

from fullmetalalchemy._internal import query_builders
from fullmetalalchemy.types import Record


async def delete_records(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[Record],
    engine: _t.Optional[AsyncEngine] = None,
) -> None:
    """Delete records from table asynchronously.

    Parameters
    ----------
    table : Union[Table, str]
        Table object or table name.
    records : Sequence[Record]
        Records to delete (matches on all columns).
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
    ...     records = [{'id': 1, 'name': 'Alice'}]
    ...     await async_api.delete.delete_records(table, records, engine)
    >>> asyncio.run(main())
    """
    if isinstance(table, str):
        raise NotImplementedError("String table names require async get_table - coming soon")

    if not records:
        return

    if engine is None:
        raise ValueError("engine parameter required for async operations")

    # Build delete statements using shared logic
    stmts = query_builders.build_delete_stmt_from_records(table, records)

    # Execute async
    async with engine.begin() as conn:
        for stmt in stmts:
            await conn.execute(stmt)


async def delete_records_by_values(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    values: _t.Sequence[_t.Any],
    engine: _t.Optional[AsyncEngine] = None,
) -> None:
    """Delete records matching column values asynchronously.

    Parameters
    ----------
    table : Union[Table, str]
        Table object or table name.
    column_name : str
        Column name to filter on.
    values : Sequence[Any]
        Values to match for deletion.
    engine : Optional[AsyncEngine]
        Async database engine.
    """
    if isinstance(table, str):
        raise NotImplementedError("String table names require async get_table - coming soon")

    if not values:
        return

    if engine is None:
        raise ValueError("engine parameter required for async operations")

    # Build delete statement using shared logic
    stmt = query_builders.build_delete_stmt(table, column_name, values)

    # Execute async
    async with engine.begin() as conn:
        await conn.execute(stmt)


async def delete_all_records(
    table: _t.Union[_sa.Table, str], engine: _t.Optional[AsyncEngine] = None
) -> None:
    """Delete all records from table asynchronously.

    Parameters
    ----------
    table : Union[Table, str]
        Table object or table name.
    engine : Optional[AsyncEngine]
        Async database engine.
    """
    if isinstance(table, str):
        raise NotImplementedError("String table names require async get_table - coming soon")

    if engine is None:
        raise ValueError("engine parameter required for async operations")

    # Build delete all statement
    stmt = _sa.delete(table)

    # Execute async
    async with engine.begin() as conn:
        await conn.execute(stmt)
