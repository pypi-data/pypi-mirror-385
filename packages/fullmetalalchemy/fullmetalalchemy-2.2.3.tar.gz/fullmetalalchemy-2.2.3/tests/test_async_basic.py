"""Basic async functionality tests to verify the async pattern works."""

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine

from fullmetalalchemy import async_api


@pytest.mark.asyncio
async def test_async_imports():
    """Test that async_api can be imported."""
    assert async_api is not None
    assert hasattr(async_api, "select")
    assert hasattr(async_api, "create_async_engine")


@pytest.mark.asyncio
async def test_create_async_engine():
    """Test creating an async engine."""
    engine = async_api.create_async_engine("sqlite+aiosqlite:///:memory:")
    assert engine is not None
    await engine.dispose()


@pytest.mark.asyncio
async def test_async_select_basic():
    """Test basic async select operation."""
    # Create async engine
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    # Create table synchronously for now (will be async later)
    async with engine.begin() as conn:
        await conn.execute(
            sa.text("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                value TEXT
            )
        """)
        )
        await conn.execute(
            sa.text("""
            INSERT INTO test_table (id, value) VALUES (1, 'test')
        """)
        )

    # Get table metadata
    metadata = sa.MetaData()
    async with engine.begin() as conn:
        await conn.run_sync(metadata.reflect)
    table = metadata.tables["test_table"]

    # Test async select
    records = await async_api.select.select_records_all(table, engine)

    assert len(records) == 1
    assert records[0]["id"] == 1
    assert records[0]["value"] == "test"

    await engine.dispose()
