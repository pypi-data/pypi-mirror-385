import pytest

import fullmetalalchemy as fa
from fullmetalalchemy.records import records_equal
from fullmetalalchemy.test_setup import create_second_test_table


def test_insert_from_table_session(engine_and_table):
    """Test inserting records from one table to another using session."""
    engine, table1 = engine_and_table
    table2 = create_second_test_table(engine)
    results = fa.select.select_records_all(table2)
    assert results == []

    session = fa.features.get_session(engine)
    fa.insert.insert_from_table_session(table1, table2, session)
    session.commit()

    results = fa.select.select_records_all(table2)
    expected = [
        {"id": 1, "x": 1, "y": 2, "z": None},
        {"id": 2, "x": 2, "y": 4, "z": None},
        {"id": 3, "x": 4, "y": 8, "z": None},
        {"id": 4, "x": 8, "y": 11, "z": None},
    ]
    assert records_equal(results, expected)


def test_insert_from_table_session_table_name(engine_and_table):
    """Test inserting from table using table names with session."""
    engine, _table1 = engine_and_table
    table2 = create_second_test_table(engine)
    results = fa.select.select_records_all(table2)
    assert results == []

    session = fa.features.get_session(engine)
    fa.insert.insert_from_table_session("xy", "xyz", session)
    session.commit()

    results = fa.select.select_records_all(table2)
    expected = [
        {"id": 1, "x": 1, "y": 2, "z": None},
        {"id": 2, "x": 2, "y": 4, "z": None},
        {"id": 3, "x": 4, "y": 8, "z": None},
        {"id": 4, "x": 8, "y": 11, "z": None},
    ]
    assert records_equal(results, expected)


def test_insert_from_table(engine_and_table):
    """Test inserting records from one table to another."""
    engine, table1 = engine_and_table
    table2 = create_second_test_table(engine)
    results = fa.select.select_records_all(table2)
    assert results == []

    fa.insert.insert_from_table(table1, table2, engine)

    results = fa.select.select_records_all(table2)
    expected = [
        {"id": 1, "x": 1, "y": 2, "z": None},
        {"id": 2, "x": 2, "y": 4, "z": None},
        {"id": 3, "x": 4, "y": 8, "z": None},
        {"id": 4, "x": 8, "y": 11, "z": None},
    ]
    assert records_equal(results, expected)


def test_insert_from_table_table_name(engine_and_table):
    """Test inserting from table using table names."""
    engine, _table1 = engine_and_table
    table2 = create_second_test_table(engine)
    results = fa.select.select_records_all(table2)
    assert results == []

    fa.insert.insert_from_table("xy", "xyz", engine)

    results = fa.select.select_records_all(table2)
    expected = [
        {"id": 1, "x": 1, "y": 2, "z": None},
        {"id": 2, "x": 2, "y": 4, "z": None},
        {"id": 3, "x": 4, "y": 8, "z": None},
        {"id": 4, "x": 8, "y": 11, "z": None},
    ]
    assert records_equal(results, expected)


def test_insert_from_table_no_engine(engine_and_table):
    """Test inserting from table without explicitly passing engine."""
    _engine, table = engine_and_table
    table2 = create_second_test_table(table.info.get("engine"))
    results = fa.select.select_records_all(table2)
    assert results == []

    fa.insert.insert_from_table(table, table2)

    results = fa.select.select_records_all(table2)
    expected = [
        {"id": 1, "x": 1, "y": 2, "z": None},
        {"id": 2, "x": 2, "y": 4, "z": None},
        {"id": 3, "x": 4, "y": 8, "z": None},
        {"id": 4, "x": 8, "y": 11, "z": None},
    ]
    assert records_equal(results, expected)


def test_insert_records_session(engine_and_table):
    """Test inserting records using a session."""
    engine, table = engine_and_table
    new_records = [{"id": 5, "x": 11, "y": 5}, {"id": 6, "x": 9, "y": 9}]

    session = fa.features.get_session(engine)
    fa.insert.insert_records_session(table, new_records, session)
    session.commit()

    results = fa.select.select_records_all(table)
    expected = [
        {"id": 1, "x": 1, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 11},
        {"id": 5, "x": 11, "y": 5},
        {"id": 6, "x": 9, "y": 9},
    ]
    assert records_equal(results, expected)


def test_insert_records_session_table_name(engine_and_table):
    """Test inserting records using session with table name."""
    engine, table = engine_and_table
    new_records = [{"id": 5, "x": 11, "y": 5}, {"id": 6, "x": 9, "y": 9}]

    session = fa.features.get_session(engine)
    fa.insert.insert_records_session("xy", new_records, session)
    session.commit()

    results = fa.select.select_records_all(table)
    expected = [
        {"id": 1, "x": 1, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 11},
        {"id": 5, "x": 11, "y": 5},
        {"id": 6, "x": 9, "y": 9},
    ]
    assert records_equal(results, expected)


def test_insert_records(engine_and_table):
    """Test inserting records with engine."""
    engine, table = engine_and_table
    new_records = [{"id": 5, "x": 11, "y": 5}, {"id": 6, "x": 9, "y": 9}]

    fa.insert.insert_records(table, new_records, engine)

    results = fa.select.select_records_all(table)
    expected = [
        {"id": 1, "x": 1, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 11},
        {"id": 5, "x": 11, "y": 5},
        {"id": 6, "x": 9, "y": 9},
    ]
    assert records_equal(results, expected)


