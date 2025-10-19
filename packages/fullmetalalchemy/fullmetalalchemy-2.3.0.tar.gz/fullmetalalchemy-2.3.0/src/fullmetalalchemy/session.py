"""
Session-based operations for FullmetalAlchemy.

This module contains all session-based CRUD operations that do not auto-commit,
allowing for fine-grained transaction control. Users can:
- Create a session manually
- Perform multiple operations
- Commit or rollback when ready

Examples
--------
>>> import fullmetalalchemy as fa
>>>
>>> engine = fa.create_engine('sqlite:///data.db')
>>> session = fa.features.get_session(engine)
>>> table = fa.get_table('users', engine)
>>>
>>> # Perform multiple operations
>>> fa.session.insert_records_session(table, records1, session)
>>> fa.session.update_records_session(table, records2, session)
>>> fa.session.delete_records_session(table, 'id', [1, 2], session)
>>>
>>> # Commit all changes
>>> session.commit()
"""

import typing as _t

import sqlalchemy as _sa
import sqlalchemy.orm.session as _sa_session

import fullmetalalchemy.exceptions as _ex
import fullmetalalchemy.features as _features
import fullmetalalchemy.records as _records
import fullmetalalchemy.types as _types

# ================== INSERT OPERATIONS ==================


def insert_from_table(
    table1: _t.Union[_sa.Table, str], table2: _t.Union[_sa.Table, str], session: _sa_session.Session
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
    >>> fa.session.insert_from_table_session(table1, table2, session)
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


def insert_records(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[_types.Record],
    session: _sa_session.Session,
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
    >>> fa.session.insert_records_session(table, new_records, session)
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
        _insert_records_slow(table, records, session)
    else:
        _insert_records_fast(table, records, session)


def _insert_records_fast(
    table: _sa.Table, records: _t.Sequence[_types.Record], session: _sa_session.Session
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
    fullmetalalchemy.exceptions.MissingPrimaryKeyError
        If the table does not have a primary key.

    Returns
    -------
    None

    Examples
    --------
    >>> from fullmetalalchemy import session, features, create_engine, select

    >>> engine = create_engine('sqlite:///data/test.db')
    >>> table = features.get_table('xy', engine)

    >>> select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    >>> new_records = [{'id': 5, 'x': 11, 'y': 5}, {'id': 6, 'x': 9, 'y': 9}]
    >>> sess = features.get_session(engine)
    >>> session._insert_records_fast_session(table, new_records, sess)
    >>> sess.commit()
    >>> select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11},
     {'id': 5, 'x': 11, 'y': 5},
     {'id': 6, 'x': 9, 'y': 9}]
    """
    if _features.missing_primary_key(table):
        raise _ex.MissingPrimaryKeyError()
    table_class = _features.get_class(table.name, session, schema=table.schema)
    mapper = _sa.inspect(table_class)
    session.bulk_insert_mappings(mapper, records)


def _insert_records_slow(
    table: _sa.Table, records: _t.Sequence[_types.Record], session: _sa_session.Session
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


# ================== DELETE OPERATIONS ==================


def delete_records(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    values: _t.Sequence[_t.Any],
    session: _sa_session.Session,
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
    >>> fa.session.delete_records_session(table, 'id', [1], session)
    >>> session.commit()
    >>> fa.select.select_records_all(table)
    [{'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    See Also
    --------
    fullmetalalchemy.session.delete_records_by_values
    """
    table = _features.str_to_table(table, session)
    col = _features.get_column(table, column_name)
    delete_stmt = _sa.delete(table).where(col.in_(values))
    session.execute(delete_stmt)


def delete_record_by_values(
    table: _t.Union[_sa.Table, str], record: _types.Record, session: _sa_session.Session
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
    >>> fa.session.delete_record_by_values_session(table, {'id': 1, 'x': 1, 'y': 2}, session)
    >>> session.commit()
    >>> fa.select.select_records_all(table)
    [{'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    """
    table = _features.str_to_table(table, session)
    delete = _build_delete_from_record(table, record)
    session.execute(delete)


def delete_records_by_values(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[_types.Record],
    session: _sa_session.Session,
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
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]

    >>> session = fa.features.get_session(engine)
    >>> fa.session.delete_records_by_values_session(table, [{'id': 3}, {'x': 2}], session)
    >>> session.commit()
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 4, 'x': 8, 'y': 11}]
    """
    table = _features.str_to_table(table, session)
    for record in records:
        delete_record_by_values(table, record, session)


def delete_all_records(table: _t.Union[_sa.Table, str], session: _sa_session.Session) -> None:
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
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2}, {'id': 2, 'x': 2, 'y': 4}]

    >>> session = fa.features.get_session(engine)
    >>> fa.session.delete_all_records_session(table, session)
    >>> session.commit()
    >>> fa.select.select_records_all(table)
    []
    """
    table = _features.str_to_table(table, session)
    query = _sa.delete(table)
    session.execute(query)


def _build_delete_from_record(table: _sa.Table, record: _types.Record) -> _t.Any:
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
        d = d.where(table.c[column] == value)
    return d


# ================== UPDATE OPERATIONS ==================


def update_matching_records(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[_types.Record],
    match_column_names: _t.Sequence[str],
    session: _sa_session.Session,
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
    >>> fa.session.update_matching_records_session(table, updated_records, ['id'], session)
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


def update_records(
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
    >>> fa.session.update_records_session(table, updated_records, session)
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
            raise ValueError("Must provide match_column_names if table has no primary key.")
        update_matching_records(table, records, match_column_names, session)
    else:
        _update_records_fast(table, records, session)


def _update_records_fast(
    table: _t.Union[_sa.Table, str],
    records: _t.Sequence[_types.Record],
    session: _sa_session.Session,
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
    >>> fa.session._update_records_fast_session(table, updated_records, session)
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


def set_column_values(
    table: _t.Union[_sa.Table, str], column_name: str, value: _t.Any, session: _sa_session.Session
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
    >>> session = fa.features.get_session(engine)
    >>> fa.session.set_column_values_session(table, 'z', 0, session)
    >>> session.commit()
    >>> fa.select.select_records_all(table)
    [{'id': 1, 'x': 1, 'y': 2, 'z': 0},
     {'id': 2, 'x': 2, 'y': 4, 'z': 0},
     {'id': 3, 'x': 4, 'y': 8, 'z': 0},
     {'id': 4, 'x': 8, 'y': 11, 'z': 0}]
    """
    table = _features.str_to_table(table, session)
    update_statement = _make_update_statement_column_value(table, column_name, value)
    session.execute(update_statement)


def _make_update_statement(
    table: _sa.Table, record_values: _t.Dict[str, _t.Any], new_values: _t.Dict[str, _t.Any]
) -> _t.Any:
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
        update_statement = update_statement.where(table.c[col] == val)
    return update_statement.values(**new_values)


def _make_update_statement_column_value(
    table: _sa.Table, column_name: str, value: _t.Any
) -> _t.Any:
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
