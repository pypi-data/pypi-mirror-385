"""Shared helper utilities for sync and async implementations.

This module contains utility functions that don't perform I/O operations
and can be safely reused by both sync and async code.
"""

import typing as _t

import sqlalchemy as _sa


def primary_key_columns(table: _sa.Table) -> _t.List[_sa.Column[_t.Any]]:
    """Get primary key columns from table.

    Parameters
    ----------
    table : sqlalchemy.Table
        Table to get primary keys from.

    Returns
    -------
    List[Column]
        List of primary key column objects.
    """
    return [col for col in table.columns if col.primary_key]


def primary_key_names(table: _sa.Table) -> _t.List[str]:
    """Get primary key column names from table.

    Parameters
    ----------
    table : sqlalchemy.Table
        Table to get primary key names from.

    Returns
    -------
    List[str]
        List of primary key column names.
    """
    return [col.name for col in table.columns if col.primary_key]


def missing_primary_key(table: _sa.Table) -> bool:
    """Check if table is missing a primary key.

    Parameters
    ----------
    table : sqlalchemy.Table
        Table to check.

    Returns
    -------
    bool
        True if table has no primary key, False otherwise.
    """
    return len(primary_key_columns(table)) == 0


def get_column(table: _sa.Table, column_name: str) -> _sa.Column[_t.Any]:
    """Get column object from table by name.

    Parameters
    ----------
    table : sqlalchemy.Table
        Table containing the column.
    column_name : str
        Name of the column.

    Returns
    -------
    Column
        SQLAlchemy Column object.

    Raises
    ------
    KeyError
        If column name doesn't exist in table.
    """
    return table.c[column_name]


def get_column_names(table: _sa.Table) -> _t.List[str]:
    """Get all column names from table.

    Parameters
    ----------
    table : sqlalchemy.Table
        Table to get column names from.

    Returns
    -------
    List[str]
        List of all column names.
    """
    return [col.name for col in table.columns]


def process_result_rows(result: _t.Any) -> _t.List[_t.Dict[str, _t.Any]]:
    """Process SQLAlchemy result rows into list of dicts.

    Works with both sync and async result objects.

    Parameters
    ----------
    result : Result
        SQLAlchemy result object.

    Returns
    -------
    List[Dict[str, Any]]
        List of records as dictionaries.
    """
    return [dict(r._mapping) for r in result]
