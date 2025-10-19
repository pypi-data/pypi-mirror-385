"""Async drop operations for FullmetalAlchemy.

This module provides async/await versions of drop operations.
"""

import typing as _t

import sqlalchemy as _sa
from sqlalchemy.ext.asyncio import AsyncEngine


async def drop_table(
    table: _t.Union[_sa.Table, str], engine: _t.Optional[AsyncEngine] = None, if_exists: bool = True
) -> None:
    """Drop table asynchronously.

    Parameters
    ----------
    table : Union[Table, str]
        Table object or table name.
    engine : Optional[AsyncEngine]
        Async database engine.
    if_exists : bool
        If True, don't raise error if table doesn't exist.

    Examples
    --------
    >>> import asyncio
    >>> from fullmetalalchemy import async_api
    >>>
    >>> async def main():
    ...     engine = async_api.create_async_engine('sqlite+aiosqlite:///data.db')
    ...     await async_api.drop.drop_table('temp_table', engine, if_exists=True)
    >>> asyncio.run(main())
    """
    if isinstance(table, str):
        # Create metadata and reflect
        metadata = _sa.MetaData()
        if engine is None:
            raise ValueError("engine parameter required when table is a string")

        async with engine.begin() as conn:
            await conn.run_sync(metadata.reflect)

            if table not in metadata.tables:
                if not if_exists:
                    raise ValueError(f"Table '{table}' does not exist")
                return

            table_obj = metadata.tables[table]
            await conn.run_sync(table_obj.drop)
    else:
        if engine is None:
            raise ValueError("engine parameter required for async operations")

        # Drop existing table object
        async with engine.begin() as conn:
            if if_exists:
                # Check if table exists first
                exists = await conn.run_sync(
                    lambda sync_conn: sync_conn.dialect.has_table(sync_conn, table.name)
                )
                if not exists:
                    return

            await conn.run_sync(table.drop)
