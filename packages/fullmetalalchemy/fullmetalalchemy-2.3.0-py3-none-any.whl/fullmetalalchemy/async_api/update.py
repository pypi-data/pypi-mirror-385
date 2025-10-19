"""Async update operations for FullmetalAlchemy.

This module provides async/await versions of update operations.
"""

import typing as _t

import sqlalchemy as _sa
from sqlalchemy.ext.asyncio import AsyncEngine

from fullmetalalchemy._internal import helpers, query_builders, validators
from fullmetalalchemy.types import Record


async def update_records(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[Record],
    engine: _t.Optional[AsyncEngine] = None,
    match_column_names: _t.Optional[_t.Sequence[str]] = None,
) -> None:
    """Update records in table asynchronously.

    Parameters
    ----------
    table : Union[Table, str]
        Table object or table name.
    records : Sequence[Record]
        Records with updated values.
    engine : Optional[AsyncEngine]
        Async database engine.
    match_column_names : Optional[Sequence[str]]
        Column names to match records on. If None, uses primary key.

    Examples
    --------
    >>> import asyncio
    >>> from fullmetalalchemy import async_api
    >>>
    >>> async def main():
    ...     engine = async_api.create_async_engine('sqlite+aiosqlite:///data.db')
    ...     table = await async_api.get_table('users', engine)
    ...     records = [{'id': 1, 'name': 'Alice Updated'}]
    ...     await async_api.update.update_records(table, records, engine)
    >>> asyncio.run(main())
    """
    if isinstance(table, str):
        raise NotImplementedError("String table names require async get_table - coming soon")

    validators.validate_records(records)

    if not records:
        return

    # Determine match columns
    if match_column_names is None:
        match_column_names = helpers.primary_key_names(table)

    if engine is None:
        raise ValueError("engine parameter required for async operations")

    # Build update statements using shared logic
    stmts = query_builders.build_update_stmt_bulk(table, records, match_column_names)

    # Execute async
    async with engine.begin() as conn:
        for stmt in stmts:
            await conn.execute(stmt)


async def update_matching_records(
    table: _t.Union[_sa.Table, str],
    match_records: _t.Sequence[Record],
    update_values: Record,
    engine: _t.Optional[AsyncEngine] = None,
) -> None:
    """Update records matching criteria asynchronously.

    Parameters
    ----------
    table : Union[Table, str]
        Table object or table name.
    match_records : Sequence[Record]
        Records defining match criteria.
    update_values : Record
        Values to update matching records with.
    engine : Optional[AsyncEngine]
        Async database engine.
    """
    if isinstance(table, str):
        raise NotImplementedError("String table names require async get_table - coming soon")

    if engine is None:
        raise ValueError("engine parameter required for async operations")

    async with engine.begin() as conn:
        for match_record in match_records:
            # Build WHERE clause from match record
            where_clause = query_builders.build_where_clause_from_dict(table, match_record)

            # Build and execute update
            stmt = (
                _sa.update(table).where(_sa.sql.elements.and_(*where_clause)).values(update_values)
            )

            await conn.execute(stmt)


async def set_column_values(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    value: _t.Any,
    engine: _t.Optional[AsyncEngine] = None,
) -> None:
    """Set all values in a column asynchronously.

    Parameters
    ----------
    table : Union[Table, str]
        Table object or table name.
    column_name : str
        Column name to update.
    value : Any
        Value to set for all rows.
    engine : Optional[AsyncEngine]
        Async database engine.
    """
    if isinstance(table, str):
        raise NotImplementedError("String table names require async get_table - coming soon")

    if engine is None:
        raise ValueError("engine parameter required for async operations")

    # Build update statement
    stmt = _sa.update(table).values({column_name: value})

    # Execute async
    async with engine.begin() as conn:
        await conn.execute(stmt)
