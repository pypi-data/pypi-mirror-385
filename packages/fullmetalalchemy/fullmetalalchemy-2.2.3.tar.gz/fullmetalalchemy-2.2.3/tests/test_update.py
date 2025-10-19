from unittest.mock import patch

import fullmetalalchemy as fa
from fullmetalalchemy.records import records_equal


def test_update_matching_records_session(engine_and_table):
    """Test updating records by matching columns using session."""
    engine, table = engine_and_table
    session = fa.features.get_session(engine)
    updated_records = [{"id": 1, "x": 11}, {"id": 4, "y": 111}]
    fa.update.update_matching_records_session(table, updated_records, ["id"], session)
    session.commit()

    expected = [
        {"id": 1, "x": 11, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 111},
    ]
    results = fa.select.select_records_all(table)
    assert records_equal(results, expected)


def test_update_matching_records_session_table_name(engine_and_table):
    """Test updating records using session with table name."""
    engine, table = engine_and_table
    session = fa.features.get_session(engine)
    updated_records = [{"id": 1, "x": 11}, {"id": 4, "y": 111}]
    fa.update.update_matching_records_session("xy", updated_records, ["id"], session)
    session.commit()

    expected = [
        {"id": 1, "x": 11, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 111},
    ]
    results = fa.select.select_records_all(table)
    assert records_equal(results, expected)


def test_update_matching_records(engine_and_table):
    """Test updating records by matching columns."""
    engine, table = engine_and_table
    updated_records = [{"id": 1, "x": 11}, {"id": 4, "y": 111}]
    fa.update.update_matching_records(table, updated_records, ["id"], engine)

    expected = [
        {"id": 1, "x": 11, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 111},
    ]
    results = fa.select.select_records_all(table)
    assert records_equal(results, expected)


def test_update_matching_records_table_name(engine_and_table):
    """Test updating records using table name."""
    engine, table = engine_and_table
    updated_records = [{"id": 1, "x": 11}, {"id": 4, "y": 111}]
    fa.update.update_matching_records("xy", updated_records, ["id"], engine)

    expected = [
        {"id": 1, "x": 11, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 111},
    ]
    results = fa.select.select_records_all(table)
    assert records_equal(results, expected)


def test_update_matching_records_no_engine(engine_and_table):
    """Test updating records without explicitly passing engine."""
    _engine, table = engine_and_table
    updated_records = [{"id": 1, "x": 11}, {"id": 4, "y": 111}]
    fa.update.update_matching_records(table, updated_records, ["id"])

    expected = [
        {"id": 1, "x": 11, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 111},
    ]
    results = fa.select.select_records_all(table)
    assert records_equal(results, expected)


def test_update_records_session(engine_and_table):
    """Test updating records using session."""
    engine, table = engine_and_table
    session = fa.features.get_session(engine)
    updated_records = [{"id": 1, "x": 11}, {"id": 4, "y": 111}]
    fa.update.update_records_session(table, updated_records, session)
    session.commit()

    expected = [
        {"id": 1, "x": 11, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 111},
    ]
    results = fa.select.select_records_all(table)
    assert records_equal(results, expected)


def test_update_records_session_table_name(engine_and_table):
    """Test updating records using session with table name."""
    engine, table = engine_and_table
    session = fa.features.get_session(engine)
    updated_records = [{"id": 1, "x": 11}, {"id": 4, "y": 111}]
    fa.update.update_records_session("xy", updated_records, session)
    session.commit()

    expected = [
        {"id": 1, "x": 11, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 111},
    ]
    results = fa.select.select_records_all(table)
    assert records_equal(results, expected)


def test_update_records(engine_and_table):
    """Test updating records with engine."""
    engine, table = engine_and_table
    updated_records = [{"id": 1, "x": 11}, {"id": 4, "y": 111}]
    fa.update.update_records(table, updated_records, engine)

    expected = [
        {"id": 1, "x": 11, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 111},
    ]
    results = fa.select.select_records_all(table)
    assert records_equal(results, expected)


def test_update_records_table_name(engine_and_table):
    """Test updating records using table name."""
    engine, table = engine_and_table
    updated_records = [{"id": 1, "x": 11}, {"id": 4, "y": 111}]
    fa.update.update_records("xy", updated_records, engine)

    expected = [
        {"id": 1, "x": 11, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 111},
    ]
    results = fa.select.select_records_all(table)
    assert records_equal(results, expected)


def test_update_records_no_engine(engine_and_table):
    """Test updating records without explicitly passing engine."""
    _engine, table = engine_and_table
    updated_records = [{"id": 1, "x": 11}, {"id": 4, "y": 111}]
    fa.update.update_records(table, updated_records)

    expected = [
        {"id": 1, "x": 11, "y": 2},
        {"id": 2, "x": 2, "y": 4},
        {"id": 3, "x": 4, "y": 8},
        {"id": 4, "x": 8, "y": 111},
    ]
    results = fa.select.select_records_all(table)
    assert records_equal(results, expected)


def test_set_column_values_session(engine_and_table):
    """Test setting all values in a column using session."""
    engine, table = engine_and_table
    session = fa.features.get_session(engine)
    new_value = 1
    fa.update.set_column_values_session(table, "x", new_value, session)
    session.commit()

    expected = [
        {"id": 1, "x": 1, "y": 2},
        {"id": 2, "x": 1, "y": 4},
        {"id": 3, "x": 1, "y": 8},
        {"id": 4, "x": 1, "y": 11},
    ]
    results = fa.select.select_records_all(table)
    assert records_equal(results, expected)


