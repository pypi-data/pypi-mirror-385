"""
Functions for manipulating and comparing records.
"""

import typing as _t

from frozendict import frozendict

import fullmetalalchemy.types as _types


def filter_record(
    record: _types.Record,
    column_names: _t.Sequence[str]
) -> _t.Dict[str, _t.Any]:
    """
    Filter out the given columns from the record.

    Parameters
    ----------
    record : dict
        The record to filter columns from.
    column_names : sequence of str
        The names of the columns to keep in the record.

    Returns
    -------
    dict
        The record with only the specified columns.

    Examples
    --------
    >>> import fullmetalalchemy as fa

    >>> record = {'id': 1, 'x': 2, 'y': 3}
    >>> column_names = ['id', 'x']
    >>> fa.update.filter_record(record, column_names)
    {'id': 1, 'x': 2}
    """
    return {column_name: record[column_name] for column_name in column_names}


def records_equal(
    records1: _t.Sequence[_types.Record],
    records2: _t.Sequence[_types.Record],
) -> bool:
    """
    Check if two sets of records contain the same records.

    Parameters
    ----------
    records1 : Sequence[Record]
        The first set of records to compare.
    records2 : Sequence[Record]
        The second set of records to compare.

    Returns
    -------
    bool
        True if both sets of records contain the same records; False otherwise.

    Examples
    --------
    >>> records1 = [{'id': 1, 'x': 1, 'y': 4},
    ...             {'id': 2, 'x': 1, 'y': 4},
    ...             {'id': 3, 'x': 1, 'y': 4}]
    >>> records2 = [{'id': 2, 'x': 1, 'y': 4},
    ...             {'id': 3, 'x': 1, 'y': 4},
    ...             {'id': 1, 'x': 1, 'y': 4}]
    >>> records_equal(records1, records2)
    True
    """
    if len(records1) != len(records2):
        return False
    if len(records1) == 0:
        return True

    frozen_records1 = {frozendict(record) for record in records1}
    frozen_records2 = {frozendict(record) for record in records2}
    return frozen_records1 == frozen_records2
