"""Tests for SessionTable class and transaction management."""

import pytest
import sqlalchemy as sa

import fullmetalalchemy as fa
from fullmetalalchemy.sessiontable import SessionTable


def test_sessiontable_init_with_engine(engine_and_table):
    """Test SessionTable initialization with Engine."""
    engine, _ = engine_and_table
    table = SessionTable("xy", engine)

    assert table.name == "xy"
    assert isinstance(table.session, sa.orm.session.Session)


def test_sessiontable_init_with_session(engine_and_table):
    """Test SessionTable initialization with Session."""
    engine, _ = engine_and_table
    session = fa.features.get_session(engine)

    table = SessionTable("xy", session)

    assert table.name == "xy"
    assert table.session is session


def test_sessiontable_init_invalid_type():
    """Test SessionTable initialization with invalid type raises TypeError."""
    with pytest.raises(TypeError, match="engine must be SqlAlchemy Engine or Session"):
        SessionTable("xy", "not_an_engine")


def test_sessiontable_context_manager_success(engine_and_table):
    """Test SessionTable context manager commits on success."""
    engine, _ = engine_and_table

    with SessionTable("xy", engine) as table:
        table.insert_records([{"id": 5, "x": 10, "y": 20}])

    # Verify changes were committed
    sa_table = fa.get_table("xy", engine)
    records = fa.select.select_records_all(sa_table, engine)
    assert len(records) == 5


def test_sessiontable_context_manager_rollback_on_error(engine_and_table):
    """Test SessionTable context manager rolls back on error."""
    engine, _ = engine_and_table

    try:
        with SessionTable("xy", engine) as table:
            table.insert_records([{"id": 5, "x": 10, "y": 20}])
            raise ValueError("Intentional error")
    except ValueError:
        pass

    # Verify changes were rolled back
    sa_table = fa.get_table("xy", engine)
    records = fa.select.select_records_all(sa_table, engine)
    assert len(records) == 4  # Original count


def test_sessiontable_commit(engine_and_table):
    """Test SessionTable.commit() method."""
    engine, _ = engine_and_table
    table = SessionTable("xy", engine)

    table.insert_records([{"id": 5, "x": 10, "y": 20}])
    new_table = table.commit()

    assert isinstance(new_table, SessionTable)
    sa_table = fa.get_table("xy", engine)
    records = fa.select.select_records_all(sa_table, engine)
    assert len(records) == 5


def test_sessiontable_rollback(engine_and_table):
    """Test SessionTable.rollback() method."""
    engine, _ = engine_and_table
    table = SessionTable("xy", engine)

    table.insert_records([{"id": 5, "x": 10, "y": 20}])
    new_table = table.rollback()

    assert isinstance(new_table, SessionTable)
    sa_table = fa.get_table("xy", engine)
    records = fa.select.select_records_all(sa_table, engine)
    assert len(records) == 4  # Changes rolled back


def test_sessiontable_repr(engine_and_table):
    """Test SessionTable __repr__ method."""
    engine, _ = engine_and_table
    table = SessionTable("xy", engine)

    repr_str = repr(table)
    assert "SessionTable(name=xy" in repr_str
    assert "columns=" in repr_str
    assert "pks=" in repr_str


def test_sessiontable_delete_records(engine_and_table):
    """Test SessionTable.delete_records() method."""
    engine, _ = engine_and_table
    table = SessionTable("xy", engine)

    table.delete_records("id", [1, 3])
    table.session.commit()

    sa_table = fa.get_table("xy", engine)
    records = fa.select.select_records_all(sa_table, engine)
    assert len(records) == 2


def test_sessiontable_delete_records_by_values(engine_and_table):
    """Test SessionTable.delete_records_by_values() method."""
    engine, _ = engine_and_table
    table = SessionTable("xy", engine)

    table.delete_records_by_values([{"id": 2}])
    table.session.commit()

    sa_table = fa.get_table("xy", engine)
    records = fa.select.select_records_all(sa_table, engine)
    assert len(records) == 3


def test_sessiontable_delete_all_records(engine_and_table):
    """Test SessionTable.delete_all_records() method."""
    engine, _ = engine_and_table
    table = SessionTable("xy", engine)

    table.delete_all_records()
    table.session.commit()

    sa_table = fa.get_table("xy", engine)
    records = fa.select.select_records_all(sa_table, engine)
    assert records == []


def test_sessiontable_insert_records(engine_and_table):
    """Test SessionTable.insert_records() method."""
    engine, _ = engine_and_table
    table = SessionTable("xy", engine)

    table.insert_records([{"id": 5, "x": 10, "y": 20}])
    table.session.commit()

    sa_table = fa.get_table("xy", engine)
    records = fa.select.select_records_all(sa_table, engine)
    assert len(records) == 5


def test_sessiontable_update_records(engine_and_table):
    """Test SessionTable.update_records() method."""
    engine, _ = engine_and_table
    table = SessionTable("xy", engine)

    table.update_records([{"id": 1, "x": 100}])
    table.session.commit()

    sa_table = fa.get_table("xy", engine)
    record = fa.select.select_record_by_primary_key(sa_table, {"id": 1}, engine)
    assert record["x"] == 100


def test_sessiontable_update_matching_records(engine_and_table):
    """Test SessionTable.update_matching_records() method."""
    engine, _ = engine_and_table
    table = SessionTable("xy", engine)

    table.update_matching_records([{"id": 2, "x": 99}], ["id"])
    table.session.commit()

    sa_table = fa.get_table("xy", engine)
    record = fa.select.select_record_by_primary_key(sa_table, {"id": 2}, engine)
    assert record["x"] == 99


def test_sessiontable_set_column_values(engine_and_table):
    """Test SessionTable.set_column_values() method."""
    engine, _ = engine_and_table
    table = SessionTable("xy", engine)

    table.set_column_values("x", 42)
    table.session.commit()

    sa_table = fa.get_table("xy", engine)
    values = fa.select.select_column_values_all(sa_table, "x", engine)
    assert all(v == 42 for v in values)


def test_sessiontable_insert_from_table_functional(engine_and_table):
    """Test SessionTable.insert_from_table() actually inserts data."""
    engine, _sa_table1 = engine_and_table

    # Create second empty table with same structure
    sa_table2 = fa.create.create_table(
        "xy_copy", ["id", "x", "y"], [int, int, int], ["id"], engine, if_exists="replace"
    )

    # Note: insert_from_table_session(table1, table2, session) inserts FROM table1 INTO table2
    # So SessionTable(xy).insert_from_table(xy_copy) would insert from xy into xy_copy
    table1 = SessionTable("xy", engine)
    table1.insert_from_table(sa_table2)
    table1.commit()

    # Check that xy_copy now has the data
    records = fa.select.select_records_all(sa_table2, engine)
    assert len(records) == 4
    assert records[0] == {"id": 1, "x": 1, "y": 2}
