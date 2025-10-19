"""Async select operations for FullmetalAlchemy.

This module provides async/await versions of all select operations,
using shared query building logic from _internal modules.
"""

import typing as _t

import sqlalchemy as _sa
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from fullmetalalchemy._internal import helpers, query_builders
from fullmetalalchemy.types import Record

AsyncSqlConnection = _t.Union[AsyncEngine, AsyncConnection]


async def select_records_all(
    table: _t.Union[_sa.Table, str],
    engine: _t.Optional[AsyncEngine] = None,
    sorted: bool = False,
    include_columns: _t.Optional[_t.Sequence[str]] = None,
) -> _t.List[Record]:
    """Select all records from table asynchronously.

    Parameters
    ----------
    table : Union[Table, str]
        Table object or table name.
    engine : Optional[AsyncEngine]
        Async database engine.
    sorted : bool
        If True, sort by primary key.
    include_columns : Optional[Sequence[str]]
        If provided, select only these columns.

    Returns
    -------
    List[Record]
        List of records as dictionaries.

    Examples
    --------
    >>> import asyncio
    >>> from fullmetalalchemy import async_api
    >>>
    >>> async def main():
    ...     engine = async_api.create_async_engine('sqlite+aiosqlite:///data.db')
    ...     table = await async_api.get_table('users', engine)
    ...     records = await async_api.select.select_records_all(table, engine)
    ...     print(records)
    >>> asyncio.run(main())
    """
    # TODO: Handle string table names
    if isinstance(table, str):
        raise NotImplementedError("String table names require async get_table - coming soon")

    # Build query using shared logic (no I/O)
    query = query_builders.build_select_all_query(table, sorted, include_columns)

    # Execute async
    if engine is None:
        raise ValueError("engine parameter required for async operations")

    async with engine.begin() as conn:
        result = await conn.execute(query)
        return helpers.process_result_rows(result)


async def select_records_slice(
    table: _t.Union[_sa.Table, str],
    start: _t.Optional[int] = None,
    stop: _t.Optional[int] = None,
    engine: _t.Optional[AsyncEngine] = None,
    sorted: bool = False,
    include_columns: _t.Optional[_t.Sequence[str]] = None,
) -> _t.List[Record]:
    """Select a slice of records asynchronously.

    Parameters
    ----------
    table : Union[Table, str]
        Table object or table name.
    start : Optional[int]
        Start index.
    stop : Optional[int]
        Stop index.
    engine : Optional[AsyncEngine]
        Async database engine.
    sorted : bool
        If True, sort by primary key.
    include_columns : Optional[Sequence[str]]
        If provided, select only these columns.

    Returns
    -------
    List[Record]
        List of records as dictionaries.
    """
    if isinstance(table, str):
        raise NotImplementedError("String table names require async get_table - coming soon")

    # Normalize None values
    if start is None:
        start = 0
    if stop is None:
        # TODO: Get row count async
        stop = 999999  # Large number for now

    # Build query using shared logic
    query = query_builders.build_select_slice_query(table, start, stop, sorted, include_columns)

    if engine is None:
        raise ValueError("engine parameter required for async operations")

    async with engine.begin() as conn:
        result = await conn.execute(query)
        return helpers.process_result_rows(result)


async def select_column_values_all(
    table: _t.Union[_sa.Table, str], column_name: str, engine: _t.Optional[AsyncEngine] = None
) -> _t.List[_t.Any]:
    """Select all values from a column asynchronously.

    Parameters
    ----------
    table : Union[Table, str]
        Table object or table name.
    column_name : str
        Column name to select.
    engine : Optional[AsyncEngine]
        Async database engine.

    Returns
    -------
    List[Any]
        List of column values.
    """
    if isinstance(table, str):
        raise NotImplementedError("String table names require async get_table - coming soon")

    # Build query using shared logic
    query = query_builders.build_select_column_query(table, column_name)

    if engine is None:
        raise ValueError("engine parameter required for async operations")

    async with engine.begin() as conn:
        result = await conn.execute(query)
        return [row[0] for row in result]


async def select_record_by_primary_key(
    table: _t.Union[_sa.Table, str],
    primary_key_value: Record,
    engine: _t.Optional[AsyncEngine] = None,
    include_columns: _t.Optional[_t.Sequence[str]] = None,
) -> Record:
    """Select a single record by primary key asynchronously.

    Parameters
    ----------
    table : Union[Table, str]
        Table object or table name.
    primary_key_value : Record
        Dictionary mapping PK columns to values.
    engine : Optional[AsyncEngine]
        Async database engine.
    include_columns : Optional[Sequence[str]]
        If provided, select only these columns.

    Returns
    -------
    Record
        Single record as dictionary.

    Raises
    ------
    ValueError
        If no record found with given primary key.
    """
    if isinstance(table, str):
        raise NotImplementedError("String table names require async get_table - coming soon")

    # Build query using shared logic
    query = query_builders.build_select_by_primary_key_query(
        table, primary_key_value, include_columns
    )

    if engine is None:
        raise ValueError("engine parameter required for async operations")

    async with engine.begin() as conn:
        result = await conn.execute(query)
        rows = helpers.process_result_rows(result)
        if not rows:
            raise ValueError(f"No record found with primary key: {primary_key_value}")
        return rows[0]
