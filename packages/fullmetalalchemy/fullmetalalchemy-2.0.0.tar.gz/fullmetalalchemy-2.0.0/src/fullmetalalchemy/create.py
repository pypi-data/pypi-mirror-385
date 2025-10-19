"""
Functions for creating SQL tables.
"""

import datetime as _datetime
import decimal as _decimal
import typing as _t

import sqlalchemy as _sa
import sqlalchemy.engine as _sa_engine
import sqlalchemy.schema as _sa_schema
from sqlalchemy import create_engine as _create_engine
from tinytim.data import column_names as _column_names  # type: ignore[import-untyped]
from tinytim.rows import row_dicts_to_data as _row_dicts_to_data  # type: ignore[import-untyped]

import fullmetalalchemy.features as _features
import fullmetalalchemy.insert as _insert
import fullmetalalchemy.type_convert as _type_convert
from fullmetalalchemy.features import get_session

create_session = get_session

_Record = _t.Dict[str, _t.Any]


def create_engine(url: str, *args: _t.Any, **kwargs: _t.Any) -> _sa_engine.Engine:
    """
    Returns a SQLAlchemy engine object for a given connection.

    Parameters
    ----------
    connection : Session or Engine
        A SQLAlchemy Session or Engine object.

    Returns
    -------
    Engine
        A SQLAlchemy Engine object that can be used to communicate with a database.

    Raises
    ------
    TypeError
        If `connection` is not an instance of either Session or Engine.

    Examples
    --------
    To get a SQLAlchemy Engine object for a given connection:

    >>> from sqlalchemy import create_engine
    >>> from sqlalchemy.orm import sessionmaker
    >>> engine = create_engine('postgresql://user:password@localhost/mydatabase')
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> engine = get_engine(session)

    """
    return _create_engine(url, *args, future=True, **kwargs)


def create_table(
    table_name: str,
    column_names:  _t.Sequence[str],
    column_types:  _t.Sequence[type],
    primary_key: _t.Sequence[str],
    engine: _sa_engine.Engine,
    schema:  _t.Optional[str] = None,
    autoincrement:  _t.Optional[bool] = False,
    if_exists:  _t.Optional[str] = 'error'
) -> _sa.Table:
    """
    Create a sql table from specifications.

    Parameters
    ----------
    table_name : str
    column_names : Sequence[str]
    column_types : Sequence
    primary_key : Sequence[str]
    engine : SqlAlchemy Engine
    schema : Optional[str]
    autoincrement : Optional[bool] default, None
    if_exists : Optional[str] default, 'error

    Returns
    -------
    sqlalchemy.Table

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> fa.get_table_names(engine)
    []
    >>> fa.create.create_table(
    ...         table_name='xy',
    ...         column_names=['id', 'x', 'y'],
    ...         column_types=[int, int, int],
    ...         primary_key=['id'],
    ...         engine=engine)
    Table('xy', MetaData(bind=Engine(sqlite:///data/test.db)),
    ...         Column('id', INTEGER(), table=<xy>, primary_key=True, nullable=False),
    ...         Column('x', INTEGER(), table=<xy>),
    ...         Column('y', INTEGER(), table=<xy>), schema=None)
     >>> fa.get_table_names(engine)
     ['xy']

    See Also
    --------
    fullmetalalchemy.create.create_table_from_records
    """
    cols = []

    for name, python_type in zip(column_names, column_types):
        sa_type = _type_convert._type_convert[python_type]
        if type(primary_key) is str:
            primary_key = [primary_key]
        col: _sa.Column[_t.Any]
        if name in primary_key:
            # autoincrement accepts bool or Literal['auto', 'ignore_fk']
            auto_inc = bool(autoincrement) if autoincrement is not None else False
            col = _sa.Column(name, sa_type, primary_key=True, autoincrement=auto_inc)
        else:
            col = _sa.Column(name, sa_type)
        cols.append(col)

    metadata = _sa.MetaData(schema=schema)
    table = _sa.Table(table_name, metadata, *cols)
    if if_exists == 'replace':
        drop_table_sql = _sa_schema.DropTable(table, if_exists=True)
        with engine.begin() as connection:
            connection.execute(drop_table_sql)
    table_creation_sql = _sa_schema.CreateTable(table)
    with engine.begin() as connection:
        connection.execute(table_creation_sql)
    return _features.get_table(table_name, engine, schema=schema)