def test_set_column_values_session_table_name(engine_and_table):
    """Test setting column values using session with table name."""
    engine, table = engine_and_table
    session = fa.features.get_session(engine)
    new_value = 1
    fa.update.set_column_values_session("xy", "x", new_value, session)
    session.commit()

    expected = [
        {"id": 1, "x": 1, "y": 2},
        {"id": 2, "x": 1, "y": 4},
        {"id": 3, "x": 1, "y": 8},
        {"id": 4, "x": 1, "y": 11},
    ]
    results = fa.select.select_records_all(table)
    assert records_equal(results, expected)


def test_set_column_values(engine_and_table):
    """Test setting all values in a column."""
    engine, table = engine_and_table
    new_value = 1
    fa.update.set_column_values(table, "x", new_value, engine)

    expected = [
        {"id": 1, "x": 1, "y": 2},
        {"id": 2, "x": 1, "y": 4},
        {"id": 3, "x": 1, "y": 8},
        {"id": 4, "x": 1, "y": 11},
    ]
    results = fa.select.select_records_all(table)
    assert records_equal(results, expected)


def test_set_column_values_table_name(engine_and_table):
    """Test setting column values using table name."""
    engine, table = engine_and_table
    new_value = 1
    fa.update.set_column_values("xy", "x", new_value, engine)

    expected = [
        {"id": 1, "x": 1, "y": 2},
        {"id": 2, "x": 1, "y": 4},
        {"id": 3, "x": 1, "y": 8},
        {"id": 4, "x": 1, "y": 11},
    ]
    results = fa.select.select_records_all(table)
    assert records_equal(results, expected)


def test_set_column_values_no_engine(engine_and_table):
    """Test setting column values without explicitly passing engine."""
    _engine, table = engine_and_table
    new_value = 1
    fa.update.set_column_values(table, "x", new_value)

    expected = [
        {"id": 1, "x": 1, "y": 2},
        {"id": 2, "x": 1, "y": 4},
        {"id": 3, "x": 1, "y": 8},
        {"id": 4, "x": 1, "y": 11},
    ]
    results = fa.select.select_records_all(table)
    assert records_equal(results, expected)


def test_update_matching_records_rollback_on_error(engine_and_table):
    """Test update_matching_records rolls back on commit error."""
    engine, table = engine_and_table
    records = [{"id": 1, "x": 99}]

    # Mock session.commit to raise an exception
    with patch("sqlalchemy.orm.session.Session.commit", side_effect=RuntimeError("DB Error")):
        try:
            fa.update.update_matching_records(table, records, ["id"], engine)
        except RuntimeError:
            pass  # Expected

    # Verify rollback occurred - data should be unchanged
    results = fa.select.select_records_all(table)
    assert results[0]["x"] == 1  # Original value


def test_update_records_rollback_on_error(engine_and_table):
    """Test update_records rolls back on commit error."""
    engine, table = engine_and_table
    records = [{"id": 1, "x": 100}]

    with patch("sqlalchemy.orm.session.Session.commit", side_effect=RuntimeError("DB Error")):
        try:
            fa.update.update_records(table, records, engine)
        except RuntimeError:
            pass

    # Verify rollback - data unchanged
    results = fa.select.select_records_all(table)
    assert results[0]["x"] == 1


def test_set_column_values_rollback_on_error(engine_and_table):
    """Test set_column_values rolls back on commit error."""
    engine, table = engine_and_table

    with patch("sqlalchemy.orm.session.Session.commit", side_effect=RuntimeError("DB Error")):
        try:
            fa.update.set_column_values(table, "x", 999, engine)
        except RuntimeError:
            pass

    # Verify rollback - data unchanged
    results = fa.select.select_records_all(table)
    assert results[0]["x"] == 1


def test_update_records_session_no_pk_no_match_columns(engine_and_table):
    """Test update_records_session raises error when table has no PK and no match_column_names."""
    import pytest

    engine, _ = engine_and_table

    # Create table without primary key
    table_no_pk = fa.create.create_table(
        "no_pk_update",
        ["a", "b"],
        [int, str],
        [],  # No primary key
        engine,
        if_exists="replace",
    )

    session = fa.features.get_session(engine)
    records = [{"a": 1, "b": "updated"}]

    with pytest.raises(
        ValueError, match="Must provide match_column_names if table has no primary key"
    ):
        fa.update.update_records_session(table_no_pk, records, session)


def test_update_records_session_no_pk_with_match_columns(engine_and_table):
    """Test update_records_session works when table has no PK but match_columns provided."""
    engine, _ = engine_and_table

    # Create and populate table without primary key
    table_no_pk = fa.create.create_table(
        "no_pk_update2",
        ["a", "b"],
        [int, str],
        [],  # No primary key
        engine,
        if_exists="replace",
    )
    fa.insert.insert_records(table_no_pk, [{"a": 1, "b": "original"}], engine)

    session = fa.features.get_session(engine)
    records = [{"a": 1, "b": "updated"}]

    # Should work with match_column_names
    fa.update.update_records_session(table_no_pk, records, session, match_column_names=["a"])
    session.commit()

    results = fa.select.select_records_all(table_no_pk, engine)
    assert results[0]["b"] == "updated"
