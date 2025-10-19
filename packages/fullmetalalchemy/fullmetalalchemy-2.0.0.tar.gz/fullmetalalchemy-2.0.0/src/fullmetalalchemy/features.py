"""
Functions for getting SQL table features and SqlAlchemy ORM objects.
"""

import typing as _t
from contextlib import contextmanager

import sqlalchemy as _sa
import sqlalchemy.engine as _sa_engine
import sqlalchemy.ext.automap as _sa_automap
import sqlalchemy.orm.session as _sa_session
from sqlalchemy.orm.decl_api import DeclarativeMeta as _DeclarativeMeta

import fullmetalalchemy.exceptions as _ex
import fullmetalalchemy.types as _types


def _extract_engine(
    connection: _t.Union[_sa_engine.Engine, _sa.engine.Connection, _sa_session.Session]
) -> _sa_engine.Engine:
    if isinstance(connection, _sa_engine.Engine):
        return connection
    if isinstance(connection, _sa.engine.Connection):
        return connection.engine
    if isinstance(connection, _sa_session.Session):
        bind = connection.get_bind()
        if bind is None:
            raise TypeError('Session is not bound to an engine or connection.')
        if isinstance(bind, _sa.engine.Connection):
            return bind.engine
        if isinstance(bind, _sa_engine.Engine):
            return bind
        raise TypeError('Unsupported bind object returned from session.')
    raise TypeError('Unsupported connection type provided.')


def get_engine(
    connection: _t.Union[_sa_engine.Engine, _sa.engine.Connection, _sa_session.Session]
) -> _sa_engine.Engine:
    if isinstance(connection, (_sa_engine.Engine, _sa.engine.Connection, _sa_session.Session)):
        return _extract_engine(connection)
    raise TypeError('connection must be an Engine, Connection, or Session instance.')


def _ensure_connection(
    connection: _t.Union[_types.SqlConnection, _sa_session.Session]
) -> _types.SqlConnection:
    if isinstance(connection, (_sa.engine.Connection, _sa_engine.Engine)):
        return connection
    if isinstance(connection, _sa_session.Session):
        return connection.connection()
    return connection


@contextmanager
def execution_context(
    connection: _t.Union[_sa_engine.Engine, _sa.engine.Connection, _sa_session.Session]
) -> _t.Iterator[_t.Union[_sa.engine.Connection, _sa_session.Session]]:
    if isinstance(connection, _sa_session.Session):
        yield connection
        return
    if isinstance(connection, _sa.engine.Connection):
        try:
            yield connection
        finally:
            pass
        return
    if isinstance(connection, _sa_engine.Engine):
        with connection.connect() as conn:
            yield conn
        return
    raise TypeError('Unsupported connection type provided to execution_context.')


def primary_key_columns(
    table: _sa.Table
) ->  _t.List[_sa.Column[_t.Any]]:
    """
    Return the primary key columns of a SQLAlchemy Table.

    Parameters
    ----------
    table : sqlalchemy.Table
        The table whose primary key columns will be returned.

    Returns
    -------
    List of sqlalchemy.Column
        The list of primary key columns for the input table.

    Examples
    --------
    >>> import fullmetalalchemy as fa
    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.features.primary_key_columns(table)
    [Column('id', INTEGER(), table=<xy>, primary_key=True, nullable=False)]
    """
    return list(table.primary_key.columns)


def primary_key_names(
    table: _sa.Table
) ->  _t.List[str]:
    """
    Return the names of the primary key columns of a SQLAlchemy Table.

    Parameters
    ----------
    table : sqlalchemy.Table
        The table whose primary key column names will be returned.

    Returns
    -------
    List of str
        The list of primary key column names for the input table.

    Examples
    --------
    >>> import fullmetalalchemy as fa
    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.features.primary_key_names(table)
    ['id']
    """
    return [c.name for c in primary_key_columns(table)]


