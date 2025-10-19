"""Async create operations for FullmetalAlchemy.

This module provides async/await versions of table creation operations.
"""

import typing as _t

import sqlalchemy as _sa
from sqlalchemy.ext.asyncio import AsyncEngine

from fullmetalalchemy.types import Record


async def create_table(
    table_name: str,
    column_names: _t.Sequence[str],
    column_types: _t.Sequence[_t.Any],
    primary_key: _t.Optional[_t.Union[str, _t.Sequence[str]]] = None,
    engine: _t.Optional[AsyncEngine] = None,
    if_exists: str = "replace",
) -> _sa.Table:
    """Create a table asynchronously.

    Parameters
    ----------
    table_name : str
        Name of table to create.
    column_names : Sequence[str]
        Column names.
    column_types : Sequence[Any]
        Column types (Python types or SQLAlchemy types).
    primary_key : Optional[Union[str, Sequence[str]]]
        Primary key column name(s).
    engine : Optional[AsyncEngine]
        Async database engine.
    if_exists : str
        Action if table exists: 'replace', 'fail', or 'append'.

    Returns
    -------
    Table
        Created SQLAlchemy Table object.

    Examples
    --------
    >>> import asyncio
    >>> from fullmetalalchemy import async_api
    >>>
    >>> async def main():
    ...     engine = async_api.create_async_engine('sqlite+aiosqlite:///data.db')
    ...     table = await async_api.create.create_table(
    ...         'users',
    ...         ['id', 'name', 'age'],
    ...         [int, str, int],
    ...         primary_key='id',
    ...         engine=engine
    ...     )
    ...     print(f"Created table: {table.name}")
    >>> asyncio.run(main())
    """
    if engine is None:
        raise ValueError("engine parameter required for async operations")

    # Import here to avoid circular imports
    from fullmetalalchemy import type_convert

    # Convert primary key to list
    if primary_key is None:
        pk_list: _t.List[str] = []
    elif isinstance(primary_key, str):
        pk_list = [primary_key]
    else:
        pk_list = list(primary_key)

    # Create metadata
    metadata = _sa.MetaData()

    # Build columns
    columns: _t.List[_sa.Column[_t.Any]] = []
    for col_name, col_type in zip(column_names, column_types):
        # Convert Python type to SQLAlchemy type
        sql_type: _t.Any
        if not isinstance(col_type, _sa.types.TypeEngine):
            # Use the internal type conversion dictionary (returns type class)
            sql_type = type_convert._type_convert[col_type]
        else:
            sql_type = col_type

        # Check if primary key
        is_pk = col_name in pk_list

        columns.append(_sa.Column(col_name, sql_type, primary_key=is_pk))

    # Create table object
    table = _sa.Table(table_name, metadata, *columns)

    # Handle if_exists
    async with engine.begin() as conn:
        # Check if table exists
        exists = await conn.run_sync(
            lambda sync_conn: sync_conn.dialect.has_table(sync_conn, table_name)
        )

        if exists:
            if if_exists == "fail":
                raise ValueError(f"Table '{table_name}' already exists")
            elif if_exists == "replace":
                # Drop existing table
                await conn.run_sync(table.drop)
            elif if_exists == "append":
                # Reflect existing table
                await conn.run_sync(metadata.reflect)
                return metadata.tables[table_name]

        # Create table
        await conn.run_sync(metadata.create_all)

    return table


async def create_table_from_records(
    table_name: str,
    records: _t.Sequence[Record],
    primary_key: _t.Optional[_t.Union[str, _t.Sequence[str]]] = None,
    engine: _t.Optional[AsyncEngine] = None,
    if_exists: str = "replace",
) -> _sa.Table:
    """Create table from records asynchronously.

    Parameters
    ----------
    table_name : str
        Name of table to create.
    records : Sequence[Record]
        Records to infer schema from and insert.
    primary_key : Optional[Union[str, Sequence[str]]]
        Primary key column name(s).
    engine : Optional[AsyncEngine]
        Async database engine.
    if_exists : str
        Action if table exists: 'replace', 'fail', or 'append'.

    Returns
    -------
    Table
        Created SQLAlchemy Table object.
    """
    if not records:
        raise ValueError("Cannot create table from empty records list")

    # Import here to avoid circular imports
    from fullmetalalchemy import create as sync_create
    from fullmetalalchemy.async_api import insert

    # Use sync version's helper to infer schema
    # Group records by column
    column_names = list(records[0].keys())

    # Collect all values for each column
    column_data = {col: [r[col] for r in records] for col in column_names}

    # Infer types using sync helper
    column_types = [sync_create._column_datatype(column_data[col]) for col in column_names]

    # Create table
    table = await create_table(
        table_name, column_names, column_types, primary_key, engine, if_exists
    )

    # Insert records
    await insert.insert_records(table, records, engine)

    return table


async def copy_table(
    source_table: _t.Union[_sa.Table, str],
    dest_table_name: str,
    engine: _t.Optional[AsyncEngine] = None,
    if_exists: str = "replace",
) -> _sa.Table:
    """Copy table structure and data asynchronously.

    Parameters
    ----------
    source_table : Union[Table, str]
        Source table to copy from.
    dest_table_name : str
        Name for destination table.
    engine : Optional[AsyncEngine]
        Async database engine.
    if_exists : str
        Action if destination table exists.

    Returns
    -------
    Table
        Copied SQLAlchemy Table object.
    """
    if isinstance(source_table, str):
        raise NotImplementedError("String table names require async get_table - coming soon")

    if engine is None:
        raise ValueError("engine parameter required for async operations")

    # Create new table with same structure
    metadata = _sa.MetaData()

    # Copy column definitions
    columns = []
    for col in source_table.columns:
        columns.append(col.copy())

    dest_table = _sa.Table(dest_table_name, metadata, *columns)

    # Handle if_exists
    async with engine.begin() as conn:
        exists = await conn.run_sync(
            lambda sync_conn: sync_conn.dialect.has_table(sync_conn, dest_table_name)
        )

        if exists:
            if if_exists == "fail":
                raise ValueError(f"Table '{dest_table_name}' already exists")
            elif if_exists == "replace":
                await conn.run_sync(dest_table.drop)

        # Create destination table
        await conn.run_sync(metadata.create_all)

        # Copy data
        insert_stmt = dest_table.insert().from_select(
            source_table.columns.keys(), _sa.select(source_table)
        )
        await conn.execute(insert_stmt)

    return dest_table
