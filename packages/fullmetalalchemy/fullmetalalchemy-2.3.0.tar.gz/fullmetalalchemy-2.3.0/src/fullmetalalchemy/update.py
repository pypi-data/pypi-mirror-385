"""
Functions for updating records in SQL tables.
"""

import typing as _t

import sqlalchemy as _sa
import sqlalchemy.engine as _sa_engine

import fullmetalalchemy.exceptions as _ex
import fullmetalalchemy.features as _features
import fullmetalalchemy.session as _session
import fullmetalalchemy.types as _types

# Re-export session functions for backward compatibility
update_matching_records_session = _session.update_matching_records
update_records_session = _session.update_records
_update_records_fast_session = _session._update_records_fast
set_column_values_session = _session.set_column_values
_make_update_statement = _session._make_update_statement
_make_update_statement_column_value = _session._make_update_statement_column_value


def update_matching_records(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[_types.Record],
    match_column_names: _t.Sequence[str],
    engine: _t.Optional[_sa_engine.Engine] = None,
) -> None:
    """
    Update records in the given table that match the specified columns in the given session.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The table to update. Can be a `Table` object or the name of the table as a string.
    records : Sequence[fullmetalalchemy.types.Record]
        The records to update in the table.
    match_column_names : Sequence[str]
        The names of the columns to match on when updating the records.
    session : sqlalchemy.orm.Session
        The session to use for the update.

    Returns
    -------
    None

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> table = fa.features.get_table('xy', engine)
    >>> updated_records = [{'id': 1, 'x': 11}, {'id': 4, 'y': 111}]
    >>> session = fa.features.get_session(engine)
    >>> fa.update.update_matching_records_session(table, updated_records, ['id'], session)
    >>> session.commit()
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 11, 'y': 2},
    ... {'id': 2, 'x': 2, 'y': 4},
    ... {'id': 3, 'x': 4, 'y': 8},
    ... {'id': 4, 'x': 8, 'y': 111}]
    """
    table, engine = _ex.convert_table_engine(table, engine)
    session = _features.get_session(engine)
    try:
        _session.update_matching_records(table, records, match_column_names, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def update_records(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[_types.Record],
    engine: _t.Optional[_sa_engine.Engine] = None,
    match_column_names: _t.Optional[_t.Sequence[str]] = None,
) -> None:
    """
    Update a sequence of records in a table.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The table to update the records in.
    records : Sequence[fullmetalalchemy.types.Record]
        The sequence of records to update in the table.
    engine : Optional[sqlalchemy.engine.Engine], optional
        The database engine to use, by default None.
    match_column_names : Optional[Sequence[str]], optional
        A sequence of column names to match records on. Required if the table
        has no primary key, by default None.

    Returns
    -------
    None

    Examples
    --------
    >>> import fullmetalalchemy as fa
    >>> import numpy as np

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> table = fa.features.get_table('xy', engine)
    >>> updated_records = [{'id': 1, 'x': 11}, {'id': 4, 'y': 111}]
    >>> fa.update.update_records(table, updated_records, engine)
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 11, 'y': 2},
    ... {'id': 2, 'x': 2, 'y': 4},
    ... {'id': 3, 'x': 4, 'y': 8},
    ... {'id': 4, 'x': 8, 'y': 111}]
    """
    table, engine = _ex.convert_table_engine(table, engine)
    session = _features.get_session(engine)
    try:
        _session.update_records(table, records, session, match_column_names)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def set_column_values(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    value: _t.Any,
    engine: _t.Optional[_sa_engine.Engine] = None,
) -> None:
    """
    Update the specified records in the given table.

    Parameters
    ----------
    table : sqlalchemy.Table or str
        The table to update.
    records : sequence of dict
        The records to update. Each record is a dictionary containing
        keys that correspond to column names in the table and values
        that correspond to the new values for those columns.
    engine : sqlalchemy.engine.Engine, optional
        The engine to use to connect to the database. If None, use the
        default engine.
    match_column_names : sequence of str, optional
        The names of columns to use to match records. If None, use the
        primary key columns.

    Returns
    -------
    None

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> table = fa.features.get_table('xy', engine)
    >>> updated_records = [{'id': 1, 'x': 11}, {'id': 4, 'y': 111}]
    >>> fa.update.update_records(table, updated_records, engine)
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 11, 'y': 2},
    ... {'id': 2, 'x': 2, 'y': 4},
    ... {'id': 3, 'x': 4, 'y': 8},
    ... {'id': 4, 'x': 8, 'y': 111}]
    """
    table, engine = _ex.convert_table_engine(table, engine)
    session = _features.get_session(engine)
    try:
        _session.set_column_values(table, column_name, value, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
