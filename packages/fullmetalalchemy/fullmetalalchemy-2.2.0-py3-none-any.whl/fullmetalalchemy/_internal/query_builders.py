"""Shared query building logic for sync and async implementations.

This module contains pure query construction functions that don't perform I/O.
These functions can be safely reused by both sync and async execution paths.
"""

import typing as _t

import sqlalchemy as _sa
import sqlalchemy.sql.elements as sa_elements

from fullmetalalchemy._internal import helpers


def build_select_all_query(
    table: _sa.Table, sorted: bool = False, include_columns: _t.Optional[_t.Sequence[str]] = None
) -> _sa.Select[_t.Any]:
    """Build SELECT query for all records.

    Parameters
    ----------
    table : sqlalchemy.Table
        Table to select from.
    sorted : bool
        If True, order by primary key columns.
    include_columns : Optional[Sequence[str]]
        If provided, select only these columns.

    Returns
    -------
    Select
        SQLAlchemy select query object.
    """
    if include_columns is not None:
        columns = [helpers.get_column(table, col) for col in include_columns]
        query = _sa.select(*columns)
    else:
        query = _sa.select(table)

    if sorted:
        query = query.order_by(*helpers.primary_key_columns(table))

    return query


def build_select_slice_query(
    table: _sa.Table,
    start: int,
    stop: int,
    sorted: bool = False,
    include_columns: _t.Optional[_t.Sequence[str]] = None,
) -> _sa.Select[_t.Any]:
    """Build SELECT query for record slice.

    Parameters
    ----------
    table : sqlalchemy.Table
        Table to select from.
    start : int
        Start index.
    stop : int
        Stop index.
    sorted : bool
        If True, order by primary key columns.
    include_columns : Optional[Sequence[str]]
        If provided, select only these columns.

    Returns
    -------
    Select
        SQLAlchemy select query with slice.
    """
    if include_columns is not None:
        columns = [helpers.get_column(table, col) for col in include_columns]
        query = _sa.select(*columns)
    else:
        query = _sa.select(table)

    if sorted:
        query = query.order_by(*helpers.primary_key_columns(table))

    return query.slice(start, stop)


def build_select_column_query(table: _sa.Table, column_name: str) -> _sa.Select[_t.Any]:
    """Build SELECT query for single column.

    Parameters
    ----------
    table : sqlalchemy.Table
        Table to select from.
    column_name : str
        Column name to select.

    Returns
    -------
    Select
        SQLAlchemy select query.
    """
    column = helpers.get_column(table, column_name)
    return _sa.select(column)


def build_select_by_primary_key_query(
    table: _sa.Table,
    primary_key_value: _t.Dict[str, _t.Any],
    include_columns: _t.Optional[_t.Sequence[str]] = None,
) -> _sa.Select[_t.Any]:
    """Build SELECT query filtering by primary key.

    Parameters
    ----------
    table : sqlalchemy.Table
        Table to select from.
    primary_key_value : Dict[str, Any]
        Dictionary mapping PK column names to values.
    include_columns : Optional[Sequence[str]]
        If provided, select only these columns.

    Returns
    -------
    Select
        SQLAlchemy select query with WHERE clause.
    """
    where_clause = build_where_clause_from_dict(table, primary_key_value)

    if include_columns is not None:
        columns = [helpers.get_column(table, col) for col in include_columns]
        query = _sa.select(*columns)
    else:
        query = _sa.select(table)

    return query.where(sa_elements.and_(*where_clause))


def build_where_clause_from_dict(
    table: _sa.Table, filter_dict: _t.Dict[str, _t.Any]
) -> _t.List[_sa.ColumnElement[bool]]:
    """Build WHERE clause from dictionary of column:value pairs.

    Parameters
    ----------
    table : sqlalchemy.Table
        Table to build WHERE clause for.
    filter_dict : Dict[str, Any]
        Dictionary mapping column names to values.

    Returns
    -------
    List[ColumnElement]
        List of WHERE clause conditions.
    """
    where_clause = []
    for col_name, value in filter_dict.items():
        column = helpers.get_column(table, col_name)
        where_clause.append(column == value)
    return where_clause


def build_insert_stmt(table: _sa.Table, records: _t.Sequence[_t.Dict[str, _t.Any]]) -> _sa.Insert:
    """Build INSERT statement.

    Parameters
    ----------
    table : sqlalchemy.Table
        Table to insert into.
    records : Sequence[Dict[str, Any]]
        Records to insert.

    Returns
    -------
    Insert
        SQLAlchemy insert statement.
    """
    return table.insert().values(list(records))


def build_update_stmt_bulk(
    table: _sa.Table,
    records: _t.Sequence[_t.Dict[str, _t.Any]],
    match_column_names: _t.Sequence[str],
) -> _t.List[_sa.Update]:
    """Build UPDATE statements for bulk update by matching columns.

    Parameters
    ----------
    table : sqlalchemy.Table
        Table to update.
    records : Sequence[Dict[str, Any]]
        Records with updated values.
    match_column_names : Sequence[str]
        Column names to match records on.

    Returns
    -------
    List[Update]
        List of UPDATE statements.
    """
    stmts = []
    for record in records:
        where_conditions = []
        update_values = {}

        for key, value in record.items():
            if key in match_column_names:
                where_conditions.append(helpers.get_column(table, key) == value)
            else:
                update_values[key] = value

        if where_conditions and update_values:
            stmt = (
                _sa.update(table).where(sa_elements.and_(*where_conditions)).values(update_values)
            )
            stmts.append(stmt)

    return stmts


def build_delete_stmt(
    table: _sa.Table, column_name: str, values: _t.Sequence[_t.Any]
) -> _sa.Delete:
    """Build DELETE statement.

    Parameters
    ----------
    table : sqlalchemy.Table
        Table to delete from.
    column_name : str
        Column name to filter on.
    values : Sequence[Any]
        Values to match for deletion.

    Returns
    -------
    Delete
        SQLAlchemy delete statement.
    """
    column = helpers.get_column(table, column_name)
    return _sa.delete(table).where(column.in_(values))


def build_delete_stmt_from_records(
    table: _sa.Table, records: _t.Sequence[_t.Dict[str, _t.Any]]
) -> _t.List[_sa.Delete]:
    """Build DELETE statements from records.

    Parameters
    ----------
    table : sqlalchemy.Table
        Table to delete from.
    records : Sequence[Dict[str, Any]]
        Records defining deletion criteria.

    Returns
    -------
    List[Delete]
        List of DELETE statements.
    """
    stmts = []
    for record in records:
        where_clause = build_where_clause_from_dict(table, record)
        if where_clause:
            stmt = _sa.delete(table).where(sa_elements.and_(*where_clause))
            stmts.append(stmt)
    return stmts
