"""
Functions for selecting records from SQL tables.
"""

import typing as _t

import sqlalchemy as _sa
import sqlalchemy.sql.elements as sa_elements

import fullmetalalchemy.exceptions as _ex
import fullmetalalchemy.exceptions as exceptions
import fullmetalalchemy.features as _features
import fullmetalalchemy.types as _types


def select_records_all(
    table: _t.Union[_sa.Table, str],
    connection: _t.Optional[_types.SqlConnection] = None,
    sorted: bool = False,
    include_columns: _t.Optional[_t.Sequence[str]] = None,
) -> _t.List[_types.Record]:
    """
    Select all records from the specified table.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The table to select records from.
    connection : Optional[fullmetalalchemy.types.SqlConnection]
        The database connection to use. If not provided, the default connection
        will be used.
    sorted : bool, optional
        If True, the records will be sorted by their primary key(s), by default False.
    include_columns : Optional[Sequence[str]], optional
        A sequence of column names to include in the query, by default None.

    Returns
    -------
    List[fullmetalalchemy.types.Record]
        A list of dictionaries representing the selected records.

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select_records_all(table, engine)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]
    """
    table, connection = _ex.convert_table_connection(table, connection)
    if include_columns is not None:
        columns = [_features.get_column(table, column_name) for column_name in include_columns]
        query = _sa.select(*columns)
    else:
        query = _sa.select(table)

    if sorted:
        query = query.order_by(*_features.primary_key_columns(table))
    engine = _features.get_engine(connection)
    with engine.connect() as con:
        results = con.execute(query)
        return [dict(r._mapping) for r in results]


def select_records_chunks(
    table: _t.Union[_sa.Table, str],
    connection: _t.Optional[_types.SqlConnection] = None,
    chunksize: int = 2,
    sorted: bool = False,
    include_columns: _t.Optional[_t.Sequence[str]] = None,
) -> _t.Generator[_t.List[_types.Record], None, None]:
    """
    Return a generator yielding a chunk of records at a time from the specified table.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The table to select records from. It can be either a string
        representing the name of the table or a SQLAlchemy table object.
    connection : Optional[SqlConnection], optional
        The database connection object, by default None.
    chunksize : int, optional
        The number of records to return per chunk, by default 2.
    sorted : bool, optional
        If True, the records are sorted by primary key, by default False.
    include_columns : Optional[Sequence[str]], optional
        A sequence of column names to include in the selection, by default None.

    Yields
    ------
    Generator[List[Record]]
        A generator that yields a chunk of records at a time from the specified table.
        Each chunk contains a list of dictionaries, where each dictionary represents a record.

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> records_chunks = fa.select.select_records_chunks(table, engine)
    >>> next(records_chunks)
    [{'id': 1, 'x': 1, 'y': 2},
     {'id': 2, 'x': 2, 'y': 4}]
    >>> next(records_chunks)
    [{'id': 3, 'x': 4, 'y': 8},
     {'id': 4, 'x': 8, 'y': 11}]
    """
    table, connection = _ex.convert_table_connection(table, connection)
    if include_columns is not None:
        columns = [_features.get_column(table, column_name) for column_name in include_columns]
        query = _sa.select(*columns)
    else:
        query = _sa.select(table)

    if sorted:
        query = query.order_by(*_features.primary_key_columns(table))
    engine = _features.get_engine(connection)
    with engine.connect() as con:
        stream = con.execute(query, execution_options={"stream_results": True})
        for results in stream.partitions(chunksize):
            yield [dict(r._mapping) for r in results]