def test_insert_records_table_name(engine_and_table):
    """Test inserting records using table name."""
    engine, table = engine_and_table
    new_records = [{"id": 5, "x": 11, "y": 5}, {"id": 6, "x": 9, "y": 9}]

    fa.insert.insert_records("xy", new_records, engine)

    results = fa.select.select_records_all(table)
    expected = [
        {"id": 1, "x": 1, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 11},
        {"id": 5, "x": 11, "y": 5},
        {"id": 6, "x": 9, "y": 9},
    ]
    assert records_equal(results, expected)


def test_insert_records_no_engine(engine_and_table):
    """Test inserting records without explicitly passing engine."""
    _engine, table = engine_and_table
    new_records = [{"id": 5, "x": 11, "y": 5}, {"id": 6, "x": 9, "y": 9}]

    fa.insert.insert_records(table, new_records)

    results = fa.select.select_records_all(table)
    expected = [
        {"id": 1, "x": 1, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 11},
        {"id": 5, "x": 11, "y": 5},
        {"id": 6, "x": 9, "y": 9},
    ]
    assert records_equal(results, expected)


def test_insert_from_table_missing_engine():
    """Test insert_from_table raises error when table is string without engine."""
    with pytest.raises(ValueError, match="Must provide engine when table1 is a string"):
        fa.insert.insert_from_table("table1", "table2", engine=None)


def test_insert_into_table_without_primary_key(engine_and_table):
    """Test inserting into a table without primary key uses slow path."""
    engine, _ = engine_and_table

    # Create a table without primary key
    table_no_pk = fa.create.create_table(
        table_name="no_pk_table",
        column_names=["a", "b"],
        column_types=[int, str],
        primary_key=[],  # No primary key
        engine=engine,
        if_exists="replace",
    )

    # Insert records
    records = [{"a": 1, "b": "hello"}, {"a": 2, "b": "world"}]
    session = fa.features.get_session(engine)
    fa.insert.insert_records_session(table_no_pk, records, session)
    session.commit()

    # Verify inserted
    results = fa.select.select_records_all(table_no_pk, engine)
    assert len(results) == 2


def test_insert_from_table_rollback_on_error(engine_and_table):
    """Test insert_from_table rolls back on commit error."""
    engine, table1 = engine_and_table
    from unittest.mock import patch

    # Create second table
    table2 = fa.create.create_table(
        "xyz", ["id", "x", "y", "z"], [int, int, int, int], ["id"], engine, if_exists="replace"
    )

    with patch("sqlalchemy.orm.session.Session.commit", side_effect=RuntimeError("DB Error")):
        try:
            fa.insert.insert_from_table(table1, table2, engine)
        except RuntimeError:
            pass

    # Verify rollback - table2 should be empty
    results = fa.select.select_records_all(table2, engine)
    assert len(results) == 0


def test_insert_records_rollback_on_error(engine_and_table):
    """Test insert_records rolls back on commit error."""
    engine, table = engine_and_table
    from unittest.mock import patch

    new_records = [{"id": 5, "x": 10, "y": 20}]

    with patch("sqlalchemy.orm.session.Session.commit", side_effect=RuntimeError("DB Error")):
        try:
            fa.insert.insert_records(table, new_records, engine)
        except RuntimeError:
            pass

    # Verify rollback - no new records
    results = fa.select.select_records_all(table, engine)
    assert len(results) == 4  # Original count


def test_insert_records_fast_missing_primary_key_error():
    """Test _insert_records_fast raises error when table has no primary key."""
    import sqlalchemy as sa

    from fullmetalalchemy.exceptions import MissingPrimaryKeyError

    engine = sa.create_engine("sqlite://")
    # Create table without primary key
    table_no_pk = fa.create.create_table(
        "no_pk_fast",
        ["a", "b"],
        [int, str],
        [],  # No primary key
        engine,
        if_exists="replace",
    )

    records = [{"a": 1, "b": "test"}]

    # _insert_records_fast should raise MissingPrimaryKey
    with pytest.raises((MissingPrimaryKeyError, ValueError)):
        fa.insert._insert_records_fast(table_no_pk, records, engine)


def test_insert_records_fast_rollback_on_error(engine_and_table):
    """Test _insert_records_fast rolls back on error."""
    from unittest.mock import patch

    engine, table = engine_and_table

    new_records = [{"id": 5, "x": 10, "y": 20}]

    with patch("sqlalchemy.orm.session.Session.commit", side_effect=RuntimeError("DB Error")):
        try:
            fa.insert._insert_records_fast(table, new_records, engine)
        except RuntimeError:
            pass

    # Verify rollback
    results = fa.select.select_records_all(table, engine)
    assert len(results) == 4


def test_insert_records_fast_session_missing_pk_error():
    """Test _insert_records_fast_session raises error when table has no primary key."""
    import sqlalchemy as sa

    from fullmetalalchemy.exceptions import MissingPrimaryKeyError

    engine = sa.create_engine("sqlite://")
    # Create table without primary key
    table_no_pk = fa.create.create_table(
        "no_pk_fast_session",
        ["a", "b"],
        [int, str],
        [],  # No primary key
        engine,
        if_exists="replace",
    )

    session = fa.features.get_session(engine)
    records = [{"a": 1, "b": "test"}]

    # _insert_records_fast_session should raise MissingPrimaryKey
    with pytest.raises(MissingPrimaryKeyError):
        fa.insert._insert_records_fast_session(table_no_pk, records, session)
