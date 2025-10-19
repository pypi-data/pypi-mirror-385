"""
Functions for inserting records into SQL tables.
"""

import typing as _t

import sqlalchemy as _sa
import sqlalchemy.engine as _sa_engine

import fullmetalalchemy.exceptions as _ex
import fullmetalalchemy.features as _features
import fullmetalalchemy.session as _session
import fullmetalalchemy.types as _types

# Re-export session functions for backward compatibility
insert_from_table_session = _session.insert_from_table
insert_records_session = _session.insert_records
_insert_records_fast_session = _session._insert_records_fast
_insert_records_slow_session = _session._insert_records_slow


def insert_from_table(
    table1: _t.Union[_sa.Table, str],
    table2: _t.Union[_sa.Table, str],
    engine: _t.Optional[_sa_engine.Engine] = None,
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
            raise ValueError("Must provide engine when table1 is a string.")
        table1 = _features.get_table(table1, engine)
    engine = _ex.check_for_engine(table1, engine)
    session = _features.get_session(engine)
    try:
        _session.insert_from_table(table1, table2, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def insert_records(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[_types.Record],
    engine: _t.Optional[_sa_engine.Engine] = None,
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
        _session.insert_records(table, records, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def _insert_records_fast(
    table: _sa.Table,
    records: _t.Sequence[_types.Record],
    engine: _t.Optional[_sa_engine.Engine] = None,
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
        raise _ex.MissingPrimaryKeyError()
    engine = _ex.check_for_engine(table, engine)
    session = _features.get_session(engine)
    try:
        _session._insert_records_fast(table, records, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