def select_existing_values(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    values: _t.Sequence[_t.Any],
    connection: _t.Optional[_types.SqlConnection] = None,
) -> _t.List[_t.Any]:
    """
    Selects existing values from a specified column in a database table.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The table to select values from. Can be either a SQLAlchemy Table object or a string representing the table name.
    column_name : str
        The name of the column to select values from.
    values : Sequence
        A sequence of values to look for in the specified column.
    connection : Optional[fullmetalalchemy.types.SqlConnection]
        The database connection to use. If None, the default engine will be used.

    Returns
    -------
    list
        A list of existing values from the specified column that match the given sequence of values.

    Examples
    --------
    >>> import fullmetalalchemy as fa
    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> values = [1, 2, 3, 4, 5]
    >>> fa.select_existing_values(table, 'x', values, engine)
    [1, 2, 4]

    """
    table, connection = _ex.convert_table_connection(table, connection)
    column = _features.get_column(table, column_name)
    query = _sa.select(column).where(column.in_(values))
    connection = _ex.check_for_engine(table, connection)
    engine = _features.get_engine(connection)
    with engine.connect() as con:
        return list(con.execute(query).scalars().fetchall())


def select_column_values_all(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    connection: _t.Optional[_types.SqlConnection] = None,
) -> _t.List[_t.Any]:
    """
    Selects all values in a specified column in a database table.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The table to select values from. Can be either a SQLAlchemy Table object or a string representing the table name.
    column_name : str
        The name of the column to select values from.
    connection : Optional[fullmetalalchemy.types.SqlConnection]
        The database connection to use. If None, the default engine will be used.

    Returns
    -------
    list
        A list of all values in the specified column.

    Examples
    --------
    >>> import fullmetalalchemy as fa
    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select_column_values_all(table, 'x', engine)
    [1, 2, 4, 8]

    """
    table, connection = _ex.convert_table_connection(table, connection)
    query = _sa.select(_features.get_column(table, column_name))
    connection = _ex.check_for_engine(table, connection)
    engine = _features.get_engine(connection)
    with engine.connect() as con:
        return list(con.execute(query).scalars().all())


def select_column_values_chunks(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    chunksize: int,
    connection: _t.Optional[_types.SqlConnection] = None,
) -> _t.Generator[_t.Sequence[_t.Any], None, None]:
    """
    Select chunks of values in named column.

    Parameters
    ----------
    table : Union[Table, str]
        The table to select the values from, either as a string or as a Table object.
    column_name : str
        The name of the column from which to select the values.
    chunksize : int
        The size of the chunks in which to partition the results.
    connection : Optional[SqlConnection], default=None
        The database connection to use. If None, a new connection is created.

    Returns
    -------
    Generator[list, None, None]
        A generator of lists containing the selected values, partitioned into chunks of `chunksize`.

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> col_chunks = fa.select.select_column_values_chunks(table, engine, 'x', 2)
    >>> next(col_chunks)
    [1, 2]
    >>> next(col_chunks)
    [4, 8]
    """
    table, connection = _ex.convert_table_connection(table, connection)
    query = _sa.select(_features.get_column(table, column_name))
    engine = _features.get_engine(connection)
    with engine.connect() as conn:
        stream = conn.execute(query, execution_options={"stream_results": True})
        yield from stream.scalars().partitions(chunksize)


def select_records_slice(
    table: _t.Union[_sa.Table, str],
    start: _t.Optional[int] = None,
    stop: _t.Optional[int] = None,
    connection: _t.Optional[_types.SqlConnection] = None,
    sorted: bool = False,
    include_columns: _t.Optional[_t.Sequence[str]] = None,
) -> _t.List[_types.Record]:
    """
    Select a slice of records from the table.

    Parameters
    ----------
    table : Union[Table, str]
        The SQLAlchemy Table object or name of the table from which to select records.
    start : Optional[int], default None
        The starting index of the slice. If None, slice starts from the beginning.
    stop : Optional[int], default None
        The ending index of the slice. If None, slice goes until the end.
    connection : Optional[SqlConnection], default None
        The SQLAlchemy database connection to use for the query. If None, a new connection
        is created using the default settings.
    sorted : bool, default False
        Whether to sort the records by the primary key columns of the table.
    include_columns : Optional[Sequence[str]], default None
        The names of the columns to include in the records. If None, all columns are included.

    Returns
    -------
    List[Record]
        A list of records, where each record is a dictionary representing a row in the table.

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select.select_records_slice(table, engine, start=1, stop=3)
    [{'id': 2, 'x': 2, 'y': 4},
     {'id': 3, 'x': 4, 'y': 8}]
    """
    table, connection = _ex.convert_table_connection(table, connection)
    start, stop = _convert_slice_indexes(table, connection, start, stop)
    if stop < start:
        raise exceptions.SliceError("stop cannot be less than start.")
    if include_columns is not None:
        columns = [_features.get_column(table, column_name) for column_name in include_columns]
        query = _sa.select(*columns)
    else:
        query = _sa.select(table)
    if sorted:
        query = query.order_by(*_features.primary_key_columns(table))
    query = query.slice(start, stop)
    engine = _features.get_engine(connection)
    with engine.connect() as conn:
        results = conn.execute(query)
        return [dict(r._mapping) for r in results]


