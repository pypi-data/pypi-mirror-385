"""
Functions for deleting records from SQL tables.
"""

import typing as _t

import sqlalchemy as _sa
import sqlalchemy.engine as _sa_engine
import sqlalchemy.orm.session as _sa_session

import fullmetalalchemy.exceptions as _ex
import fullmetalalchemy.features as _features
import fullmetalalchemy.types as _types


def delete_records_session(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    values: _t.Sequence[_t.Any],
    session: _sa_session.Session
) -> None:
    """
    Delete records from SQL table that match passed values in column.
    Adds deletes to passed session.

    Parameters
    ----------
    table : sa.Table | str
        SqlAlchemy Table or table name
    column_name : str
        SQL table column name to match values
    values : Sequence
        values to match in SQL table column
    session : SqlAlchemy Session
        SqlAlchemy connection session

    Returns
    -------
    None

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    >>> session = fa.features.get_session(engine)
    >>> fa.delete.delete_records_session(table, 'id', [1], session)
    >>> session.commit()
    >>> fa.select.select_records_all(table)
    [{'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    See Also
    --------
    fullmetalalchemy.delete.delete_records_by_values_session
    """
    table = _features.str_to_table(table, session)
    col = _features.get_column(table, column_name)
    delete_stmt = _sa.delete(table).where(col.in_(values))
    session.execute(delete_stmt)


