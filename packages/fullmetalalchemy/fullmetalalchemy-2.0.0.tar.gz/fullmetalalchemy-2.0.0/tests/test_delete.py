from unittest.mock import patch

import sqlalchemy.orm.session as sa_session

from fullmetalalchemy.delete import (
    delete_all_records,
    delete_all_records_session,
    delete_records,
    delete_records_by_values,
    delete_records_by_values_session,
    delete_records_session,
)
from fullmetalalchemy.records import records_equal
from fullmetalalchemy.select import select_records_all


def test_delete_all(engine_and_table):
    """Test deleting all records from a table."""
    engine, table = engine_and_table
    delete_all_records(table, engine)
    results = select_records_all(table, engine)
    assert records_equal(results, [])


def test_delete_all_table_name(engine_and_table):
    """Test deleting all records using table name."""
    engine, table = engine_and_table
    delete_all_records('xy', engine)
    results = select_records_all(table, engine)
    assert records_equal(results, [])


def test_delete_all_no_engine(engine_and_table):
    """Test deleting all records without explicitly passing engine."""
    engine, table = engine_and_table
    delete_all_records(table)
    results = select_records_all(table, engine)
    assert records_equal(results, [])


def test_delete_all_session(engine_and_table):
    """Test deleting all records using a session."""
    engine, table = engine_and_table
    session = sa_session.Session(engine)
    delete_all_records_session(table, session)
    results = select_records_all(table, engine)
    assert records_equal(results, [])


def test_delete_all_session_table_name(engine_and_table):
    """Test deleting all records using session with table name."""
    engine, table = engine_and_table
    session = sa_session.Session(engine)
    delete_all_records_session('xy', session)
    results = select_records_all(table, engine)
    assert records_equal(results, [])


def test_delete_records_session(engine_and_table):
    """Test deleting specific records using session."""
    engine, table = engine_and_table
    session = sa_session.Session(engine)
    delete_records_session(table, 'id', [1], session)
    session.commit()
    results = select_records_all(table, engine)
    expected = [
        {'id': 2, 'x': 2, 'y': 4},
        {'id': 3, 'x': 4, 'y': 8},
        {'id': 4, 'x': 8, 'y': 11}
    ]
    assert records_equal(results, expected)


def test_delete_records_session_table_name(engine_and_table):
    """Test deleting records using session with table name."""
    engine, table = engine_and_table
    session = sa_session.Session(engine)
    delete_records_session('xy', 'id', [1], session)
    session.commit()
    results = select_records_all(table, engine)
    expected = [
        {'id': 2, 'x': 2, 'y': 4},
        {'id': 3, 'x': 4, 'y': 8},
        {'id': 4, 'x': 8, 'y': 11}
    ]
    assert records_equal(results, expected)


def test_delete_records(engine_and_table):
    """Test deleting records by column values."""
    engine, table = engine_and_table
    delete_records(table, 'id', [1], engine)
    results = select_records_all(table, engine)
    expected = [
        {'id': 2, 'x': 2, 'y': 4},
        {'id': 3, 'x': 4, 'y': 8},
        {'id': 4, 'x': 8, 'y': 11}
    ]
    assert records_equal(results, expected)


def test_delete_records_table_name(engine_and_table):
    """Test deleting records using table name."""
    engine, table = engine_and_table
    delete_records('xy', 'id', [1], engine)
    results = select_records_all(table, engine)
    expected = [
        {'id': 2, 'x': 2, 'y': 4},
        {'id': 3, 'x': 4, 'y': 8},
        {'id': 4, 'x': 8, 'y': 11}
    ]
    assert records_equal(results, expected)


def test_delete_records_no_engine(engine_and_table):
    """Test deleting records without explicitly passing engine."""
    engine, table = engine_and_table
    delete_records(table, 'id', [1])
    results = select_records_all(table, engine)
    expected = [
        {'id': 2, 'x': 2, 'y': 4},
        {'id': 3, 'x': 4, 'y': 8},
        {'id': 4, 'x': 8, 'y': 11}
    ]
    assert records_equal(results, expected)


def test_delete_records_by_values(engine_and_table):
    """Test deleting records by matching field values."""
    engine, table = engine_and_table
    delete_records_by_values(table, [{'id': 3}, {'x': 2}], engine)
    results = select_records_all(table, engine)
    expected = [{'id': 1, 'x': 1, 'y': 2},
                {'id': 4, 'x': 8, 'y': 11}]
    assert records_equal(results, expected)


def test_delete_records_by_values_no_engine(engine_and_table):
    """Test deleting records by values without explicitly passing engine."""
    engine, table = engine_and_table
    delete_records_by_values(table, [{'id': 3}, {'x': 2}])
    results = select_records_all(table, engine)
    expected = [{'id': 1, 'x': 1, 'y': 2},
                {'id': 4, 'x': 8, 'y': 11}]
    assert records_equal(results, expected)


def test_delete_records_by_values_table_name(engine_and_table):
    """Test deleting records by values using table name."""
    engine, table = engine_and_table
    delete_records_by_values('xy', [{'id': 3}, {'x': 2}], engine)
    results = select_records_all(table, engine)
    expected = [{'id': 1, 'x': 1, 'y': 2},
                {'id': 4, 'x': 8, 'y': 11}]
    assert records_equal(results, expected)


def test_delete_records_by_values_session(engine_and_table):
    """Test deleting records by values using a session."""
    engine, table = engine_and_table
    session = sa_session.Session(engine)
    delete_records_by_values_session(table, [{'id': 3}, {'x': 2}], session)
    results = select_records_all(table, engine)
    expected = [{'id': 1, 'x': 1, 'y': 2},
                {'id': 4, 'x': 8, 'y': 11}]
    assert records_equal(results, expected)


def test_delete_records_by_values_session_table_name(engine_and_table):
    """Test deleting records by values using session with table name."""
    engine, table = engine_and_table
    session = sa_session.Session(engine)
    delete_records_by_values_session('xy', [{'id': 3}, {'x': 2}], session)
    results = select_records_all(table, engine)
    expected = [{'id': 1, 'x': 1, 'y': 2},
                {'id': 4, 'x': 8, 'y': 11}]
    assert records_equal(results, expected)


def test_delete_records_rollback_on_error(engine_and_table):
    """Test delete_records rolls back on commit error."""
    engine, table = engine_and_table

    with patch('sqlalchemy.orm.session.Session.commit', side_effect=RuntimeError("DB Error")):
        try:
            delete_records(table, 'id', [1], engine)
        except RuntimeError:
            pass

    # Verify rollback - data unchanged
    results = select_records_all(table, engine)
    assert len(results) == 4  # All records still there


def test_delete_records_by_values_rollback_on_error(engine_and_table):
    """Test delete_records_by_values rolls back on commit error."""
    engine, table = engine_and_table

    with patch('sqlalchemy.orm.session.Session.commit', side_effect=RuntimeError("DB Error")):
        try:
            delete_records_by_values(table, [{'id': 2}], engine)
        except RuntimeError:
            pass

    # Verify rollback
    results = select_records_all(table, engine)
    assert len(results) == 4


def test_delete_all_records_rollback_on_error(engine_and_table):
    """Test delete_all_records rolls back on commit error."""
    engine, table = engine_and_table

    with patch('sqlalchemy.orm.session.Session.commit', side_effect=RuntimeError("DB Error")):
        try:
            delete_all_records(table, engine)
        except RuntimeError:
            pass

    # Verify rollback
    results = select_records_all(table, engine)
    assert len(results) == 4