def select_column_values_by_slice(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    start: _t.Optional[int] = None,
    stop: _t.Optional[int] = None,
    connection: _t.Optional[_types.SqlConnection] = None,
) -> _t.List[_t.Any]:
    """
    Select a slice of column values from the given table.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The table object or name of the table from which to select values.
    column_name : str
        The name of the column from which to select values.
    start : Optional[int], default None
        The starting index of the slice of values to select. If not provided, the slice starts from the beginning.
    stop : Optional[int], default None
        The ending index of the slice of values to select. If not provided, the slice ends at the last row.
    connection : Optional[fullmetalalchemy.types.SqlConnection], default None
        The database connection to use. If not provided, a new connection is created.

    Returns
    -------
    list
        A list of values selected from the column.

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select.select_column_values_by_slice(table, 'y', start=1, stop=3)
    [4, 8]
    """
    table, connection = _ex.convert_table_connection(table, connection)
    start, stop = _convert_slice_indexes(table, connection, start, stop)
    if stop < start:
        raise exceptions.SliceError("stop cannot be less than start.")
    query = _sa.select(_features.get_column(table, column_name)).slice(start, stop)
    engine = _features.get_engine(connection)
    with engine.connect() as conn:
        return list(conn.execute(query).scalars().all())


def select_column_value_by_index(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    index: int,
    connection: _t.Optional[_types.SqlConnection] = None,
) -> _t.Any:
    """
    Selects the value in a column of a table at a given index.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The table to select the value from. Can be either the SQLAlchemy table object or the name of the table as a string.
    column_name : str
        The name of the column to select the value from.
    index : int
        The index of the row to select the value from. Can be negative to indicate an index from the end (e.g. -1 selects the last row).
    connection : Optional[fullmetalalchemy.types.SqlConnection], optional
        The database connection to use. If not provided, a new connection will be created and closed after use.

    Returns
    -------
    Any
        The value in the specified column and row of the table.

    Raises
    ------
    IndexError
        If the index is out of range (either too large or too negative).

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select_column_value_by_index(table, 'y', 2)
    8
    """
    table, connection = _ex.convert_table_connection(table, connection)
    if index < 0:
        row_count = _features.get_row_count(table, connection)
        if index < -row_count:
            raise IndexError("Index out of range.")
        index = _calc_positive_index(index, row_count)
    query = _sa.select(_features.get_column(table, column_name)).slice(index, index + 1)
    engine = _features.get_engine(connection)
    with engine.connect() as conn:
        return conn.execute(query).scalars().all()[0]


def select_record_by_index(
    table: _t.Union[_sa.Table, str],
    index: int,
    connection: _t.Optional[_types.SqlConnection] = None,
) -> _t.Dict[str, _t.Any]:
    """
    Select a record from table by its index.

    Parameters
    ----------
    table : Union[Table, str]
        The table or table name to select records from.
    index : int
        The index of the record to select. If a negative index is provided, it will count from the end of the table.
    connection : Optional[SqlConnection]
        The database connection to use for the operation. If not provided, a connection will be obtained from the
        default connection pool.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the record's values.

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select.select_record_by_index(table, 2, engine)
    {'id': 3, 'x': 4, 'y': 8}
    """
    table, connection = _ex.convert_table_connection(table, connection)
    if index < 0:
        row_count = _features.get_row_count(table, connection)
        if index < -row_count:
            raise IndexError("Index out of range.")
        index = _calc_positive_index(index, row_count)
    query = _sa.select(table).slice(index, index + 1)
    engine = _features.get_engine(connection)
    with engine.connect() as conn:
        results = conn.execute(query)
        return next(dict(r._mapping) for r in results)


