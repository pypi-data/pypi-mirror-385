"""
Functions for inserting records into SQL tables.
"""

import typing as _t

import sqlalchemy as _sa
import sqlalchemy.engine as _sa_engine
import sqlalchemy.orm.session as _sa_session

import fullmetalalchemy.exceptions as _ex
import fullmetalalchemy.features as _features
import fullmetalalchemy.types as _types


def insert_from_table_session(
    table1: _t.Union[_sa.Table, str],
    table2: _t.Union[_sa.Table, str],
    session: _sa_session.Session
) -> None:
    """
    Inserts all rows from table1 to table2 using the provided SQLAlchemy session.

    Parameters
    ----------
    table1 : Union[sqlalchemy.Table, str]
        The source table to copy from. If a string is passed, it is used as
        the table name to fetch from the database.
    table2 : Union[sqlalchemy.Table, str]
        The destination table to insert into. If a string is passed, it is used as
        the table name to fetch from the database.
    session : sqlalchemy.orm.session.Session
        The SQLAlchemy session to use for the database connection.

    Returns
    -------
    None

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> table1 = fa.features.get_table('xy', engine)
    >>> table2 = fa.features.get_table('xyz', engine)
    >>> fa.select.select_records_all(table2)
    []

    >>> session = fa.features.get_session(engine)
    >>> fa.insert.insert_from_table_session(table1, table2, session)
    >>> session.commit()
    >>> fa.select.select_records_all(table2)
    [{'id': 1, 'x': 1, 'y': 2, 'z': None},
     {'id': 2, 'x': 2, 'y': 4, 'z': None},
     {'id': 3, 'x': 4, 'y': 8, 'z': None},
     {'id': 4, 'x': 8, 'y': 11, 'z': None}]
    """
    table1 = _features.str_to_table(table1, session)
    table2 = _features.str_to_table(table2, session)
    session.execute(table2.insert().from_select(table1.columns.keys(), table1))