def get_connection(
    connection: _t.Union[_types.SqlConnection, _sa_session.Session]
) -> _types.SqlConnection:
    return _ensure_connection(connection)


def get_metadata(
    connection: _types.SqlConnection,
    schema: _t.Optional[str] = None
) -> _sa.MetaData:
    return _sa.MetaData(schema=schema)


def get_table(
    table_name: str,
    connection: _types.SqlConnection,
    schema: _t.Optional[str] = None
) -> _sa.Table:
    engine = get_engine(connection)
    metadata = get_metadata(engine, schema)
    table = _sa.Table(table_name, metadata, autoload_with=engine, schema=schema)
    table.info.setdefault('engine', engine)
    return table


def get_engine_table(
    connection_string: str,
    table_name: str,
    schema: _t.Optional[str] = None
) -> _t.Tuple[_sa_engine.Engine, _sa.Table]:
    """
    Get the engine and table objects from a given connection string,
    table name, and optional schema.

    Parameters
    ----------
    connection_string : str
        The connection string to the database.
    table_name : str
        The name of the table to get.
    schema : str, optional
        The name of the schema the table belongs to.

    Returns
    -------
    Tuple[Engine, Table]
        The SQLAlchemy engine and table objects.

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> assert isinstance(engine, _sa_engine.Engine)
    >>> assert isinstance(table, _sa.Table)
    """
    engine = _sa.create_engine(connection_string)
    table = get_table(table_name, engine, schema)
    return engine, table


def get_class(
    table_name: str,
    connection: _t.Union[_types.SqlConnection, _sa_session.Session],
    schema: _t.Optional[str] = None
) -> _DeclarativeMeta:
    """
    Reflects the specified table and returns a declarative class that corresponds to it.

    Parameters
    ----------
    table_name : str
        The name of the table to reflect.
    connection : Union[SqlConnection, Session]
        The connection to use to reflect the table. This can be either an `SqlConnection`
        or an active `Session` object.
    schema : Optional[str], optional
        The name of the schema to which the table belongs, by default None.

    Returns
    -------
    DeclarativeMeta
        The declarative class that corresponds to the specified table.

    Raises
    ------
    MissingPrimaryKey
        If the specified table does not have a primary key.

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> fa.features.get_class('xy', engine)
    sqlalchemy.ext.automap.xy
    """
    engine = get_engine(connection)
    metadata = get_metadata(engine, schema)
    metadata.reflect(engine, only=[table_name], schema=schema)
    base = _sa_automap.automap_base(metadata=metadata)
    base.prepare()
    if table_name not in base.classes:
        raise _ex.MissingPrimaryKeyError()
    return base.classes[table_name]  # type: ignore[no-any-return]


def get_session(
    engine: _sa_engine.Engine
) -> _sa_session.Session:
    """
    Creates and returns a new SQLAlchemy session object using the provided SQLAlchemy engine object.

    Parameters
    ----------
    engine : _sa_engine.Engine
        SQLAlchemy engine object to create a new session from.

    Returns
    -------
    _sa_session.Session
        New SQLAlchemy session object.

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> fa.features.get_session(engine)
    <sqlalchemy.orm.session.Session at 0x7f95999e1eb0>
    """
    return _sa_session.Session(engine, future=True)


def get_column(
    table: _sa.Table,
    column_name: str
) -> _sa.Column[_t.Any]:
    """
    Retrieve a SQLAlchemy column object from a SQLAlchemy table.

    Parameters
    ----------
    table : sqlalchemy.Table
        The SQLAlchemy table to retrieve the column from.
    column_name : str
        The name of the column to retrieve.

    Returns
    -------
    sqlalchemy.Column
        The SQLAlchemy column object corresponding to the given column name.

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.features.get_column(table, 'x')
    Column('x', INTEGER(), table=<xy>)
    """
    return table.c[column_name]