def select_primary_key_records_by_slice(
    table: _t.Union[_sa.Table, str],
    _slice: slice,
    connection: _t.Optional[_types.SqlConnection] = None,
    sorted: bool = False,
) -> _t.List[_types.Record]:
    """
    Selects primary key records by slice from a table.

    Parameters
    ----------
    table : Union[Table, str]
        The table or table name to select the records from.
    _slice : slice
        The slice to select the records from.
    connection : Optional[SqlConnection], optional
        The database connection to use, by default None.
    sorted : bool, optional
        If set to True, the primary key records will be returned in ascending
        order, by default False.

    Returns
    -------
    List[Record]
        A list of primary key records.

    Example
    -------
    >>> import fullmetalalchemy as fa
    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select.select_primary_key_records_by_slice(table, slice(1, 3), engine)
    [{'id': 2}, {'id': 3}]
    """
    table, connection = _ex.convert_table_connection(table, connection)
    start = _slice.start
    stop = _slice.stop
    start, stop = _convert_slice_indexes(table, connection, start, stop)
    if stop < start:
        raise exceptions.SliceError("stop cannot be less than start.")
    primary_key_values = _features.primary_key_columns(table)
    if sorted:
        query = _sa.select(*primary_key_values).order_by(*primary_key_values).slice(start, stop)
    else:
        query = _sa.select(*primary_key_values).slice(start, stop)
    engine = _features.get_engine(connection)
    with engine.connect() as conn:
        results = conn.execute(query)
        return [dict(r._mapping) for r in results]


def select_record_by_primary_key(
    table: _t.Union[_sa.Table, str],
    primary_key_value: _types.Record,
    connection: _t.Optional[_types.SqlConnection] = None,
    include_columns: _t.Optional[_t.Sequence[str]] = None,
) -> _types.Record:
    """
    Retrieve a record from a database table using its primary key value.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The database table from which to retrieve the record. Can be either a `sqlalchemy.Table` object or a string with the name of the table.
    primary_key_value : Record
        A dictionary containing the primary key column names and their values for the record to retrieve.
    connection : Optional[SqlConnection]
        A connection to the database. If `None`, a new connection will be created.
    include_columns : Optional[Sequence[str]]
        A sequence of column names to include in the returned record. If `None`, all columns will be included.

    Returns
    -------
    Record
        A dictionary containing the values for the requested record.

    Raises
    ------
    MissingPrimaryKey
        If the primary key values are missing in the table or if no record matches the primary key value.

    Example
    -------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select.select_record_by_primary_key(table, {'id': 3}, engine)
    {'id': 3, 'x': 4, 'y': 8}
    """
    table, connection = _ex.convert_table_connection(table, connection)
    # TODO: check if primary key values exist
    where_clause = _features._get_where_clause(table, primary_key_value)
    if len(where_clause) == 0:
        raise exceptions.MissingPrimaryKey("Primary key values missing in table.")
    if include_columns is not None:
        columns = [_features.get_column(table, column_name) for column_name in include_columns]
        query = _sa.select(*columns).where(sa_elements.and_(*where_clause))
    else:
        query = _sa.select(table).where(sa_elements.and_(*where_clause))
    engine = _features.get_engine(connection)
    with engine.connect() as conn:
        result_rows = conn.execute(query)
        results = [dict(r._mapping) for r in result_rows]
        if len(results) == 0:
            raise exceptions.MissingPrimaryKeyError("Primary key values missing in table.")
        return results[0]


