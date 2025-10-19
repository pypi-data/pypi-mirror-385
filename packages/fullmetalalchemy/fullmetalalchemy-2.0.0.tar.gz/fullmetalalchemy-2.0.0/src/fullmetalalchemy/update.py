"""
Functions for updating records in SQL tables.
"""

import typing as _t

import sqlalchemy as _sa
import sqlalchemy.engine as _sa_engine
import sqlalchemy.orm.session as _sa_session

import fullmetalalchemy.exceptions as _ex
import fullmetalalchemy.features as _features
import fullmetalalchemy.records as _records
import fullmetalalchemy.types as _types


def update_matching_records_session(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[_types.Record],
    match_column_names: _t.Sequence[str],
    session: _sa_session.Session
) -> None:
    """
    Update records in the database table that match the specified column names and values
    with the new record values.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The table to update. Either a SQLAlchemy Table object or a string with the name
        of the table.
    records : Sequence[fullmetalalchemy.types.Record]
        A sequence of dictionaries with the updated values for each record.
    match_column_names : Sequence[str]
        A sequence of column names used to match records in the database table.
    session : sqlalchemy.orm.session.Session
        A SQLAlchemy session object to use for the update operation.

    Returns
    -------
    None
        This function does not return anything. The records are updated in the database.

    Examples
    --------
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
    table = _features.str_to_table(table, session)
    match_values = [_records.filter_record(record, match_column_names) for record in records]
    for values, record in zip(match_values, records):
        stmt = _make_update_statement(table, values, record)
        session.execute(stmt)


def update_matching_records(
    table:_t.Union[_sa.Table, str],
    records: _t.Sequence[_types.Record],
    match_column_names: _t.Sequence[str],
    engine: _t.Optional[_sa_engine.Engine] = None
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
        update_matching_records_session(table, records, match_column_names, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def update_records_session(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[_types.Record],
    session: _sa_session.Session,
    match_column_names: _t.Optional[_t.Sequence[str]] = None,
) -> None:
    """
    Update the specified records in the given SQLAlchemy session.

    Parameters
    ----------
    table : Union[Table, str]
        The table to update records in. Either an SQLAlchemy Table object
        or a string name of the table.
    records : Sequence[Record]
        The updated records to insert. Each record must have a primary key value.
    session : sqlalchemy.orm.session.Session
        The SQLAlchemy session to use to perform the updates.
    match_column_names : Optional[Sequence[str]], optional
        A list of column names to match on when updating. If the table has
        a primary key, this can be left as None. Otherwise, it is required to
        specify the columns to match on, by default None.

    Returns
    -------
    None

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> table = fa.features.get_table('xy', engine)
    >>> updated_records = [{'id': 1, 'x': 11}, {'id': 4, 'y': 111}]
    >>> session = fa.features.get_session(engine)
    >>> fa.update.update_records_session(table, updated_records, session)
    >>> session.commit()
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 11, 'y': 2},
    ... {'id': 2, 'x': 2, 'y': 4},
    ... {'id': 3, 'x': 4, 'y': 8},
    ... {'id': 4, 'x': 8, 'y': 111}]
    """
    table = _features.str_to_table(table, session)
    if _features.missing_primary_key(table):
        if match_column_names is None:
            raise ValueError('Must provide match_column_names if table has no primary key.')
        update_matching_records_session(table, records, match_column_names, session)
    else:
        _update_records_fast_session(table, records, session)


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
        update_records_session(table, records, session, match_column_names)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def _update_records_fast_session(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[_types.Record],
    session: _sa_session.Session
) -> None:
    """
    Update records in a database table using the SQLAlchemy ORM's bulk_update_mappings function.

    Parameters
    ----------
    table : Union[Table, str]
        The SQLAlchemy Table object or name of the table to update.
    records : Sequence[Record]
        A sequence of dictionaries representing the records to be updated in the table.
    session : Session
        The SQLAlchemy Session object to use for the database transaction.

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
    >>> fa.update._update_records_fast_session(table, updated_records, session)
    >>> session.commit()
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 11, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 111}]
    """
    table = _features.str_to_table(table, session)
    table_name = table.name
    table_class = _features.get_class(table_name, session, schema=table.schema)
    mapper = _sa.inspect(table_class)
    session.bulk_update_mappings(mapper, records)


def _make_update_statement(
    table: _sa.Table,
    record_values: _t.Dict[str, _t.Any],
    new_values: _t.Dict[str, _t.Any]
) -> _sa.sql.expression.Update:
    """
    Constructs a SQLAlchemy update statement based on the given table and
    record values.

    Parameters
    ----------
    table : sqlalchemy.Table
        The table to update.
    record_values : dict
        A dictionary representing the primary key of the record to update.
    new_values : dict
        A dictionary representing the updated values for the record.

    Returns
    -------
    sqlalchemy.sql.expression.Update
        The constructed SQLAlchemy update statement.

    Example
    -------
    >>> import sqlalchemy as sa

    >>> engine = sa.create_engine('sqlite:///example.db')
    >>> metadata = sa.MetaData()
    >>> table = sa.Table('my_table', metadata,
    ...     sa.Column('id', sa.Integer, primary_key=True),
    ...     sa.Column('name', sa.String),
    ...     sa.Column('age', sa.Integer)
    ... )
    >>> record_values = {'id': 1}
    >>> new_values = {'name': 'John', 'age': 30}
    >>> update_stmt = _make_update_statement(table, record_values, new_values)
    """
    update_statement = _sa.update(table)
    for col, val in record_values.items():
        update_statement = update_statement.where(table.c[col]==val)
    return update_statement.values(**new_values)


def _make_update_statement_column_value(
    table: _sa.Table,
    column_name: str,
    value: _t.Any
) -> _sa.sql.expression.Update:
    """
    Create an update statement to set a column's value.

    Parameters
    ----------
    table : sqlalchemy.Table
        The table to update.
    column_name : str
        The name of the column to update.
    value : Any
        The new value to set for the column.

    Returns
    -------
    sqlalchemy.sql.expression.Update
        The update statement.

    Examples
    --------
    >>> import sqlalchemy as sa

    >>> table = sa.Table('my_table', sa.MetaData(), sa.Column('x', sa.Integer))
    >>> column_name = 'x'
    >>> value = 42
    >>> statement = _make_update_statement_column_value(table, column_name, value)
    >>> print(str(statement))
    UPDATE my_table SET x=:x_1
    """
    new_value = {column_name: value}
    return _sa.update(table).values(**new_value)


def set_column_values_session(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    value: _t.Any,
    session: _sa_session.Session
) -> None:
    """
    Update the values of a column for all rows in the table using the given session.

    Parameters
    ----------
    table : sqlalchemy.Table or str
        The table or table name to update.
    column_name : str
        The name of the column to update.
    value : Any
        The new value to set for the column.
    session : sqlalchemy.orm.Session
        The SQLAlchemy session to use for the update.

    Returns
    -------
    None

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine = fa.create_engine('sqlite:///data/test.db')
    >>> table = fa.features.get_table('xy', engine)
    >>> new_value = 1
    >>> session = fa.features.get_session(engine)
    >>> fa.update.set_column_values_session(table, 'x', new_value, session)
    >>> session.commit()
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 1, 'y': 4},
     {'id': 3, 'x': 1, 'y': 8},
     {'id': 4, 'x': 1, 'y': 11}]
    """
    table = _features.str_to_table(table, session)
    stmt = _make_update_statement_column_value(table, column_name, value)
    session.execute(stmt)


def set_column_values(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    value: _t.Any,
    engine: _t.Optional[_sa_engine.Engine] = None
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
        set_column_values_session(table, column_name, value, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