def get_table_constraints(
    table: _sa.Table
) -> _t.Set[_t.Any]:
    """
    Get a set of all constraints for a given SQLAlchemy Table object.

    Parameters
    ----------
    table : sqlalchemy.Table
        The Table object to get the constraints from.

    Returns
    -------
    set
        A set of all constraints for the given Table object.

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.features.get_table_constraints(table)
    {PrimaryKeyConstraint(Column('id', INTEGER(), table=<xy>, primary_key=True, nullable=False))}
    """
    return table.constraints


def get_primary_key_constraints(
    table: _sa.Table
) -> _t.Union[_t.Tuple[_t.Optional[str], _t.List[str]], _t.Tuple[()]]:
    """
    Get the primary key constraints of a SQLAlchemy table.

    Parameters
    ----------
    table : sqlalchemy.Table
        The SQLAlchemy table object to get the primary key constraints of.

    Returns
    -------
    Tuple[Optional[str], List[str]] | Tuple[()]
        A tuple with the primary key constraint name (if it exists) and a list of
        the column names that make up the primary key. Returns empty tuple if no
        primary key exists.

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.features.get_primary_key_constraints(table)
    (None, ['id'])
    """
    cons = get_table_constraints(table)
    for con in cons:
        if isinstance(con, _sa.PrimaryKeyConstraint):
            pk_name: _t.Optional[str] = con.name  # type: ignore[assignment]
            col_names: _t.List[str] = [col.name for col in con.columns]
            return (pk_name, col_names)
    return ()


def missing_primary_key(
    table: _sa.Table,
) -> bool:
    """
    Check if a sqlalchemy table has a primary key.

    Parameters
    ----------
    table : sqlalchemy.Table
        The table to check.

    Returns
    -------
    bool
        True if the table doesn't have a primary key, False otherwise.

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.features.missing_primary_key(table)
    False
    """
    pks = get_primary_key_constraints(table)
    return len(pks) == 0 or (len(pks) > 1 and pks[1] == [])


def get_column_types(
    table: _sa.Table
) -> _t.Dict[str, _t.Any]:
    """
    Get the types of columns in a SQLAlchemy table.

    Parameters
    ----------
    table : sqlalchemy.Table
        SQLAlchemy table to get column types from.

    Returns
    -------
    dict
        A dictionary with the names of columns as keys and the SQLAlchemy
        types of the columns as values.

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.features.get_column_types(table)
    {'id': INTEGER(), 'x': INTEGER(), 'y': INTEGER()}
    """
    return {c.name: c.type for c in table.c}


def get_column_names(
    table: _sa.Table
) ->  _t.List[str]:
    """
    Returns a list of the column names for the given SQLAlchemy table object.

    Parameters
    ----------
    table : sqlalchemy.Table
        The SQLAlchemy table object to get column names for.

    Returns
    -------
    List[str]
        A list of the column names for the given table.

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.features.get_column_names(table)
    ['id', 'x', 'y']
    """
    return [c.name for c in table.columns]


def get_table_names(
    engine: _sa_engine.Engine,
    schema: _t.Optional[str] = None
) ->  _t.List[str]:
    """
    Get a list of the names of tables in the database connected to the given engine.

    Parameters
    ----------
    engine : _sa_engine.Engine
        An SQLAlchemy engine instance connected to a database.
    schema : Optional[str], optional
        The name of the schema to filter by, by default None.

    Returns
    -------
    List[str]
        A list of table names.

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> fa.features.get_table_names(engine)
    ['xy']
    """
    return _sa.inspect(engine).get_table_names(schema)


def get_row_count(
    table: _sa.Table,
    session: _t.Optional[_types.SqlConnection] = None
) -> int:
    """
    Returns the number of rows in a given table.

    Parameters
    ----------
    table : sqlalchemy.Table
        The table to get the row count from.
    session : sqlalchemy.orm.Session, optional
        The session to use. If not provided, a new session is created.

    Returns
    -------
    int
        The number of rows in the table.

    Examples
    --------
    >>> import fullmetalalchemy as fa
    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.features.get_row_count(table)
    0
    """
    engine = _ex.check_for_engine(table, session)
    col_name = get_column_names(table)[0]
    col = get_column(table, col_name)
    with engine.connect() as conn:
        result = conn.execute(_sa.select(_sa.func.count(col))).scalar()
        return result if result is not None else 0