def select_records_by_primary_keys(
    table: _t.Union[_sa.Table, str],
    primary_keys_values: _t.Sequence[_types.Record],
    connection: _t.Optional[_types.SqlConnection] = None,
    schema: _t.Optional[str] = None,
    include_columns: _t.Optional[_t.Sequence[str]] = None,
) -> _t.List[_types.Record]:
    """
    Select records from a table using a sequence of primary key values.

    Parameters
    ----------
    table : Union[Table, str]
        The table to select records from. Either the table object or the name of the table.
    primary_keys_values : Sequence[Record]
        A sequence of primary key values to select records by.
    connection : Optional[SqlConnection], optional
        The connection to use for the query, by default None.
    schema : Optional[str], optional
        The schema of the table, by default None.
    include_columns : Optional[Sequence[str]], optional
        A sequence of column names to include in the selected records, by default None.

    Returns
    -------
    List[Record]
        A list of dictionaries representing the selected records.

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select.select_records_by_primary_keys(table, engine, [{'id': 3}, {'id': 1}])
    [{'id': 1, 'x': 1, 'y': 2}, {'id': 3, 'x': 4, 'y': 8}]
    """
    table, connection = _ex.convert_table_connection(table, connection)
    # TODO: check if primary key values exist
    where_clauses = []
    for record in primary_keys_values:
        where_clause = _features._get_where_clause(table, record)
        where_clauses.append(sa_elements.and_(*where_clause))
    if len(where_clauses) == 0:
        return []
    if include_columns is not None:
        columns = [_features.get_column(table, column_name) for column_name in include_columns]
        query = _sa.select(*columns).where(sa_elements.or_(*where_clauses))
    else:
        query = _sa.select(table).where(sa_elements.or_(*where_clauses))
    engine = _features.get_engine(connection)
    with engine.connect() as conn:
        results = conn.execute(query)
        return [dict(r._mapping) for r in results]


def select_column_values_by_primary_keys(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    primary_keys_values: _t.Sequence[_types.Record],
    connection: _t.Optional[_types.SqlConnection] = None,
) -> _t.List[_t.Any]:
    """
    Selects the values in a column of a table for rows with specified primary key values.

    Parameters
    ----------
    table : Union[sqlalchemy.Table, str]
        The table to select the values from. Can be either the SQLAlchemy table object or the name of the table as a string.
    column_name : str
        The name of the column to select the values from.
    primary_keys_values : Sequence[fullmetalalchemy.types.Record]
        A sequence of primary key values to filter the rows by. Each value is a dictionary mapping column names to values for the corresponding row.
    connection : Optional[fullmetalalchemy.types.SqlConnection], optional
        The database connection to use. If not provided, a new connection will be created and closed after use.

    Returns
    -------
    list
        A list of the values in the specified column for rows that match the primary key values.

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select_column_values_by_primary_keys(table, 'y', [{'id': 3}, {'id': 1}])
    [2, 8]
    """
    table, connection = _ex.convert_table_connection(table, connection)
    # TODO: check if primary key values exist
    where_clauses = []
    for record in primary_keys_values:
        where_clause = _features._get_where_clause(table, record)
        where_clauses.append(sa_elements.and_(*where_clause))

    if len(where_clauses) == 0:
        return []
    query = _sa.select(_features.get_column(table, column_name)).where(
        sa_elements.or_(*where_clauses)
    )
    engine = _features.get_engine(connection)
    with engine.connect() as conn:
        results = conn.execute(query)
        return list(results.scalars().fetchall())


def select_value_by_primary_keys(
    table: _t.Union[_sa.Table, str],
    column_name: str,
    primary_key_value: _types.Record,
    connection: _t.Optional[_types.SqlConnection] = None,
    schema: _t.Optional[str] = None,
) -> _t.Any:
    """
    Select a single value from a database table by primary key.

    Parameters
    ----------
    table : Union[Table, str]
        A SQLAlchemy table object or string that specifies the table name.
    column_name : str
        The name of the column containing the value to be selected.
    primary_key_value : Record
        A dictionary that maps the primary key column names to their corresponding values.
    connection : Optional[SqlConnection]
        A SQLAlchemy database connection object. If None, a connection will be
        created using the default connection settings.
    schema : Optional[str]
        The name of the schema containing the table. If None, the default schema
        for the database connection will be used.

    Returns
    -------
    Any
        The value of the specified column for the record with the given primary key.

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> fa.select.select_value_by_primary_keys(table, 'y', {'id': 3})
    8
    """
    table, connection = _ex.convert_table_connection(table, connection)
    # TODO: check if primary key values exist
    where_clause = _features._get_where_clause(table, primary_key_value)
    if len(where_clause) == 0:
        raise KeyError("No such primary key values exist in table.")
    query = _sa.select(_features.get_column(table, column_name)).where(
        sa_elements.and_(*where_clause)
    )
    engine = _features.get_engine(connection)
    with engine.connect() as conn:
        return conn.execute(query).scalars().all()[0]


