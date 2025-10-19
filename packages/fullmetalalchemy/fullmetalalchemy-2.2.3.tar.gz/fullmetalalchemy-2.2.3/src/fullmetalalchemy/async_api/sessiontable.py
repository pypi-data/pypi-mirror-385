"""AsyncSessionTable class for async transaction-safe operations."""

from __future__ import annotations

import typing as _t

import sqlalchemy as _sa
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

# Handle SQLAlchemy 1.4 vs 2.0+ async session creation
try:
    from sqlalchemy.ext.asyncio import async_sessionmaker

    SQLALCHEMY_20_PLUS = True
except ImportError:
    # SQLAlchemy 1.4 doesn't have async_sessionmaker
    SQLALCHEMY_20_PLUS = False
    from sqlalchemy.orm import sessionmaker

    # Create a wrapper for SQLAlchemy 1.4
    def async_sessionmaker(engine, **kwargs):  # type: ignore
        return sessionmaker(engine, class_=AsyncSession, **kwargs)


from fullmetalalchemy.types import Record


class AsyncSessionTable:
    """
    Async class for session-based table operations.
    Methods add changes to session.
    Call commit method to commit all changes added to session.
    Call rollback method to reverse all changes added to session.
    Use context manager to automatically commit/rollback.

    Examples
    --------
    >>> import asyncio
    >>> from fullmetalalchemy.async_api.sessiontable import AsyncSessionTable
    >>>
    >>> async def main():
    ...     engine = create_async_engine('sqlite+aiosqlite:///data.db')
    ...     table = AsyncSessionTable('xy', engine)
    ...     await table.insert_records([{'id': 5, 'x': 5, 'y': 9}])
    ...     await table.update_records([{'id': 2, 'x': 33, 'y': 8}])
    ...     await table.commit()
    >>>
    >>> # Same but using context manager
    >>> async def main_with_context():
    ...     engine = create_async_engine('sqlite+aiosqlite:///data.db')
    ...     async with AsyncSessionTable('xy', engine) as table:
    ...         await table.insert_records([{'id': 5, 'x': 5, 'y': 9}])
    ...         await table.update_records([{'id': 2, 'x': 33, 'y': 8}])
    ...         # Auto-commits on exit, rolls back on exception
    """

    def __init__(
        self,
        name: str,
        engine: _t.Union[AsyncEngine, AsyncSession],
        schema: _t.Optional[str] = None,
    ) -> None:
        """
        Initialize AsyncSessionTable.

        Parameters
        ----------
        name : str
            Table name
        engine : Union[AsyncEngine, AsyncSession]
            Async database engine or session
        schema : Optional[str]
            Schema name (default None)
        """
        self.name = name
        self.schema = schema
        self._owns_session = False

        if isinstance(engine, AsyncSession):
            self.session = engine
            # Try to get the async engine from session
            bind = engine.get_bind()
            # The bind might be AsyncEngine, AsyncConnection, or None
            if bind is None:
                raise TypeError("AsyncSession is not bound to an engine")
            # For AsyncConnection, get its engine
            if hasattr(bind, "engine"):
                self.engine: AsyncEngine = bind.engine  # type: ignore
            elif isinstance(bind, AsyncEngine):
                self.engine = bind
            else:
                # Fallback: assume bind is usable as engine
                self.engine = bind  # type: ignore
        elif isinstance(engine, AsyncEngine):
            self.engine = engine
            session_maker = async_sessionmaker(engine, expire_on_commit=False)
            self.session = session_maker()
            self._owns_session = True
        else:
            raise TypeError("engine must be AsyncEngine or AsyncSession")

        self._table: _t.Optional[_sa.Table] = None

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
    def column_names(self) -> _t.List[str]:
        """Get column names (requires table to be loaded)."""
        if self._table is None:
            raise RuntimeError("Table metadata not loaded. Use async context manager first")
        return [col.name for col in self._table.columns]

    @property
    def primary_key_names(self) -> _t.List[str]:
        """Get primary key column names (requires table to be loaded)."""
        if self._table is None:
            raise RuntimeError("Table metadata not loaded. Use async context manager first")
        return [col.name for col in self._table.primary_key]

    @property
    def column_types(self) -> _t.List[type]:
        """Get column types (requires table to be loaded)."""
        if self._table is None:
            raise RuntimeError("Table metadata not loaded. Use async context manager first")
        return [type(col.type) for col in self._table.columns]

    def __repr__(self) -> str:
        if self._table is None:
            return f"AsyncSessionTable(name={self.name}, schema={self.schema})"
        return (
            f"AsyncSessionTable(name={self.name}, columns={self.column_names}, "
            f"pks={self.primary_key_names}, types={self.column_types})"
        )

    async def __aenter__(self) -> AsyncSessionTable:
        """Enter async context manager."""
        await self._get_table()
        return self

    async def __aexit__(
        self,
        exc_type: _t.Optional[_t.Type[BaseException]],
        exc_val: _t.Optional[BaseException],
        exc_tb: _t.Optional[_t.Any],
    ) -> None:
        """Exit async context manager - commit on success, rollback on error."""
        try:
            if exc_type is not None:
                await self.rollback()
            else:
                await self.commit()
        finally:
            if self._owns_session:
                await self.session.close()

    async def commit(self) -> None:
        """Commit all changes in the session."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback all changes in the session."""
        await self.session.rollback()

    # CRUD Operations - all use session

    async def insert_records(self, records: _t.Sequence[Record]) -> None:
        """Insert records into table (adds to session, doesn't commit)."""
        table = await self._get_table()
        # Insert using session
        for record in records:
            stmt = table.insert().values(record)
            await self.session.execute(stmt)

    async def insert_from_table(self, source_table: _sa.Table) -> None:
        """Insert records from another table (adds to session)."""
        table = await self._get_table()
        stmt = table.insert().from_select(source_table.columns.keys(), _sa.select(source_table))
        await self.session.execute(stmt)

    async def update_records(
        self, records: _t.Sequence[Record], match_column_names: _t.Optional[_t.Sequence[str]] = None
    ) -> None:
        """Update records in table (adds to session)."""
        table = await self._get_table()

        if match_column_names is None:
            match_column_names = self.primary_key_names

        for record in records:
            where_conditions = []
            update_values = {}

            for key, value in record.items():
                if key in match_column_names:
                    where_conditions.append(table.c[key] == value)
                else:
                    update_values[key] = value

            if where_conditions and update_values:
                stmt = _sa.update(table).where(_sa.and_(*where_conditions)).values(update_values)
                await self.session.execute(stmt)

    async def update_matching_records(
        self, match_records: _t.Sequence[Record], update_values: Record
    ) -> None:
        """Update records matching criteria (adds to session)."""
        table = await self._get_table()

        for match_record in match_records:
            where_conditions = [table.c[key] == value for key, value in match_record.items()]

            if where_conditions:
                stmt = _sa.update(table).where(_sa.and_(*where_conditions)).values(update_values)
                await self.session.execute(stmt)

    async def set_column_values(self, column_name: str, value: _t.Any) -> None:
        """Set all values in a column (adds to session)."""
        table = await self._get_table()
        stmt = _sa.update(table).values({column_name: value})
        await self.session.execute(stmt)

    async def delete_records(self, column_name: str, values: _t.Sequence[_t.Any]) -> None:
        """Delete records by column values (adds to session)."""
        table = await self._get_table()
        stmt = _sa.delete(table).where(table.c[column_name].in_(values))
        await self.session.execute(stmt)

    async def delete_records_by_values(self, records: _t.Sequence[Record]) -> None:
        """Delete records matching all column values (adds to session)."""
        table = await self._get_table()

        for record in records:
            where_conditions = [table.c[key] == value for key, value in record.items()]
            if where_conditions:
                stmt = _sa.delete(table).where(_sa.and_(*where_conditions))
                await self.session.execute(stmt)

    async def delete_all_records(self) -> None:
        """Delete all records from table (adds to session)."""
        table = await self._get_table()
        stmt = _sa.delete(table)
        await self.session.execute(stmt)

    # Select Operations - read-only, no session changes

    async def select_all(self) -> _t.List[Record]:
        """Select all records."""
        table = await self._get_table()
        result = await self.session.execute(_sa.select(table))
        return [dict(row._mapping) for row in result]

    async def select_records_all(
        self, sorted: bool = False, include_columns: _t.Optional[_t.Sequence[str]] = None
    ) -> _t.List[Record]:
        """Select all records with options."""
        table = await self._get_table()

        if include_columns is not None:
            columns = [table.c[col] for col in include_columns]
            query = _sa.select(*columns)
        else:
            query = _sa.select(table)

        if sorted:
            pk_cols = [table.c[pk] for pk in self.primary_key_names]
            query = query.order_by(*pk_cols)

        result = await self.session.execute(query)
        return [dict(row._mapping) for row in result]

    async def select_records_slice(
        self,
        start: _t.Optional[int] = None,
        stop: _t.Optional[int] = None,
        sorted: bool = False,
        include_columns: _t.Optional[_t.Sequence[str]] = None,
    ) -> _t.List[Record]:
        """Select records slice."""
        table = await self._get_table()

        if include_columns is not None:
            columns = [table.c[col] for col in include_columns]
            query = _sa.select(*columns)
        else:
            query = _sa.select(table)

        if sorted:
            pk_cols = [table.c[pk] for pk in self.primary_key_names]
            query = query.order_by(*pk_cols)

        if start is None:
            start = 0
        if stop is not None:
            query = query.slice(start, stop)
        else:
            query = query.offset(start)

        result = await self.session.execute(query)
        return [dict(row._mapping) for row in result]

    async def select_record_by_primary_key(
        self, primary_key_value: Record, include_columns: _t.Optional[_t.Sequence[str]] = None
    ) -> Record:
        """Select record by primary key."""
        table = await self._get_table()

        if include_columns is not None:
            columns = [table.c[col] for col in include_columns]
            query = _sa.select(*columns)
        else:
            query = _sa.select(table)

        where_conditions = [table.c[key] == value for key, value in primary_key_value.items()]
        query = query.where(_sa.and_(*where_conditions))

        result = await self.session.execute(query)
        row = result.first()
        if row is None:
            raise ValueError(f"No record found with primary key: {primary_key_value}")
        return dict(row._mapping)

    async def select_column_values_all(self, column_name: str) -> _t.List[_t.Any]:
        """Get all values from a column."""
        table = await self._get_table()
        query = _sa.select(table.c[column_name])
        result = await self.session.execute(query)
        return [row[0] for row in result]