def insert_from_table(
    table1: _t.Union[_sa.Table, str],
    table2: _t.Union[_sa.Table, str],
    engine: _t.Optional[_sa_engine.Engine] = None
) -> None:
    """
    Insert rows from one table into another.

    Parameters
    ----------
    table1 : Union[sqlalchemy.Table, str]
        The source table. Can be a string representing the name of the table
        or the actual table object.
    table2 : Union[sqlalchemy.Table, str]
        The destination table. Can be a string representing the name of the table
        or the actual table object.
    engine : Optional[sqlalchemy.engine.Engine], optional
        The engine to be used to create a session, by default None. If None,
        the function will try to extract the engine from either table1 or table2.

    Returns
    -------
    None

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> table1 = fa.features.get_table('xy', engine)
    >>> table2 = fa.features.get_table('xyz', engine)
    >>> fa.select.select_records_all(table2)
    []

    >>> fa.insert.insert_from_table(table1, table2, engine)
    >>> fa.select.select_records_all(table2)
    [{'id': 1, 'x': 1, 'y': 2, 'z': None},
     {'id': 2, 'x': 2, 'y': 4, 'z': None},
     {'id': 3, 'x': 4, 'y': 8, 'z': None},
     {'id': 4, 'x': 8, 'y': 11, 'z': None}]
    """
    # Convert table1 to Table object if it's a string
    if isinstance(table1, str):
        if engine is None:
            raise ValueError('Must provide engine when table1 is a string.')
        table1 = _features.get_table(table1, engine)
    engine = _ex.check_for_engine(table1, engine)
    session = _features.get_session(engine)
    try:
        insert_from_table_session(table1, table2, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def insert_records_session(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[_types.Record],
    session: _sa_session.Session
) -> None:
    """
    Insert records into a given table using a provided session.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The table to insert records into. Can be a string name of the table or a SQLAlchemy
        Table object.
    records : Sequence[Dict[str, Any]]
        A sequence of dictionaries representing the records to insert into the table.
    session : sqlalchemy.orm.Session
        A SQLAlchemy session to use for the insertion.

    Returns
    -------
    None

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> table = fa.features.get_table('xy', engine)

    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    >>> new_records = [{'id': 5, 'x': 11, 'y': 5}, {'id': 6, 'x': 9, 'y': 9}]
    >>> session = fa.features.get_session(engine)
    >>> fa.insert.insert_records_session(table, new_records, session)
    >>> session.commit()
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11},
     {'id': 5, 'x': 11, 'y': 5},
     {'id': 6, 'x': 9, 'y': 9}]
    """
    table = _features.str_to_table(table, session)
    if _features.missing_primary_key(table):
        _insert_records_slow_session(table, records, session)
    else:
        _insert_records_fast_session(table, records, session)


def insert_records(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[_types.Record],
    engine: _t.Optional[_sa_engine.Engine] = None
) -> None:
    """
    Insert records into a table.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The table object or name of the table.
    records : Sequence[Record]
        A sequence of records to insert into the table.
    engine : Optional[sqlalchemy.engine.Engine], optional
        The database engine to use. If None, then the default engine will be used.

    Returns
    -------
    None

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> table = fa.features.get_table('xy', engine)

    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    >>> new_records = [{'id': 5, 'x': 11, 'y': 5}, {'id': 6, 'x': 9, 'y': 9}]
    >>> fa.insert.insert_records(table, new_records, engine)
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11},
     {'id': 5, 'x': 11, 'y': 5},
     {'id': 6, 'x': 9, 'y': 9}]
    """
    table, engine = _ex.convert_table_engine(table, engine)
    session = _features.get_session(engine)
    try:
        insert_records_session(table, records, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def _insert_records_fast(
    table: _sa.Table,
    records: _t.Sequence[_types.Record],
    engine: _t.Optional[_sa_engine.Engine] = None
) -> None:
    """
    Inserts records into a database table using a fast method that avoids
    checking for a missing primary key.

    Parameters
    ----------
    table : sqlalchemy.Table
        The table to insert records into.
    records : Sequence[Dict[str, Any]]
        A sequence of records to insert into the table. Each record is a dictionary
        where the keys correspond to the column names and the values correspond
        to the data to be inserted.
    engine : sqlalchemy.engine.Engine, optional
        An optional database engine to use for the insertion. If not provided,
        the engine associated with the table is used.

    Returns
    -------
    None

    Raises
    ------
    MissingPrimaryKey
        If the table does not have a primary key.

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> table = fa.features.get_table('xy', engine)

    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    >>> new_records = [{'id': 5, 'x': 11, 'y': 5}, {'id': 6, 'x': 9, 'y': 9}]
    >>> fa.insert._insert_records_fast(table, new_records, engine)
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11},
     {'id': 5, 'x': 11, 'y': 5},
     {'id': 6, 'x': 9, 'y': 9}]
    """
    if _features.missing_primary_key(table):
        raise _ex.MissingPrimaryKey()
    engine = _ex.check_for_engine(table, engine)
    session = _features.get_session(engine)
    try:
        _insert_records_fast_session(table, records, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def _insert_records_fast_session(
    table: _sa.Table,
    records: _t.Sequence[_types.Record],
    session: _sa_session.Session
) -> None:
    """
    Insert a sequence of new records into a SQLAlchemy Table using bulk insert.

    Parameters
    ----------
    table : sqlalchemy.Table
        The SQLAlchemy Table to insert the records into.
    records : Sequence[fullmetalalchemy.types.Record]
        The sequence of new records to insert into the table.
    session : sqlalchemy.orm.Session
        The SQLAlchemy Session to use for the transaction.

    Raises
    ------
    fullmetalalchemy.exceptions.MissingPrimaryKey
        If the table does not have a primary key.

    Returns
    -------
    None

    Examples
    --------
    >>> from fullmetalalchemy import insert, features, create_engine, select

    >>> engine = create_engine('sqlite:///data/test.db')
    >>> table = features.get_table('xy', engine)

    >>> select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    >>> new_records = [{'id': 5, 'x': 11, 'y': 5}, {'id': 6, 'x': 9, 'y': 9}]
    >>> session = features.get_session(engine)
    >>> insert._insert_records_fast_session(table, new_records, session)
    >>> session.commit()
    >>> select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11},
     {'id': 5, 'x': 11, 'y': 5},
     {'id': 6, 'x': 9, 'y': 9}]
    """
    if _features.missing_primary_key(table):
        raise _ex.MissingPrimaryKey()
    table_class = _features.get_class(table.name, session, schema=table.schema)
    mapper = _sa.inspect(table_class)
    session.bulk_insert_mappings(mapper, records)


def _insert_records_slow_session(
    table: _sa.Table,
    records: _t.Sequence[_types.Record],
    session: _sa_session.Session
) -> None:
    """
    Inserts records into the given table using the provided session and
    the slow method of SQLAlchemy.

    Parameters
    ----------
    table : sqlalchemy.Table
        The table into which the records are being inserted.
    records : Sequence[fullmetalalchemy.types.Record]
        The records to be inserted.
    session : sqlalchemy.orm.session.Session
        The session to use for the insertion.

    Returns
    -------
    None

    """
    session.execute(table.insert(), records)
