"""Tests for Table class and its magic methods."""

import pytest

import fullmetalalchemy as fa
from fullmetalalchemy.records import records_equal
from fullmetalalchemy.table import Table


@pytest.fixture
def populated_table(engine_and_table):
    """Create a Table instance with populated data."""
    engine, _sa_table = engine_and_table
    return Table("xy", engine)


def test_table_repr(populated_table):
    """Test Table __repr__ method."""
    repr_str = repr(populated_table)
    assert "Table(name=xy" in repr_str
    assert "columns=" in repr_str
    assert "pks=" in repr_str
    assert "types=" in repr_str


def test_table_len(populated_table):
    """Test Table __len__ magic method."""
    assert len(populated_table) == 4


def test_table_eq(engine_and_table):
    """Test Table __eq__ magic method."""
    engine, sa_table = engine_and_table
    table1 = Table("xy", engine)
    Table("xy", engine)
    # Tables with same metadata should be equal
    assert table1 == sa_table


def test_table_getitem_int(populated_table):
    """Test Table __getitem__ with integer index."""
    record = populated_table[0]
    assert record == {"id": 1, "x": 1, "y": 2}

    record = populated_table[2]
    assert record == {"id": 3, "x": 4, "y": 8}


def test_table_getitem_str(populated_table):
    """Test Table __getitem__ with string column name."""
    values = populated_table["x"]
    assert values == [1, 2, 4, 8]


def test_table_getitem_slice(populated_table):
    """Test Table __getitem__ with slice."""
    records = populated_table[1:3]
    expected = [{"id": 2, "x": 2, "y": 4}, {"id": 3, "x": 4, "y": 8}]
    assert records_equal(records, expected)


def test_table_getitem_invalid_key(populated_table):
    """Test Table __getitem__ with invalid key type."""
    with pytest.raises(ValueError, match="key must be int, str, or slice"):
        _ = populated_table[12.5]


def test_table_add_dict(engine_and_table):
    """Test Table __add__ with single dict."""
    engine, _ = engine_and_table
    table = Table("xy", engine)

    table + {"id": 5, "x": 10, "y": 20}

    records = fa.select.select_records_all(table.sa_table, engine)
    assert len(records) == 5
    assert records[-1] == {"id": 5, "x": 10, "y": 20}


def test_table_add_iterable(engine_and_table):
    """Test Table __add__ with iterable of dicts."""
    engine, _ = engine_and_table
    table = Table("xy", engine)

    new_records = [{"id": 5, "x": 10, "y": 20}, {"id": 6, "x": 11, "y": 21}]
    table + new_records

    records = fa.select.select_records_all(table.sa_table, engine)
    assert len(records) == 6


def test_table_sub_dict(engine_and_table):
    """Test Table __sub__ with single dict."""
    engine, _ = engine_and_table
    table = Table("xy", engine)

    table - {"id": 1}

    records = fa.select.select_records_all(table.sa_table, engine)
    assert len(records) == 3
    assert all(r["id"] != 1 for r in records)


def test_table_sub_iterable(engine_and_table):
    """Test Table __sub__ with iterable of dicts."""
    engine, _ = engine_and_table
    table = Table("xy", engine)

    to_delete = [{"id": 1}, {"id": 3}]
    table - to_delete

    records = fa.select.select_records_all(table.sa_table, engine)
    assert len(records) == 2
    assert all(r["id"] not in [1, 3] for r in records)


def test_table_delitem_int(engine_and_table):
    """Test Table __delitem__ with integer index."""
    engine, _ = engine_and_table
    table = Table("xy", engine)

    del table[0]

    records = fa.select.select_records_all(table.sa_table, engine)
    assert len(records) == 3
    assert all(r["id"] != 1 for r in records)


def test_table_delitem_slice(engine_and_table):
    """Test Table __delitem__ with slice."""
    engine, _ = engine_and_table
    table = Table("xy", engine)

    del table[1:3]

    records = fa.select.select_records_all(table.sa_table, engine)
    assert len(records) == 2


def test_table_records_property(populated_table):
    """Test Table.records property."""
    records = populated_table.records
    assert len(records) == 4
    assert records[0]["id"] == 1


def test_table_columns_property(populated_table):
    """Test Table.columns property."""
    columns = populated_table.columns
    assert columns == ["id", "x", "y"]


def test_table_column_names_property(populated_table):
    """Test Table.column_names property."""
    assert populated_table.column_names == ["id", "x", "y"]


def test_table_column_types_property(populated_table):
    """Test Table.column_types property."""
    col_types = populated_table.column_types
    assert "id" in col_types
    assert "x" in col_types
    assert "y" in col_types


def test_table_primary_key_names_property(populated_table):
    """Test Table.primary_key_names property."""
    assert populated_table.primary_key_names == ["id"]


def test_table_row_count_property(populated_table):
    """Test Table.row_count property."""
    assert populated_table.row_count == 4


def test_table_drop(engine_and_table):
    """Test Table.drop() method."""
    engine, _ = engine_and_table
    table = Table("xy", engine)

    table.drop(if_exists=True)

    table_names = fa.get_table_names(engine)
    assert "xy" not in table_names


def test_table_delete_records(engine_and_table):
    """Test Table.delete_records() method."""
    engine, _ = engine_and_table
    table = Table("xy", engine)

    table.delete_records("id", [1, 3])

    records = fa.select.select_records_all(table.sa_table, engine)
    assert len(records) == 2
    assert all(r["id"] in [2, 4] for r in records)


