"""Tests for exceptions module."""
import pytest
import sqlalchemy as sa

from fullmetalalchemy.exceptions import (
    MissingPrimaryKeyError,
    SliceError,
    check_for_engine,
)


def test_missing_primary_key_error_with_table_name():
    """Test MissingPrimaryKeyError with table name."""
    error = MissingPrimaryKeyError('my_table')
    assert 'my_table' in str(error)


def test_slice_error():
    """Test SliceError exception."""
    error = SliceError('Test slice error')
    assert 'Test slice error' in str(error)


def test_check_for_engine_with_none_no_bind():
    """Test check_for_engine raises error when no engine found."""
    # Create a table without binding
    metadata = sa.MetaData()
    table = sa.Table('test', metadata, sa.Column('id', sa.Integer, primary_key=True))

    with pytest.raises(ValueError, match='sa_table must be bound to engine'):
        check_for_engine(table, None)


def test_check_for_engine_extracts_from_connection(engine_and_table):
    """Test check_for_engine extracts engine from connection."""
    engine, table = engine_and_table

    with engine.connect() as conn:
        extracted_engine = check_for_engine(table, conn)
        assert isinstance(extracted_engine, sa.engine.Engine)


def test_check_for_engine_with_engine(engine_and_table):
    """Test check_for_engine returns engine when passed directly."""
    engine, table = engine_and_table

    result = check_for_engine(table, engine)
    assert result is engine


def test_check_for_engine_from_table_info(engine_and_table):
    """Test check_for_engine gets engine from table.info."""
    engine, _ = engine_and_table

    # Create a table with engine in info
    metadata = sa.MetaData()
    table = sa.Table('test2', metadata, sa.Column('id', sa.Integer, primary_key=True))
    table.info['engine'] = engine

    result = check_for_engine(table, None)
    assert result is engine


def test_convert_table_connection_with_session(engine_and_table):
    """Test convert_table_connection with Session connection type."""
    from fullmetalalchemy.exceptions import convert_table_connection
    engine, table = engine_and_table
    session = sa.orm.Session(engine)

    result_table, result_conn = convert_table_connection(table, session)
    assert result_table is table
    assert result_conn is session

