"""AsyncTable class for async table operations."""

from __future__ import annotations

import typing as _t

import sqlalchemy as _sa
from sqlalchemy.ext.asyncio import AsyncEngine

from fullmetalalchemy import async_api
from fullmetalalchemy.types import Record


class AsyncTable:
    """
    Async class that combines all fullmetalalchemy async table functions.
    Methods change SQL table asynchronously.

    Example
    -------
    >>> import asyncio
    >>> from fullmetalalchemy.async_api.table import AsyncTable
    >>>
    >>> async def main():
    ...     engine = create_async_engine('sqlite+aiosqlite:///data.db')
    ...     table = AsyncTable('xy', engine)
    ...     await table.insert_records([{'id': 5, 'x': 5, 'y': 9}])
    ...     await table.update_records([{'id': 2, 'x': 33, 'y': 8}])
    >>> asyncio.run(main())
    """

    def __init__(self, name: str, engine: AsyncEngine, schema: _t.Optional[str] = None) -> None:
        """
        Initialize AsyncTable.

        Parameters
        ----------
        name : str
            Table name
        engine : AsyncEngine
            Async database engine
        schema : Optional[str]
            Schema name (default None)
        """
        self.name = name
        self.engine = engine
        self.schema = schema
        self._table: _t.Optional[_sa.Table] = None
        self._row_count_cache: _t.Optional[int] = None

    async def _get_table(self) -> _sa.Table:
        """Get or create table metadata object."""
        if self._table is None:
            # Reflect table metadata
            metadata = _sa.MetaData()
            async with self.engine.begin() as conn:
                await conn.run_sync(
                    lambda sync_conn: metadata.reflect(bind=sync_conn, schema=self.schema)
                )
            table_key = f"{self.schema}.{self.name}" if self.schema else self.name
            self._table = metadata.tables[table_key]
        return self._table

    @property
    async def sa_table(self) -> _sa.Table:
        """Get SQLAlchemy Table object."""
        return await self._get_table()

    @property
    def column_names(self) -> _t.List[str]:
        """Get column names (requires table to be loaded)."""
        if self._table is None:
            raise RuntimeError("Table metadata not loaded. Call await table._get_table() first")
        return [col.name for col in self._table.columns]

    @property
    def primary_key_names(self) -> _t.List[str]:
        """Get primary key column names (requires table to be loaded)."""
        if self._table is None:
            raise RuntimeError("Table metadata not loaded. Call await table._get_table() first")
        return [col.name for col in self._table.primary_key]

    @property
    def column_types(self) -> _t.List[type]:
        """Get column types (requires table to be loaded)."""
        if self._table is None:
            raise RuntimeError("Table metadata not loaded. Call await table._get_table() first")
        return [type(col.type) for col in self._table.columns]

    def __repr__(self) -> str:
        if self._table is None:
            return f"AsyncTable(name={self.name}, schema={self.schema})"
        return (
            f"AsyncTable(name={self.name}, columns={self.column_names}, "
            f"pks={self.primary_key_names}, types={self.column_types})"
        )

    async def __aenter__(self) -> AsyncTable:
        """Enter async context manager."""
        await self._get_table()
        return self

    async def __aexit__(
        self,
        exc_type: _t.Optional[_t.Type[BaseException]],
        exc_val: _t.Optional[BaseException],
        exc_tb: _t.Optional[_t.Any],
    ) -> None:
        """Exit async context manager."""
        pass

    async def __len__(self) -> int:
        """Get row count."""
        table = await self._get_table()
        async with self.engine.begin() as conn:
            result = await conn.execute(_sa.select(_sa.func.count()).select_from(table))
            row = result.first()
            return row[0] if row else 0

    def __getitem__(
        self, key: _t.Union[int, str, slice]
    ) -> _t.Coroutine[_t.Any, _t.Any, _t.Union[Record, _t.List[_t.Any]]]:
        """
        Get records based on key type.

        Returns a coroutine that must be awaited.

        Parameters
        ----------
        key : Union[int, str, slice]
            - int: Get record at index
            - str: Get all values for column
            - slice: Get records slice

        Returns
        -------
        Coroutine
            Awaitable that returns record(s) or column values

        Examples
        --------
        >>> record = await table[0]
        >>> column_values = await table['name']
        >>> records_slice = await table[0:10]
        """
        if isinstance(key, int):
            return self.select_record_by_index(key)
        elif isinstance(key, str):
            return self.select_column_values_all(key)
        elif isinstance(key, slice):
            return self.select_records_slice(key.start, key.stop)
        else:
            raise TypeError(f"indices must be int, str, or slice, not {type(key).__name__}")

    async def __aiter__(self) -> _t.AsyncIterator[Record]:
        """Iterate over all records asynchronously."""
        table = await self._get_table()
        records = await async_api.select.select_records_all(table, self.engine)
        for record in records:
            yield record

    # CRUD Operations

    async def insert_records(self, records: _t.Sequence[Record]) -> None:
        """Insert records into table."""
        table = await self._get_table()
        await async_api.insert.insert_records(table, records, self.engine)
        self._row_count_cache = None

    async def insert_from_table(self, source_table: _sa.Table) -> None:
        """Insert records from another table."""
        table = await self._get_table()
        await async_api.insert.insert_from_table(source_table, table, self.engine)
        self._row_count_cache = None

    async def update_records(
        self, records: _t.Sequence[Record], match_column_names: _t.Optional[_t.Sequence[str]] = None
    ) -> None:
        """Update records in table."""
        table = await self._get_table()
        await async_api.update.update_records(table, records, self.engine, match_column_names)

    async def update_matching_records(
        self, match_records: _t.Sequence[Record], update_values: Record
    ) -> None:
        """Update records matching criteria."""
        table = await self._get_table()
        await async_api.update.update_matching_records(
            table, match_records, update_values, self.engine
        )

    async def set_column_values(self, column_name: str, value: _t.Any) -> None:
        """Set all values in a column."""
        table = await self._get_table()
        await async_api.update.set_column_values(table, column_name, value, self.engine)

    async def delete_records(self, column_name: str, values: _t.Sequence[_t.Any]) -> None:
        """Delete records by column values."""
        table = await self._get_table()
        await async_api.delete.delete_records_by_values(table, column_name, values, self.engine)
        self._row_count_cache = None

    async def delete_records_by_values(self, records: _t.Sequence[Record]) -> None:
        """Delete records matching all column values."""
        table = await self._get_table()
        await async_api.delete.delete_records(table, records, self.engine)
        self._row_count_cache = None

    async def delete_all_records(self) -> None:
        """Delete all records from table."""
        table = await self._get_table()
        await async_api.delete.delete_all_records(table, self.engine)
        self._row_count_cache = None

    async def drop(self, if_exists: bool = True) -> None:
        """Drop the table."""
        table = await self._get_table()
        await async_api.drop.drop_table(table, self.engine, if_exists)
        self._table = None
        self._row_count_cache = None

    # Select Operations

    async def select_all(self) -> _t.List[Record]:
        """Select all records."""
        table = await self._get_table()
        return await async_api.select.select_records_all(table, self.engine)

    async def select_records_all(
        self, sorted: bool = False, include_columns: _t.Optional[_t.Sequence[str]] = None
    ) -> _t.List[Record]:
        """Select all records with options."""
        table = await self._get_table()
        return await async_api.select.select_records_all(
            table, self.engine, sorted, include_columns
        )

    async def select_records_slice(
        self,
        start: _t.Optional[int] = None,
        stop: _t.Optional[int] = None,
        sorted: bool = False,
        include_columns: _t.Optional[_t.Sequence[str]] = None,
    ) -> _t.List[Record]:
        """Select records slice."""
        table = await self._get_table()
        return await async_api.select.select_records_slice(
            table, start, stop, self.engine, sorted, include_columns
        )

    async def select_record_by_index(self, index: int) -> Record:
        """Select single record by index."""
        records = await self.select_records_slice(index, index + 1)
        if not records:
            raise IndexError(f"Record index {index} out of range")
        return records[0]

    async def select_record_by_primary_key(
        self, primary_key_value: Record, include_columns: _t.Optional[_t.Sequence[str]] = None
    ) -> Record:
        """Select record by primary key."""
        table = await self._get_table()
        return await async_api.select.select_record_by_primary_key(
            table, primary_key_value, self.engine, include_columns
        )

    async def select_column_values_all(self, column_name: str) -> _t.List[_t.Any]:
        """Get all values from a column."""
        table = await self._get_table()
        return await async_api.select.select_column_values_all(table, column_name, self.engine)