def _convert_slice_indexes(
    table: _t.Union[_sa.Table, str],
    connection: _types.SqlConnection,
    start: _t.Optional[int] = None,
    stop: _t.Optional[int] = None,
) -> _t.Tuple[int, int]:
    """
    Convert slice indexes.

    Parameters
    ----------
    table : str or sqlalchemy.Table
        The name or object of the table.
    connection : sqlalchemy.engine.Connection
        The connection object.
    start : int, optional
        The starting index of the slice. Defaults to None.
    stop : int, optional
        The stopping index of the slice. Defaults to None.

    Returns
    -------
    tuple
        A tuple of two ints representing the converted start and stop indexes.

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> engine, table = fa.get_engine_table('sqlite:///data/test.db', 'xy')
    >>> start, stop = fa.select._convert_slice_indexes(table, engine, 2, 6)
    >>> start, stop
    (2, 6)
    """
    table, connection = _ex.convert_table_connection(table, connection)
    # start index is 0 if None
    start = 0 if start is None else start
    row_count = _features.get_row_count(table, connection)

    # stop index is row count if None
    stop = row_count if stop is None else stop
    # convert negative indexes
    start = _calc_positive_index(start, row_count)
    start = _stop_underflow_index(start, row_count)
    stop = _calc_positive_index(stop, row_count)
    stop = _stop_overflow_index(stop, row_count)

    if row_count == 0:
        return 0, 0

    return start, stop


def _calc_positive_index(index: int, row_count: int) -> int:
    """
    Takes an integer index and row count, and returns the corresponding
    positive index if the given index is negative.

    Parameters
    ----------
    index : int
        The index to be converted to a positive index.
        If the index is negative, it will be converted to a positive index.
    row_count : int
        The number of rows in the table.

    Returns
    -------
    int
        The positive index that corresponds to the given index.

    Examples
    --------
    >>> _calc_positive_index(-1, 10)
    9
    >>> _calc_positive_index(-10, 20)
    10
    >>> _calc_positive_index(5, 10)
    5
    """
    # convert negative index to real index
    if index < 0:
        index = row_count + index
    return index


def _stop_overflow_index(index: int, row_count: int) -> int:
    """
    Checks if the given index is greater than the row count of the table.
    If so, it returns the row count, otherwise it returns the given index.

    Parameters
    ----------
    index : int
        The index value to check
    row_count : int
        The number of rows in the table.

    Returns
    -------
    int
        The modified index value, which is either the given index value or
        the row count of the table.

    Examples
    --------
    >>> _stop_overflow_index(5, 10)
    5
    >>> _stop_overflow_index(15, 10)
    10
    """
    if index > row_count - 1:
        return row_count
    return index


def _stop_underflow_index(index: int, row_count: int) -> int:
    """
    Return the input index or 0 if it is less than 0 and less than -row_count.

    Parameters
    ----------
    index : int
        The index to check.
    row_count : int
        The number of rows in the table.

    Returns
    -------
    int
        The input index or 0 if it is less than 0 and less than -row_count.

    Examples
    --------
    >>> _stop_underflow_index(1, 10)
    1
    >>> _stop_underflow_index(-5, 10)
    0
    >>> _stop_underflow_index(-15, 10)
    0
    """
    if index < 0 and index < -row_count:
        return 0
    return index
