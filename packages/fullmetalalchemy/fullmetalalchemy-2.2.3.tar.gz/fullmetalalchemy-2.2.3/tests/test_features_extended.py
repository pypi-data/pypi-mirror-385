"""Extended tests for features module to cover error paths and edge cases."""

import pytest
import sqlalchemy as sa

import fullmetalalchemy as fa
from fullmetalalchemy.features import (
    _extract_engine,
    get_engine,
    missing_primary_key,
    str_to_table,
)


def test_extract_engine_with_engine():
    """Test _extract_engine with Engine."""
    engine = sa.create_engine("sqlite://")
    result = _extract_engine(engine)
    assert result is engine


def test_extract_engine_with_connection():
    """Test _extract_engine with Connection."""
    engine = sa.create_engine("sqlite://")
    with engine.connect() as conn:
        result = _extract_engine(conn)
        assert isinstance(result, sa.engine.Engine)


def test_extract_engine_with_session():
    """Test _extract_engine with Session."""
    engine = sa.create_engine("sqlite://")
    session = sa.orm.Session(engine)
    result = _extract_engine(session)
    assert isinstance(result, sa.engine.Engine)


def test_extract_engine_with_unbound_session():
    """Test _extract_engine with unbound Session raises error."""
    session = sa.orm.Session()
    with pytest.raises((TypeError, sa.exc.UnboundExecutionError)):
        _extract_engine(session)


def test_extract_engine_with_invalid_type():
    """Test _extract_engine with invalid type raises TypeError."""
    with pytest.raises(TypeError, match="Unsupported connection type"):
        _extract_engine("not_a_connection")  # type: ignore


def test_get_engine_with_invalid_type():
    """Test get_engine with invalid type raises TypeError."""
    with pytest.raises(TypeError, match="connection must be an Engine, Connection, or Session"):
        get_engine("invalid")  # type: ignore


def test_missing_primary_key_table_with_pk(engine_and_table):
    """Test missing_primary_key returns False for table with primary key."""
    _, table = engine_and_table
    assert not missing_primary_key(table)


def test_missing_primary_key_table_without_pk():
    """Test missing_primary_key returns True for table without primary key."""
    engine = sa.create_engine("sqlite://")
    table = fa.create.create_table(
        table_name="no_pk",
        column_names=["a", "b"],
        column_types=[int, str],
        primary_key=[],  # No primary key
        engine=engine,
        if_exists="replace",
    )
    assert missing_primary_key(table)


def test_str_to_table_with_string(engine_and_table):
    """Test str_to_table converts string to table."""
    engine, _ = engine_and_table
    session = sa.orm.Session(engine)
    table = str_to_table("xy", session)
    assert isinstance(table, sa.Table)
    assert table.name == "xy"


def test_str_to_table_with_table_object(engine_and_table):
    """Test str_to_table returns table object unchanged."""
    engine, table = engine_and_table
    session = sa.orm.Session(engine)
    result = str_to_table(table, session)
    assert result is table


def test_get_table_names(engine_and_table):
    """Test get_table_names returns list of table names."""
    engine, _ = engine_and_table
    names = fa.get_table_names(engine)
    assert isinstance(names, list)
    assert "xy" in names


def test_get_table_with_string(engine_and_table):
    """Test get_table with string table name."""
    engine, _ = engine_and_table
    table = fa.get_table("xy", engine)
    assert isinstance(table, sa.Table)
    assert table.name == "xy"


def test_get_column(engine_and_table):
    """Test get_column retrieves a column from table."""
    _, table = engine_and_table
    column = fa.features.get_column(table, "x")
    assert column.name == "x"


def test_get_column_types(engine_and_table):
    """Test get_column_types returns dict of column types."""
    _, table = engine_and_table
    col_types = fa.features.get_column_types(table)
    assert isinstance(col_types, dict)
    assert "id" in col_types
    assert "x" in col_types
    assert "y" in col_types


def test_execution_context_with_session(engine_and_table):
    """Test execution_context with Session."""
    from fullmetalalchemy.features import execution_context

    engine, _ = engine_and_table
    session = sa.orm.Session(engine)

    with execution_context(session) as ctx:
        assert isinstance(ctx, sa.orm.session.Session)


def test_execution_context_with_connection(engine_and_table):
    """Test execution_context with Connection."""
    from fullmetalalchemy.features import execution_context

    engine, _ = engine_and_table

    with engine.connect() as conn:
        with execution_context(conn) as ctx:
            assert isinstance(ctx, sa.engine.Connection)


def test_execution_context_with_engine(engine_and_table):
    """Test execution_context with Engine."""
    from fullmetalalchemy.features import execution_context

    engine, _ = engine_and_table

    with execution_context(engine) as ctx:
        assert isinstance(ctx, sa.engine.Connection)


def test_execution_context_with_invalid_type():
    """Test execution_context raises error with invalid type."""
    import pytest

    from fullmetalalchemy.features import execution_context

    with pytest.raises(TypeError, match="Unsupported connection type"):
        with execution_context("invalid"):  # type: ignore
            pass


def test_ensure_connection_with_session(engine_and_table):
    """Test _ensure_connection with Session returns connection."""
    from fullmetalalchemy.features import _ensure_connection

    engine, _ = engine_and_table
    session = sa.orm.Session(engine)

    result = _ensure_connection(session)
    # Session.connection() returns a connection
    assert result is not None


def test_get_primary_key_constraints(engine_and_table):
    """Test get_primary_key_constraints returns constraint info."""
    _, table = engine_and_table
    _pk_name, pk_cols = fa.features.get_primary_key_constraints(table)
    assert pk_cols == ["id"]


def test_get_table_constraints(engine_and_table):
    """Test get_table_constraints returns all constraints."""
    _, table = engine_and_table
    constraints = fa.features.get_table_constraints(table)
    assert constraints is not None


def test_extract_engine_with_connection_bound_session(engine_and_table):
    """Test _extract_engine with Session bound to Connection."""
    engine, _ = engine_and_table

    # Create a session bound to a connection
    with engine.connect() as conn:
        session = sa.orm.Session(bind=conn)
        result = _extract_engine(session)
        assert isinstance(result, sa.engine.Engine)


def test_extract_engine_with_engine_bound_session(engine_and_table):
    """Test _extract_engine with Session bound to Engine."""
    engine, _ = engine_and_table

    # Create a session bound directly to an engine
    session = sa.orm.Session(bind=engine)
    result = _extract_engine(session)
    assert isinstance(result, sa.engine.Engine)
    assert result is engine


def test_ensure_connection_returns_engine_or_connection(engine_and_table):
    """Test _ensure_connection with Engine."""
    from fullmetalalchemy.features import _ensure_connection

    engine, _ = engine_and_table

    result = _ensure_connection(engine)
    assert result is engine


def test_ensure_connection_returns_connection_from_connection(engine_and_table):
    """Test _ensure_connection with Connection returns Connection."""
    from fullmetalalchemy.features import _ensure_connection

    engine, _ = engine_and_table

    with engine.connect() as conn:
        result = _ensure_connection(conn)
        assert result is conn


def test_get_class_with_existing_table(engine_and_table):
    """Test get_class successfully gets class for existing table."""
    engine, _ = engine_and_table

    # get_class should work with existing table
    table_class = fa.features.get_class("xy", engine)
    assert table_class is not None
    # Automap classes have __name__ attribute
    assert "xy" in str(table_class)