def test_table_delete_records_by_values(engine_and_table):
    """Test Table.delete_records_by_values() method."""
    engine, _ = engine_and_table
    table = Table("xy", engine)

    table.delete_records_by_values([{"id": 2}, {"x": 4}])

    records = fa.select.select_records_all(table.sa_table, engine)
    assert len(records) == 2


def test_table_delete_all_records(engine_and_table):
    """Test Table.delete_all_records() method."""
    engine, _ = engine_and_table
    table = Table("xy", engine)

    table.delete_all_records()

    records = fa.select.select_records_all(table.sa_table, engine)
    assert records == []


def test_table_insert_records(engine_and_table):
    """Test Table.insert_records() method."""
    engine, _ = engine_and_table
    table = Table("xy", engine)

    table.insert_records([{"id": 5, "x": 10, "y": 20}])

    records = fa.select.select_records_all(table.sa_table, engine)
    assert len(records) == 5
    assert records[-1] == {"id": 5, "x": 10, "y": 20}


def test_table_insert_from_table_functional(engine_and_table):
    """Test Table.insert_from_table() actually inserts data."""
    engine, _sa_table1 = engine_and_table

    # Create second empty table with same structure
    sa_table2 = fa.create.create_table(
        "xy_copy", ["id", "x", "y"], [int, int, int], ["id"], engine, if_exists="replace"
    )

    # Note: insert_from_table(table1, table2, engine) inserts FROM table1 INTO table2
    # So Table(xy).insert_from_table(xy_copy) would insert from xy into xy_copy
    table1 = Table("xy", engine)
    table1.insert_from_table(sa_table2)

    # Check that xy_copy now has the data
    records = fa.select.select_records_all(sa_table2, engine)
    assert len(records) == 4
    assert records[0] == {"id": 1, "x": 1, "y": 2}


def test_table_update_records(engine_and_table):
    """Test Table.update_records() method."""
    engine, _ = engine_and_table
    table = Table("xy", engine)

    table.update_records([{"id": 1, "x": 100, "y": 200}])

    record = fa.select.select_record_by_primary_key(table.sa_table, {"id": 1}, engine)
    assert record["x"] == 100
    assert record["y"] == 200


def test_table_update_matching_records(engine_and_table):
    """Test Table.update_matching_records() method."""
    engine, _ = engine_and_table
    table = Table("xy", engine)

    table.update_matching_records([{"id": 2, "x": 99}], ["id"])

    record = fa.select.select_record_by_primary_key(table.sa_table, {"id": 2}, engine)
    assert record["x"] == 99
    assert record["y"] == 4  # y unchanged


def test_table_set_column_values(engine_and_table):
    """Test Table.set_column_values() method."""
    engine, _ = engine_and_table
    table = Table("xy", engine)

    table.set_column_values("x", 42)

    values = fa.select.select_column_values_all(table.sa_table, "x", engine)
    assert all(v == 42 for v in values)


def test_table_select_methods_from_basetable(populated_table):
    """Test that Table inherits all select methods from BaseTable."""
    # Test select_existing_values
    result = populated_table.select_existing_values("x", [1, 2, 5, 10])
    assert set(result) == {1, 2}

    # Test select_column_values_chunks
    chunks = list(populated_table.select_column_values_chunks("x", chunksize=2))
    assert len(chunks) == 2

    # Test select_column_values_by_slice
    values = populated_table.select_column_values_by_slice("x", 1, 3)
    assert values == [2, 4]

    # Test select_column_value_by_index
    value = populated_table.select_column_value_by_index("x", 2)
    assert value == 4

    # Test select_primary_key_records_by_slice
    records = populated_table.select_primary_key_records_by_slice(slice(0, 2))
    assert len(records) == 2

    # Test select_record_by_primary_key
    record = populated_table.select_record_by_primary_key({"id": 3})
    assert record == {"id": 3, "x": 4, "y": 8}

    # Test select_records_by_primary_keys
    records = populated_table.select_records_by_primary_keys([{"id": 1}, {"id": 3}])
    assert len(records) == 2

    # Test select_column_values_by_primary_keys
    values = populated_table.select_column_values_by_primary_keys("x", [{"id": 1}, {"id": 2}])
    assert values == [1, 2]

    # Test select_value_by_primary_keys
    value = populated_table.select_value_by_primary_keys("y", {"id": 4})
    assert value == 11


def test_basetable_abstract_methods_not_implemented(engine_and_table):
    """Test that BaseTable abstract methods raise NotImplementedError."""
    from fullmetalalchemy.basetable import BaseTable

    engine, _ = engine_and_table

    # Create a minimal concrete subclass for testing
    class MinimalTable(BaseTable):
        pass

    test_table = MinimalTable("xy", engine)

    # Test insert_records raises NotImplementedError
    with pytest.raises(NotImplementedError):
        test_table.insert_records([{"id": 1}])

    # Test delete_records_by_values raises NotImplementedError
    with pytest.raises(NotImplementedError):
        test_table.delete_records_by_values([{"id": 1}])


def test_table_select_records_chunks_with_all_params(populated_table):
    """Test select_records_chunks with all parameters for full coverage."""
    chunks = list(
        populated_table.select_records_chunks(chunksize=2, sorted=True, include_columns=["id", "x"])
    )
    # Should get 2 chunks with only id and x columns, sorted
    assert len(chunks) == 2
    assert chunks[0][0] == {"id": 1, "x": 1}
    assert chunks[0][1] == {"id": 2, "x": 2}
