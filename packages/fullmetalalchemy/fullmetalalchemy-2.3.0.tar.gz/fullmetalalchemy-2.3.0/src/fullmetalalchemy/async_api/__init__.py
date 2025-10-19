"""Async API for FullmetalAlchemy.

This package provides async/await versions of all FullmetalAlchemy operations
using SQLAlchemy's async engine capabilities.

Usage
-----
```python
import asyncio
from fullmetalalchemy import async_api

async def main():
    engine = async_api.create_async_engine('sqlite+aiosqlite:///data.db')

    # Using AsyncTable class
    table = async_api.AsyncTable('users', engine)
    async with table:
        await table.insert_records([{'id': 1, 'name': 'Alice'}])
        records = await table.select_all()

    # Using AsyncSessionTable for transactions
    async with async_api.AsyncSessionTable('users', engine) as table:
        await table.insert_records([{'id': 2, 'name': 'Bob'}])
        await table.update_records([{'id': 1, 'name': 'Alice Updated'}])
        # Auto-commits on exit

asyncio.run(main())
```

Modules
-------
- select: Async select operations
- insert: Async insert operations
- update: Async update operations
- delete: Async delete operations
- create: Async table creation and create_async_engine
- drop: Async drop operations

Classes
-------
- AsyncTable: Async table operations with array-like access
- AsyncSessionTable: Async transaction management with context manager
"""

from fullmetalalchemy.async_api import batch, create, delete, drop, insert, select, session, update
from fullmetalalchemy.async_api.batch import AsyncBatchProcessor, AsyncBatchResult
from fullmetalalchemy.async_api.sessiontable import AsyncSessionTable
from fullmetalalchemy.async_api.table import AsyncTable

try:
    from sqlalchemy.ext.asyncio import create_async_engine
except ImportError:

    def create_async_engine(*args, **kwargs):  # type: ignore
        raise ImportError(
            "Async support requires SQLAlchemy with asyncio extra. "
            "Install with: pip install 'SQLAlchemy[asyncio]' aiosqlite"
        )


__all__ = [
    "AsyncBatchProcessor",
    "AsyncBatchResult",
    "AsyncSessionTable",
    "AsyncTable",
    "batch",
    "create",
    "create_async_engine",
    "delete",
    "drop",
    "insert",
    "select",
    "session",
    "update",
]
