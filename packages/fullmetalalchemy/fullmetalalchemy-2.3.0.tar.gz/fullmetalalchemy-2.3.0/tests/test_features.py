import sqlalchemy as sa
from sqlalchemy import INTEGER, MetaData, Table
from sqlalchemy.engine import Engine
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.orm.session import Session

from fullmetalalchemy.features import (
    get_class,
    get_connection,
    get_engine_table,
    get_metadata,
    get_session,
    get_table,
    primary_key_columns,
    primary_key_names,
)
from fullmetalalchemy.test_setup import create_test_table, insert_test_records


def test_primary_key_columns(engine_and_table):
    """Test getting primary key columns from a table."""
    _engine, table = engine_and_table
    results = primary_key_columns(table)
    names = [c.name for c in results]
    types = [type(c.type) for c in results]
    assert names == ["id"]
    assert types == [INTEGER]


def test_primary_key_names(engine_and_table):
    """Test getting primary key column names from a table."""
    _engine, table = engine_and_table
    results = primary_key_names(table)
    assert results == ["id"]


def test_get_connection(engine_and_table):
    """Test getting a connection from a session."""
    engine, _table = engine_and_table
    session = get_session(engine)
    con = get_connection(session)
    assert isinstance(con, Connection)


def test_get_session(engine_and_table):
    """Test creating a session from an engine."""
    engine, _table = engine_and_table
    session = get_session(engine)
    assert isinstance(session, Session)


def test_get_metadata(engine_and_table):
    """Test getting metadata from an engine."""
    engine, _table = engine_and_table
    meta = get_metadata(engine)
    assert isinstance(meta, MetaData)


def test_get_table(engine_and_table):
    """Test getting a table object by name."""
    engine, _table = engine_and_table
    result_table = get_table("xy", engine)
    results = result_table.name, result_table.info.get("engine"), type(result_table)
    expected = "xy", engine, Table
    assert results == expected


def test_get_engine_table():
    """Test getting engine and table from connection string."""
    con_str = "sqlite:///data/test.db"
    engine = sa.create_engine(con_str)
    table = create_test_table(engine)
    insert_test_records(table, engine)

    results = get_engine_table(con_str, "xy")
    results = tuple(type(x) for x in results)
    expected = Engine, Table
    assert results == expected


def test_get_class(engine_and_table):
    """Test getting automap class from table name."""
    engine, _table = engine_and_table
    result = get_class("xy", engine)
    assert isinstance(type(result), type(DeclarativeMeta))