def get_schemas(
    engine: _sa_engine.Engine
) ->  _t.List[str]:
    """
    Get a list of all schemas in the database connected to the given engine.

    Parameters
    ----------
    engine : sqlalchemy.engine.Engine
        An instance of the SQLAlchemy engine connected to the database.

    Returns
    -------
    List[str]
        A list of all schemas in the connected database.

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> fa.features.get_schemas(engine)
    ['main']
    """
    insp = _sa.inspect(engine)
    return insp.get_schema_names()


def tables_metadata_equal(
    table1: _sa.Table,
    table2: _sa.Table
) -> bool:
    """
    Check if two SQL tables have the same metadata.

    Parameters
    ----------
    table1 : sqlalchemy.Table
        First SQL table to compare
    table2 : sqlalchemy.Table
        Second SQL table to compare

    Returns
    -------
    bool
        True if the two SQL tables have the same metadata, otherwise False.

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.features.tables_metadata_equal(table, table)
    True
    """
    if table1.name != table2.name:
        return False

    get_column_types(table1)
    get_column_types(table2)
    # if column_types1 != column_types2: return False

    table1_keys = primary_key_names(table1)
    table2_keys = primary_key_names(table2)
    if set(table1_keys) != set(table2_keys):
        return False

    return True


def str_to_table(
    table_name: _t.Union[str, _sa.Table],
    connection: _t.Optional[_types.SqlConnection]
) -> _sa.Table:
    """
    Convert a table name to a SQLAlchemy table object.

    Parameters
    ----------
    table_name : str or sqlalchemy.Table
        If a string is passed, it should be the name of the table to be fetched.
        If a `sqlalchemy.Table` object is passed, it is simply returned.

    connection : SQLAlchemy connection
        Connection to the database.

    Returns
    -------
    sqlalchemy.Table
        The corresponding table object.

    Raises
    ------
    ValueError
        If `table_name` is a string and `connection` is `None`.

    TypeError
        If `table_name` is neither a string nor a `sqlalchemy.Table`.

    Example
    -------
    >>> import fullmetalalchemy as fa
    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> table_name = 'xy'
    >>> table = fa.features.str_to_table(table_name, engine)
    >>> print(table.name)
    xy
    """
    if type(table_name) is str:
        if connection is None:
            raise ValueError('table_name cannot be str while connection is None')
        return get_table(table_name, connection)
    elif type(table_name) is _sa.Table:
        return table_name
    else:
        raise TypeError('table_name can only be str or sa.Table')


def _get_where_clause(
    sa_table: _sa.Table,
    record: _types.Record
) -> _t.List[_t.Any]:
    """
    Given a record, return a list of SQLAlchemy binary expressions
    representing the WHERE clause for a SQL query.

    Parameters
    ----------
    sa_table : sqlalchemy.Table
        The table object that the WHERE clause is for.
    record : Dict[str, Any]
        The record to match against.

    Returns
    -------
    List[sqlalchemy.sql.elements.BinaryExpression]
        A list of SQLAlchemy binary expressions representing the WHERE clause.

    Examples
    --------
    >>> from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
    >>> engine = create_engine('sqlite://')
    >>> metadata = MetaData()
    >>> test_table = Table(
    ...     'test', metadata,
    ...     Column('id', Integer, primary_key=True),
    ...     Column('name', String)
    ... )
    >>> metadata.create_all(engine)
    >>> record = {'id': 1, 'name': 'test_name'}
    >>> where_clause = _get_where_clause(test_table, record)
    >>> where_clause
    [test.id = :id_1, test.name = :name_1]

    """
    return [sa_table.c[key_name] == key_value for key_name, key_value in record.items()]
