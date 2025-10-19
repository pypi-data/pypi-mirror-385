"""Comprehensive async CRUD operation tests."""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from fullmetalalchemy import async_api


@pytest.fixture(scope="function")
async def async_engine():
    """Create async engine for tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def async_table(async_engine):
    """Create test table."""
    table = await async_api.create.create_table(
        "test_table",
        ["id", "name", "value"],
        [int, str, int],
        primary_key="id",
        engine=async_engine,
    )
    yield table, async_engine


# CREATE Tests


@pytest.mark.asyncio
async def test_create_table_basic(async_engine):
    """Test basic table creation."""
    table = await async_api.create.create_table(
        "users",
        ["id", "name", "age"],
        [int, str, int],
        primary_key="id",
        engine=async_engine,
    )

    assert table.name == "users"
    assert len(table.columns) == 3
    assert "id" in table.columns
    assert "name" in table.columns
    assert "age" in table.columns


@pytest.mark.asyncio
async def test_create_table_from_records(async_engine):
    """Test table creation from records."""
    records = [
        {"id": 1, "name": "Alice", "score": 95},
        {"id": 2, "name": "Bob", "score": 87},
    ]

    table = await async_api.create.create_table_from_records(
        "students", records, primary_key="id", engine=async_engine
    )

    assert table.name == "students"

    # Verify records were inserted
    result_records = await async_api.select.select_records_all(table, async_engine)
    assert len(result_records) == 2
    assert result_records[0]["name"] == "Alice"


@pytest.mark.asyncio
async def test_create_table_if_exists_replace(async_engine):
    """Test replacing existing table."""
    # Create table
    await async_api.create.create_table(
        "temp", ["id"], [int], primary_key="id", engine=async_engine
    )

    # Replace it
    table = await async_api.create.create_table(
        "temp",
        ["id", "data"],
        [int, str],
        primary_key="id",
        engine=async_engine,
        if_exists="replace",
    )

    assert len(table.columns) == 2  # New table has 2 columns


@pytest.mark.asyncio
async def test_copy_table(async_engine):
    """Test copying table structure and data."""
    # Create source table with data
    source = await async_api.create.create_table_from_records(
        "source",
        [{"id": 1, "val": "a"}, {"id": 2, "val": "b"}],
        primary_key="id",
        engine=async_engine,
    )

    # Copy table
    dest = await async_api.create.copy_table(source, "destination", async_engine)

    assert dest.name == "destination"

    # Verify data was copied
    records = await async_api.select.select_records_all(dest, async_engine)
    assert len(records) == 2
    assert records[0]["val"] == "a"


# INSERT Tests


@pytest.mark.asyncio
async def test_insert_records(async_table):
    """Test inserting records."""
    table, engine = async_table

    records = [
        {"id": 1, "name": "Alice", "value": 100},
        {"id": 2, "name": "Bob", "value": 200},
    ]

    await async_api.insert.insert_records(table, records, engine)

    # Verify insertion
    result = await async_api.select.select_records_all(table, engine)
    assert len(result) == 2
    assert result[0]["name"] == "Alice"
    assert result[1]["value"] == 200


@pytest.mark.asyncio
async def test_insert_from_table(async_engine):
    """Test inserting from one table to another."""
    # Create source table with data
    source = await async_api.create.create_table_from_records(
        "source_tbl",
        [{"id": 1, "data": "x"}, {"id": 2, "data": "y"}],
        primary_key="id",
        engine=async_engine,
    )

    # Create empty destination table
    dest = await async_api.create.create_table(
        "dest_tbl", ["id", "data"], [int, str], primary_key="id", engine=async_engine
    )

    # Insert from source to dest
    await async_api.insert.insert_from_table(source, dest, async_engine)

    # Verify
    records = await async_api.select.select_records_all(dest, async_engine)
    assert len(records) == 2
    assert records[0]["data"] == "x"


# SELECT Tests


@pytest.mark.asyncio
async def test_select_records_all(async_table):
    """Test selecting all records."""
    table, engine = async_table

    # Insert test data
    await async_api.insert.insert_records(
        table,
        [
            {"id": 1, "name": "Alice", "value": 100},
            {"id": 2, "name": "Bob", "value": 200},
        ],
        engine,
    )

    # Select all
    records = await async_api.select.select_records_all(table, engine)

    assert len(records) == 2
    assert records[0]["name"] == "Alice"


@pytest.mark.asyncio
async def test_select_records_sorted(async_table):
    """Test selecting with sorting."""
    table, engine = async_table

    # Insert in non-sorted order
    await async_api.insert.insert_records(
        table,
        [
            {"id": 3, "name": "Charlie", "value": 300},
            {"id": 1, "name": "Alice", "value": 100},
            {"id": 2, "name": "Bob", "value": 200},
        ],
        engine,
    )

    # Select sorted
    records = await async_api.select.select_records_all(table, engine, sorted=True)

    assert len(records) == 3
    assert records[0]["id"] == 1
    assert records[1]["id"] == 2
    assert records[2]["id"] == 3


@pytest.mark.asyncio
async def test_select_records_slice(async_table):
    """Test selecting a slice of records."""
    table, engine = async_table

    # Insert test data
    await async_api.insert.insert_records(
        table,
        [
            {"id": 1, "name": "Alice", "value": 100},
            {"id": 2, "name": "Bob", "value": 200},
            {"id": 3, "name": "Charlie", "value": 300},
            {"id": 4, "name": "David", "value": 400},
        ],
        engine,
    )

    # Select slice
    records = await async_api.select.select_records_slice(
        table, start=1, stop=3, engine=engine, sorted=True
    )

    assert len(records) == 2
    assert records[0]["name"] == "Bob"
    assert records[1]["name"] == "Charlie"


@pytest.mark.asyncio
async def test_select_column_values_all(async_table):
    """Test selecting all values from a column."""
    table, engine = async_table

    await async_api.insert.insert_records(
        table,
        [
            {"id": 1, "name": "Alice", "value": 100},
            {"id": 2, "name": "Bob", "value": 200},
        ],
        engine,
    )

    values = await async_api.select.select_column_values_all(table, "name", engine)

    assert len(values) == 2
    assert "Alice" in values
    assert "Bob" in values


@pytest.mark.asyncio
async def test_select_record_by_primary_key(async_table):
    """Test selecting by primary key."""
    table, engine = async_table

    await async_api.insert.insert_records(
        table,
        [
            {"id": 1, "name": "Alice", "value": 100},
            {"id": 2, "name": "Bob", "value": 200},
        ],
        engine,
    )

    record = await async_api.select.select_record_by_primary_key(table, {"id": 2}, engine)

    assert record["name"] == "Bob"
    assert record["value"] == 200


@pytest.mark.asyncio
async def test_select_with_include_columns(async_table):
    """Test selecting specific columns."""
    table, engine = async_table

    await async_api.insert.insert_records(table, [{"id": 1, "name": "Alice", "value": 100}], engine)

    records = await async_api.select.select_records_all(
        table, engine, include_columns=["id", "name"]
    )

    assert len(records) == 1
    assert "id" in records[0]
    assert "name" in records[0]
    assert "value" not in records[0]


# UPDATE Tests


@pytest.mark.asyncio
async def test_update_records(async_table):
    """Test updating records."""
    table, engine = async_table

    # Insert initial data
    await async_api.insert.insert_records(table, [{"id": 1, "name": "Alice", "value": 100}], engine)

    # Update
    await async_api.update.update_records(
        table, [{"id": 1, "name": "Alice Updated", "value": 150}], engine
    )

    # Verify
    records = await async_api.select.select_records_all(table, engine)
    assert records[0]["name"] == "Alice Updated"
    assert records[0]["value"] == 150


@pytest.mark.asyncio
async def test_update_matching_records(async_table):
    """Test updating records matching criteria."""
    table, engine = async_table

    # Insert initial data
    await async_api.insert.insert_records(
        table,
        [
            {"id": 1, "name": "Alice", "value": 100},
            {"id": 2, "name": "Bob", "value": 100},
        ],
        engine,
    )

    # Update all records with value=100
    await async_api.update.update_matching_records(table, [{"value": 100}], {"value": 999}, engine)

    # Verify both were updated
    records = await async_api.select.select_records_all(table, engine)
    assert records[0]["value"] == 999
    assert records[1]["value"] == 999


@pytest.mark.asyncio
async def test_set_column_values(async_table):
    """Test setting all values in a column."""
    table, engine = async_table

    # Insert initial data
    await async_api.insert.insert_records(
        table,
        [
            {"id": 1, "name": "Alice", "value": 100},
            {"id": 2, "name": "Bob", "value": 200},
        ],
        engine,
    )

    # Set all values to 500
    await async_api.update.set_column_values(table, "value", 500, engine)

    # Verify
    records = await async_api.select.select_records_all(table, engine)
    assert all(r["value"] == 500 for r in records)


# DELETE Tests


@pytest.mark.asyncio
async def test_delete_records(async_table):
    """Test deleting records."""
    table, engine = async_table

    # Insert test data
    await async_api.insert.insert_records(
        table,
        [
            {"id": 1, "name": "Alice", "value": 100},
            {"id": 2, "name": "Bob", "value": 200},
        ],
        engine,
    )

    # Delete first record
    await async_api.delete.delete_records(table, [{"id": 1, "name": "Alice", "value": 100}], engine)

    # Verify
    records = await async_api.select.select_records_all(table, engine)
    assert len(records) == 1
    assert records[0]["name"] == "Bob"


@pytest.mark.asyncio
async def test_delete_records_by_values(async_table):
    """Test deleting by column values."""
    table, engine = async_table

    # Insert test data
    await async_api.insert.insert_records(
        table,
        [
            {"id": 1, "name": "Alice", "value": 100},
            {"id": 2, "name": "Bob", "value": 200},
            {"id": 3, "name": "Charlie", "value": 300},
        ],
        engine,
    )

    # Delete by IDs
    await async_api.delete.delete_records_by_values(table, "id", [1, 3], engine)

    # Verify
    records = await async_api.select.select_records_all(table, engine)
    assert len(records) == 1
    assert records[0]["name"] == "Bob"


@pytest.mark.asyncio
async def test_delete_all_records(async_table):
    """Test deleting all records."""
    table, engine = async_table

    # Insert test data
    await async_api.insert.insert_records(
        table,
        [
            {"id": 1, "name": "Alice", "value": 100},
            {"id": 2, "name": "Bob", "value": 200},
        ],
        engine,
    )

    # Delete all
    await async_api.delete.delete_all_records(table, engine)

    # Verify
    records = await async_api.select.select_records_all(table, engine)
    assert len(records) == 0


# DROP Tests


@pytest.mark.asyncio
async def test_drop_table(async_engine):
    """Test dropping table."""
    # Create table
    table = await async_api.create.create_table(
        "temp_drop", ["id"], [int], primary_key="id", engine=async_engine
    )

    # Drop it
    await async_api.drop.drop_table(table, async_engine)

    # Verify it's gone by trying to drop again with if_exists=False raises SQL error
    import sqlalchemy as sa

    with pytest.raises((ValueError, RuntimeError, sa.exc.OperationalError)):
        await async_api.drop.drop_table(table, async_engine, if_exists=False)


@pytest.mark.asyncio
async def test_drop_table_if_exists(async_engine):
    """Test dropping non-existent table with if_exists=True."""
    # This should not raise an error
    await async_api.drop.drop_table("nonexistent", async_engine, if_exists=True)
