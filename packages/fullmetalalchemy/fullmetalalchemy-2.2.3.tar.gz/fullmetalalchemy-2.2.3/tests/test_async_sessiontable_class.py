"""Tests for AsyncSessionTable class."""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

# Handle SQLAlchemy 1.4 vs 2.0 async session creation
try:
    from sqlalchemy.ext.asyncio import async_sessionmaker
except ImportError:
    # SQLAlchemy 1.4 doesn't have async_sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker

    def async_sessionmaker(engine, **kwargs):  # type: ignore
        return sessionmaker(engine, class_=AsyncSession, **kwargs)


from fullmetalalchemy.async_api import AsyncSessionTable, create


@pytest.fixture
async def async_engine_with_data():
    """Create async engine with test data."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    # Create table with data
    await create.create_table_from_records(
        "test_table",
        [
            {"id": 1, "name": "Alice", "value": 100},
            {"id": 2, "name": "Bob", "value": 200},
            {"id": 3, "name": "Charlie", "value": 300},
        ],
        primary_key="id",
        engine=engine,
    )

    yield engine
    await engine.dispose()


# Basic Operations


@pytest.mark.asyncio
async def test_async_sessiontable_init_with_engine(async_engine_with_data):
    """Test AsyncSessionTable initialization with engine."""
    table = AsyncSessionTable("test_table", async_engine_with_data)
    assert table.name == "test_table"
    assert table.engine == async_engine_with_data
    assert table._owns_session is True


@pytest.mark.asyncio
async def test_async_sessiontable_init_with_session(async_engine_with_data):
    """Test AsyncSessionTable initialization with session."""
    session_maker = async_sessionmaker(async_engine_with_data)
    session = session_maker()

    table = AsyncSessionTable("test_table", session)
    assert table.name == "test_table"
    assert table.session == session
    assert table._owns_session is False

    await session.close()


@pytest.mark.asyncio
async def test_async_sessiontable_repr(async_engine_with_data):
    """Test AsyncSessionTable repr."""
    table = AsyncSessionTable("test_table", async_engine_with_data)
    async with table:
        repr_str = repr(table)
        assert "AsyncSessionTable" in repr_str
        assert "test_table" in repr_str


# Context Manager


@pytest.mark.asyncio
async def test_async_sessiontable_context_manager_success(async_engine_with_data):
    """Test AsyncSessionTable context manager commits on success."""
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        await table.insert_records([{"id": 4, "name": "Diana", "value": 400}])

    # Verify changes were committed
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        records = await table.select_all()
        assert len(records) == 4
        assert any(r["name"] == "Diana" for r in records)


@pytest.mark.asyncio
async def test_async_sessiontable_context_manager_rollback(async_engine_with_data):
    """Test AsyncSessionTable context manager rolls back on error."""
    try:
        async with AsyncSessionTable("test_table", async_engine_with_data) as table:
            await table.insert_records([{"id": 5, "name": "Eve", "value": 500}])
            raise ValueError("Test error")
    except ValueError:
        pass

    # Verify changes were rolled back
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        records = await table.select_all()
        assert len(records) == 3  # Original count
        assert not any(r["name"] == "Eve" for r in records)


@pytest.mark.asyncio
async def test_async_sessiontable_manual_commit(async_engine_with_data):
    """Test AsyncSessionTable manual commit."""
    table = AsyncSessionTable("test_table", async_engine_with_data)
    await table._get_table()

    await table.insert_records([{"id": 6, "name": "Frank", "value": 600}])
    await table.commit()

    # Verify
    async with AsyncSessionTable("test_table", async_engine_with_data) as table2:
        records = await table2.select_all()
        assert any(r["name"] == "Frank" for r in records)


@pytest.mark.asyncio
async def test_async_sessiontable_manual_rollback(async_engine_with_data):
    """Test AsyncSessionTable manual rollback."""
    table = AsyncSessionTable("test_table", async_engine_with_data)
    await table._get_table()

    await table.insert_records([{"id": 7, "name": "Grace", "value": 700}])
    await table.rollback()

    # Verify changes were rolled back
    async with AsyncSessionTable("test_table", async_engine_with_data) as table2:
        records = await table2.select_all()
        assert not any(r["name"] == "Grace" for r in records)


# CRUD Operations


@pytest.mark.asyncio
async def test_async_sessiontable_insert(async_engine_with_data):
    """Test AsyncSessionTable insert_records."""
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        await table.insert_records([{"id": 8, "name": "Henry", "value": 800}])

    # Verify committed
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        records = await table.select_all()
        assert any(r["name"] == "Henry" for r in records)


@pytest.mark.asyncio
async def test_async_sessiontable_update(async_engine_with_data):
    """Test AsyncSessionTable update_records."""
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        await table.update_records([{"id": 2, "name": "Bob Updated", "value": 250}])

    # Verify
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        record = await table.select_record_by_primary_key({"id": 2})
        assert record["name"] == "Bob Updated"


@pytest.mark.asyncio
async def test_async_sessiontable_update_matching_records(async_engine_with_data):
    """Test AsyncSessionTable update_matching_records."""
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        await table.update_matching_records([{"value": 100}], {"value": 999})

    # Verify
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        records = await table.select_all()
        assert any(r["value"] == 999 for r in records)


@pytest.mark.asyncio
async def test_async_sessiontable_delete(async_engine_with_data):
    """Test AsyncSessionTable delete_records."""
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        await table.delete_records("id", [1, 3])

    # Verify
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        records = await table.select_all()
        assert len(records) == 1
        assert records[0]["name"] == "Bob"


@pytest.mark.asyncio
async def test_async_sessiontable_delete_by_values(async_engine_with_data):
    """Test AsyncSessionTable delete_records_by_values."""
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        await table.delete_records_by_values([{"id": 2, "name": "Bob", "value": 200}])

    # Verify
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        records = await table.select_all()
        assert len(records) == 2
        assert not any(r["name"] == "Bob" for r in records)


# Select Operations


@pytest.mark.asyncio
async def test_async_sessiontable_select_all(async_engine_with_data):
    """Test AsyncSessionTable select_all."""
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        records = await table.select_all()
        assert len(records) == 3


@pytest.mark.asyncio
async def test_async_sessiontable_select_slice(async_engine_with_data):
    """Test AsyncSessionTable select_records_slice."""
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        records = await table.select_records_slice(0, 2, sorted=True)
        assert len(records) == 2
        assert records[0]["id"] == 1


@pytest.mark.asyncio
async def test_async_sessiontable_select_column_values(async_engine_with_data):
    """Test AsyncSessionTable select_column_values_all."""
    async with AsyncSessionTable("test_table", async_engine_with_data) as table:
        names = await table.select_column_values_all("name")
        assert len(names) == 3
        assert "Alice" in names