def delete_records(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    values: _t.Sequence[_t.Any],
    engine: _t.Optional[_sa_engine.Engine] = None
) -> None:
    """
    Delete records from SQL table that match passed values in column.

    Parameters
    ----------
    table : sa.Table | str
        SqlAlchemy Table or name of SQL table
    column_name : str
        SQL table column name to match values
    values : Sequence
        values to match in SQL table column
    engine : SqlAlchemy Engine
        SqlAlchemy connection engine

    Returns
    -------
    None

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    >>> fa.delete.delete_records(table, 'id', [1])
    >>> fa.select.select_records_all(table)
    [{'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    See Also
    --------
    fullmetalalchemy.delete.delete_records_by_values
    """
    table, engine = _ex.convert_table_engine(table, engine)
    session = _features.get_session(engine)
    delete_records_session(table, column_name, values, session)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def delete_records_by_values(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[_t.Dict[str, _t.Any]],
    engine: _t.Optional[_sa.engine.Engine] = None
) -> None:
    """
    Deletes records from a SQL table that match the passed records.

    Parameters
    ----------
    table : sa.Table | str
        SqlAlchemy Table or table name
    records : Sequence[Dict]
        records to match in SQL table
    engine : Optional[sa.engine.Engine]
        SqlAlchemy connection engine. If not given, it will try to obtain one from the passed table.

    Returns
    -------
    None

    Example
    -------
    >>> import sqlalchemize as sz

    >>> engine, table = sz.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> sz.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    >>> sz.delete.delete_records_by_values(table, [{'id': 3}, {'x': 2}], engine)
    >>> sz.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 4, 'x': 8, 'y': 11}]
    """
    table, engine = _ex.convert_table_engine(table, engine)
    session = _features.get_session(engine)
    try:
        delete_records_by_values_session(table, records, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def delete_record_by_values_session(
    table: _t.Union[_sa.Table, str],
    record: _types.Record,
    session: _sa_session.Session
) -> None:
    """
    Deletes a single row from a table based on the values in the specified record.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The table to delete from. Can either be a `sqlalchemy.Table` object
        or a string containing the name of the table.
    record : fullmetalalchemy.types.Record
        A dictionary of column names and values representing the row to delete.
    session : sqlalchemy.orm.session.Session
        The session object to use for the database transaction.

    Returns
    -------
    None

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    >>> session = fa.features.get_session(engine)
    >>> fa.delete.delete_record_by_values_session(table, {'id': 1, 'x': 1, 'y': 2}, session)
    >>> session.commit()
    >>> fa.select.select_records_all(table)
    [{'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    """
    table = _features.str_to_table(table, session)
    delete = _build_delete_from_record(table, record)
    session.execute(delete)


def delete_records_by_values_session(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[_types.Record],
    session: _sa_session.Session
) -> None:
    """
    Delete records from the specified table that match the given records
    by values using the provided session.

    Parameters
    ----------
    table : Union[Table, str]
        The SQLAlchemy table object or name of the table to delete records from.
    records : Sequence[Record]
        A sequence of records to delete from the table. Each record is a dictionary
        with keys as column names and values as the value to match.
    session : Session
        The SQLAlchemy session to use for the database operation.

    Returns
    -------
    None

    Example
    -------
    >>> import sqlalchemize as sz

    >>> engine, table = sz.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    >>> session = sz.features.get_session(engine)
    >>> sz.delete.delete_records_by_values_session(table, [{'id': 3}, {'x': 2}], session)
    >>> session.commit()
    >>> sz.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 4, 'x': 8, 'y': 11}]
    """
    table = _features.str_to_table(table, session)
    for record in records:
        delete_record_by_values_session(table, record, session)


def _build_delete_from_record(
    table: _sa.Table,
    record: _types.Record
) -> _sa.sql.Delete:
    """
    Builds a SQL DELETE statement for deleting a record from a table based on a
    dictionary of key-value pairs.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The table object or name to delete from.
    record : Dict[str, Any]
        A dictionary of key-value pairs representing the record to delete.

    Returns
    -------
    sqlalchemy.sql.expression.Delete
        A SQL DELETE statement for deleting a record from the table based on the given record.

    Example
    -------
    >>> from sqlalchemy import Table, Column, Integer, MetaData

    >>> metadata = MetaData()
    >>> table = Table('mytable', metadata,
    ...               Column('id', Integer, primary_key=True),
    ...               Column('name', String))
    >>> record = {'id': 1, 'name': 'test'}
    >>> delete_statement = _build_delete_from_record(table, record)
    >>> print(delete_statement)
    DELETE FROM mytable WHERE mytable.id = :id_1 AND mytable.name = :name_1
    """
    d = _sa.delete(table)
    for column, value in record.items():
        d = d.where(table.c[column]==value)
    return d


def delete_all_records_session(
    table: _t.Union[_sa.Table, str],
    session: _sa_session.Session
) -> None:
    """
    Delete all records from the specified table.

    Parameters
    ----------
    table : Union[Table, str]
        The table to delete records from. It can be either a sqlalchemy
        Table object or a table name.
    session : Session
        The session to use to execute the query.

    Returns
    -------
    None

    Examples
    --------
    >>> import sqlalchemize as sz

    >>> engine, table = sz.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> sz.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2}, {'id': 2, 'x': 2, 'y': 4}]

    >>> session = sz.features.get_session(engine)
    >>> sz.delete.delete_all_records_session(table, session)
    >>> session.commit()
    >>> sz.select.select_records_all(table)
    []
    """
    table = _features.str_to_table(table, session)
    query = _sa.delete(table)
    session.execute(query)


def delete_all_records(
    table: _t.Union[_sa.Table, str],
    engine: _t.Optional[_sa_engine.Engine] = None
) -> None:
    """
    Delete all records from a table.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The table to delete records from.
    engine : Optional[sqlalchemy.engine.Engine]
        The engine to use. If `None`, use default engine.

    Returns
    -------
    None

    Raises
    ------
    fullmetalalchemy.exceptions.InvalidInputType
        If `table` parameter is not a valid SQLAlchemy Table object or a string.
    Exception
        If any other error occurs.

    Example
    -------
    >>> import sqlalchemize as sz

    >>> engine, table = sz.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> sz.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2}, {'id': 2, 'x': 2, 'y': 4}]

    >>> sz.delete.delete_all_records(table)
    >>> sz.select.select_records_all(table)
    []
    """
    table, engine = _ex.convert_table_engine(table, engine)
    session = _features.get_session(engine)
    try:
        delete_all_records_session(table, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
