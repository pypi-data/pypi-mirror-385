"""
Functions for deleting records from SQL tables.
"""

import typing as _t

import sqlalchemy as _sa
import sqlalchemy.engine as _sa_engine

import fullmetalalchemy.exceptions as _ex
import fullmetalalchemy.features as _features
import fullmetalalchemy.session as _session

# Re-export session functions for backward compatibility
delete_records_session = _session.delete_records
delete_record_by_values_session = _session.delete_record_by_values
delete_records_by_values_session = _session.delete_records_by_values
delete_all_records_session = _session.delete_all_records
_build_delete_from_record = _session._build_delete_from_record


def delete_records(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    values: _t.Sequence[_t.Any],
    engine: _t.Optional[_sa_engine.Engine] = None,
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
    try:
        _session.delete_records(table, column_name, values, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def delete_records_by_values(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[_t.Dict[str, _t.Any]],
    engine: _t.Optional[_sa.engine.Engine] = None,
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
        _session.delete_records_by_values(table, records, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def delete_all_records(
    table: _t.Union[_sa.Table, str], engine: _t.Optional[_sa_engine.Engine] = None
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
        _session.delete_all_records(table, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
