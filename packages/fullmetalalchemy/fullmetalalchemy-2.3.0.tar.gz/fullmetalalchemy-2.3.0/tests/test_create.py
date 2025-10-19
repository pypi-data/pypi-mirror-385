import pytest
import sqlalchemy as sa

import fullmetalalchemy as sz
from fullmetalalchemy.create import (
    _column_datatype,
    copy_table,
    create_engine,
    create_table,
    create_table_from_records,
)
from fullmetalalchemy.features import tables_metadata_equal
from fullmetalalchemy.records import records_equal


@pytest.fixture
def engine():
    """Create a fresh in-memory SQLite engine for each test."""
    return sa.create_engine("sqlite://")


def test_create_table_sqlite(engine):
    """Test creating a table from specifications."""
    create_table(
        table_name="xy",
        column_names=["id", "x", "y"],
        column_types=[int, int, int],
        primary_key=["id"],
        engine=engine,
        if_exists="replace",
    )
    table = sz.features.get_table("xy", engine)
    expected = sa.Table(
        "xy",
        sa.MetaData(),
        sa.Column("id", sa.sql.sqltypes.INTEGER(), primary_key=True, nullable=False),
        sa.Column("x", sa.sql.sqltypes.INTEGER()),
        sa.Column("y", sa.sql.sqltypes.INTEGER()),
        schema=None,
    )
    assert tables_metadata_equal(table, expected)


def test_create_table_from_records_sqlite(engine):
    """Test creating a table from records with automatic type inference."""
    records = [
        {"id": 1, "x": 1, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 11},
    ]
    table = create_table_from_records(
        table_name="xy", records=records, primary_key=["id"], engine=engine, if_exists="replace"
    )
    expected = sa.Table(
        "xy",
        sa.MetaData(),
        sa.Column("id", sa.sql.sqltypes.INTEGER(), primary_key=True, nullable=False),
        sa.Column("x", sa.sql.sqltypes.INTEGER()),
        sa.Column("y", sa.sql.sqltypes.INTEGER()),
        schema=None,
    )
    assert tables_metadata_equal(table, expected)
    selected = sz.select.select_records_all(table, engine)
    assert records_equal(selected, records)


def test_create_engine():
    """Test create_engine wrapper function."""
    engine = create_engine("sqlite://")
    assert isinstance(engine, sa.engine.Engine)


def test_copy_table(engine_and_table):
    """Test copying a table to a new table."""
    engine, original_table = engine_and_table

    # Copy the table
    new_table = copy_table("xy_copy", original_table, engine)

    assert new_table.name == "xy_copy"
    # Verify data was copied
    records = sz.select.select_records_all(new_table, engine)
    assert len(records) == 4
    assert records[0] == {"id": 1, "x": 1, "y": 2}


def test_copy_table_with_if_exists_replace(engine_and_table):
    """Test copy_table with if_exists='replace'."""
    engine, original_table = engine_and_table

    # Create table first
    copy_table("xy_copy", original_table, engine, if_exists="replace")
    # Copy again with replace
    new_table = copy_table("xy_copy", original_table, engine, if_exists="replace")

    assert new_table.name == "xy_copy"
    records = sz.select.select_records_all(new_table, engine)
    assert len(records) == 4


def test_column_datatype_float():
    """Test _column_datatype with float values."""
    values = [1.5, 2.7, 3.9]
    result = _column_datatype(values)
    assert result is float


def test_column_datatype_string():
    """Test _column_datatype with string values."""
    values = ["hello", "world", "test"]
    result = _column_datatype(values)
    assert result is str


def test_column_datatype_list():
    """Test _column_datatype with list values."""
    values = [[1, 2], [3, 4]]
    result = _column_datatype(values)
    assert result is list


def test_column_datatype_dict():
    """Test _column_datatype with dict values."""
    values = [{"a": 1}, {"b": 2}]
    result = _column_datatype(values)
    assert result is dict


def test_column_datatype_mixed_fallback():
    """Test _column_datatype falls back to str for mixed types."""
    values = [1, "a", 2.5]
    result = _column_datatype(values)
    assert result is str


def test_create_table_with_autoincrement(engine):
    """Test creating table with autoincrement primary key."""
    table = create_table(
        table_name="test_auto",
        column_names=["id", "value"],
        column_types=[int, str],
        primary_key=["id"],
        engine=engine,
        autoincrement=True,
        if_exists="replace",
    )
    assert table.name == "test_auto"


def test_column_datatype_with_unhashable_types():
    """Test _column_datatype with unhashable types (lists/dicts in values)."""
    # This triggers the TypeError except block when trying to hash
    values = [[1, 2, 3], [4, 5, 6]]  # Lists are unhashable
    result = _column_datatype(values)
    # Should return list type
    assert result is list


def test_column_datatype_all_integers():
    """Test _column_datatype with all integer values."""
    # Integer values match both int and (int, float) tuple
    # Should prefer int (line 216-217)
    values = [1, 2, 3, 4, 5]
    result = _column_datatype(values)
    assert result is int


def test_column_datatype_mixed_int_and_float():
    """Test _column_datatype with mixed int and float values."""
    # Mixed int/float should match only (int, float) tuple
    values = [1, 2.5, 3, 4.7]
    result = _column_datatype(values)
    assert result is float