def create_table_from_records(
    table_name: str,
    records:  _t.Sequence[_Record],
    primary_key: _t.Sequence[str],
    engine: _sa_engine.Engine,
    column_types:  _t.Optional[_t.Sequence[type]] = None,
    schema:  _t.Optional[str] = None,
    autoincrement:  _t.Optional[bool] = False,
    if_exists:  _t.Optional[str] = 'error',
    columns:  _t.Optional[_t.Sequence[str]] = None,
    missing_value:  _t.Optional[_t.Any] = None
) -> _sa.Table:
    """
    Create a sql table from specs and insert records.

    Returns
    -------
    sqlalchemy.Table

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> fa.get_table_names(engine)
    []
    >>> records = [
    ...        {'id': 1, 'x': 1, 'y': 2},
    ...        {'id': 2, 'x': 2, 'y': 4},
    ...        {'id': 3, 'x': 4, 'y': 8},
    ...        {'id': 4, 'x': 8, 'y': 11}]
    >>> fa.create.create_table_from_records(
    ...         table_name='xy',
    ...         records=records,
    ...         primary_key=['id'],
    ...         engine=engine,
    ...         if_exists='replace')
    Table('xy', MetaData(bind=Engine(sqlite:///data/test.db)),
    ...         Column('id', INTEGER(), table=<xy>, primary_key=True, nullable=False),
    ...         Column('x', INTEGER(), table=<xy>),
    ...         Column('y', INTEGER(), table=<xy>), schema=None)
     >>> fa.get_table_names(engine)
     ['xy']

    See Also
    --------
    fullmetalalchemy.create.create_table_from_records
    """
    data = _row_dicts_to_data(records, columns, missing_value)
    if column_types is None:
        column_types = [_column_datatype(values) for values in data.values()]
    col_names = _column_names(data)
    table = create_table(
        table_name, col_names, column_types, primary_key,
        engine, schema, autoincrement, if_exists
    )
    _insert.insert_records(table, records, engine)
    return table


def _column_datatype(values: _t.Iterable[_t.Any]) -> type:
    dtypes: _t.List[_t.Union[type, _t.Tuple[type, ...]]] = [
        int, str, (int, float), _decimal.Decimal, _datetime.datetime,
        bytes, bool, _datetime.date, _datetime.time,
        _datetime.timedelta, list, dict
    ]
    for value in values:
        for dtype in list(dtypes):
            try:
                if not isinstance(value, dtype):
                    if dtype in dtypes:
                        dtypes.remove(dtype)
            except TypeError:
                # Handle unhashable types
                pass
    # Special case: if both int and (int, float) remain, prefer int
    # This handles all-integer values which match both int and (int, float)
    if len(dtypes) == 2 and int in dtypes and (int, float) in dtypes:
        return int
    # If only one dtype remains, use it
    if len(dtypes) == 1:
        dtype_item = dtypes[0]
        # Handle tuple (int, float) - means values are mixed int/float
        if dtype_item == (int, float):
            return float
        # Regular type
        if isinstance(dtype_item, type):
            return dtype_item
    # Multiple types or no types matched - fall back to str
    return str

def copy_table(
    new_name: str,
    table: _sa.Table,
    engine: _sa_engine.Engine,
    if_exists: str = 'replace'
) -> _sa.Table:
    """
    Create a copy of an existing table with a new name.

    Parameters
    ----------
    new_name : str
        The name of the new table to create.
    table : sqlalchemy.Table
        The table to copy.
    engine : sqlalchemy.engine.Engine
        The database engine to use for the operation.
    if_exists : {'fail', 'replace'}, optional
        What to do if the new table already exists. The default is 'replace'.

    Returns
    -------
    sqlalchemy.Table
        The newly created table.

    Examples
    --------
    >>> from sqlalchemy import create_engine
    >>> engine = create_engine('sqlite:///:memory:')
    >>> from sqlalchemy import Column, Integer, String, MetaData
    >>> metadata = MetaData()
    >>> test_table = Table(
    ...     'test', metadata,
    ...     Column('id', Integer, primary_key=True),
    ...     Column('name', String)
    ... )
    >>> test_table.create(engine)
    >>> copy_table('test_copy', test_table, engine)
    Table('test_copy', MetaData(bind=None), Column('id', Integer(), ...)

    """
    src_engine = engine
    schema = table.schema
    src_name = table.name
    dest_schema = schema
    dest_name = new_name

    # reflect existing columns, and create table object for oldTable
    src_metadata = _sa.MetaData(schema=schema)
    src_metadata.reflect(src_engine, only=[src_name])

    # get columns from existing table
    if schema:
        src_table = src_metadata.tables[_sa.schema._get_table_key(src_name, schema)]
    else:
        src_table = src_metadata.tables[src_name]

    # create engine and table object for newTable
    dest_metadata = _sa.MetaData(schema=dest_schema)
    dest_table = _sa.Table(dest_name, dest_metadata, schema=dest_schema)

    if if_exists == 'replace':
        drop_table_sql = _sa_schema.DropTable(dest_table, if_exists=True)
        with engine.begin() as con:
            con.execute(drop_table_sql)

    # copy schema and create newTable from oldTable
    for column in src_table.columns:
        dest_table.append_column(column.copy())

    with engine.begin() as con:
        dest_table.create(con)

    # insert records from oldTable
    _insert.insert_from_table(src_table, dest_table, engine)
    return dest_table
