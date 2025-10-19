"""Tests for AsyncTable class."""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from fullmetalalchemy.async_api import AsyncTable, create


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
async def test_async_table_init(async_engine_with_data):
    """Test AsyncTable initialization."""
    table = AsyncTable("test_table", async_engine_with_data)
    assert table.name == "test_table"
    assert table.engine == async_engine_with_data


@pytest.mark.asyncio
async def test_async_table_repr(async_engine_with_data):
    """Test AsyncTable repr."""
    table = AsyncTable("test_table", async_engine_with_data)
    async with table:
        repr_str = repr(table)
        assert "AsyncTable" in repr_str
        assert "test_table" in repr_str


@pytest.mark.asyncio
async def test_async_table_context_manager(async_engine_with_data):
    """Test AsyncTable context manager."""
    async with AsyncTable("test_table", async_engine_with_data) as table:
        assert table._table is not None
        assert table.column_names == ["id", "name", "value"]


@pytest.mark.asyncio
async def test_async_table_len(async_engine_with_data):
    """Test AsyncTable __len__."""
    table = AsyncTable("test_table", async_engine_with_data)
    length = await table.__len__()
    assert length == 3


# Array-like Access


@pytest.mark.asyncio
async def test_async_table_getitem_int(async_engine_with_data):
    """Test AsyncTable __getitem__ with int (record by index)."""
    table = AsyncTable("test_table", async_engine_with_data)
    await table._get_table()

    record = await table[0]
    assert record["name"] == "Alice"


@pytest.mark.asyncio
async def test_async_table_getitem_str(async_engine_with_data):
    """Test AsyncTable __getitem__ with str (column values)."""
    table = AsyncTable("test_table", async_engine_with_data)
    await table._get_table()

    names = await table["name"]
    assert len(names) == 3
    assert "Alice" in names
    assert "Bob" in names


@pytest.mark.asyncio
async def test_async_table_getitem_slice(async_engine_with_data):
    """Test AsyncTable __getitem__ with slice."""
    table = AsyncTable("test_table", async_engine_with_data)
    await table._get_table()

    records = await table[0:2]
    assert len(records) == 2
    assert records[0]["name"] == "Alice"
    assert records[1]["name"] == "Bob"


@pytest.mark.asyncio
async def test_async_table_iteration(async_engine_with_data):
    """Test AsyncTable async iteration."""
    table = AsyncTable("test_table", async_engine_with_data)
    await table._get_table()

    records = []
    async for record in table:
        records.append(record)

    assert len(records) == 3
    assert records[0]["name"] == "Alice"


# CRUD Operations


@pytest.mark.asyncio
async def test_async_table_insert(async_engine_with_data):
    """Test AsyncTable insert_records."""
    table = AsyncTable("test_table", async_engine_with_data)
    async with table:
        await table.insert_records([{"id": 4, "name": "Diana", "value": 400}])

        # Verify
        all_records = await table.select_all()
        assert len(all_records) == 4
        assert all_records[3]["name"] == "Diana"


@pytest.mark.asyncio
async def test_async_table_update(async_engine_with_data):
    """Test AsyncTable update_records."""
    table = AsyncTable("test_table", async_engine_with_data)
    async with table:
        await table.update_records([{"id": 1, "name": "Alice Updated", "value": 150}])

        # Verify
        record = await table.select_record_by_primary_key({"id": 1})
        assert record["name"] == "Alice Updated"
        assert record["value"] == 150


@pytest.mark.asyncio
async def test_async_table_set_column_values(async_engine_with_data):
    """Test AsyncTable set_column_values."""
    table = AsyncTable("test_table", async_engine_with_data)
    async with table:
        await table.set_column_values("value", 999)

        # Verify all values changed
        records = await table.select_all()
        assert all(r["value"] == 999 for r in records)


@pytest.mark.asyncio
async def test_async_table_delete_records(async_engine_with_data):
    """Test AsyncTable delete_records."""
    table = AsyncTable("test_table", async_engine_with_data)
    async with table:
        await table.delete_records("id", [1, 3])

        # Verify
        records = await table.select_all()
        assert len(records) == 1
        assert records[0]["name"] == "Bob"


@pytest.mark.asyncio
async def test_async_table_delete_all_records(async_engine_with_data):
    """Test AsyncTable delete_all_records."""
    table = AsyncTable("test_table", async_engine_with_data)
    async with table:
        await table.delete_all_records()

        # Verify
        records = await table.select_all()
        assert len(records) == 0


@pytest.mark.asyncio
async def test_async_table_drop(async_engine_with_data):
    """Test AsyncTable drop."""
    table = AsyncTable("test_table", async_engine_with_data)
    await table._get_table()

    await table.drop()

    # Verify table is gone
    assert table._table is None


# Select Operations


@pytest.mark.asyncio
async def test_async_table_select_all(async_engine_with_data):
    """Test AsyncTable select_all."""
    table = AsyncTable("test_table", async_engine_with_data)
    async with table:
        records = await table.select_all()
        assert len(records) == 3


@pytest.mark.asyncio
async def test_async_table_select_with_options(async_engine_with_data):
    """Test AsyncTable select with sorting and columns."""
    table = AsyncTable("test_table", async_engine_with_data)
    async with table:
        records = await table.select_records_all(sorted=True, include_columns=["id", "name"])

        assert len(records) == 3
        assert records[0]["id"] == 1
        assert "value" not in records[0]


@pytest.mark.asyncio
async def test_async_table_select_column_values(async_engine_with_data):
    """Test AsyncTable select_column_values_all."""
    table = AsyncTable("test_table", async_engine_with_data)
    async with table:
        values = await table.select_column_values_all("value")
        assert values == [100, 200, 300]
