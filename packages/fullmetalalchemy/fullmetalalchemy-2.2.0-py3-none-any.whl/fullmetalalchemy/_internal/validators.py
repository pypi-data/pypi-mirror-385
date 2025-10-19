"""Shared validation logic for sync and async implementations.

This module contains validation functions that don't perform I/O operations.
"""

import typing as _t


def validate_records(records: _t.Any) -> None:
    """Validate that records is a sequence of dictionaries.

    Parameters
    ----------
    records : Any
        Value to validate.

    Raises
    ------
    TypeError
        If records is not a sequence of dictionaries.
    """
    if not isinstance(records, (list, tuple)):
        raise TypeError("records must be a sequence (list or tuple)")

    for record in records:
        if not isinstance(record, dict):
            raise TypeError("Each record must be a dictionary")


def validate_slice_params(start: _t.Optional[int], stop: _t.Optional[int]) -> None:
    """Validate slice parameters.

    Parameters
    ----------
    start : Optional[int]
        Start index.
    stop : Optional[int]
        Stop index.

    Raises
    ------
    ValueError
        If stop < start (after normalization).
    """
    if start is not None and stop is not None and stop < start:
        raise ValueError("stop cannot be less than start")


def validate_primary_key_value(primary_key_value: _t.Dict[str, _t.Any]) -> None:
    """Validate primary key value dictionary.

    Parameters
    ----------
    primary_key_value : Dict[str, Any]
        Primary key values.

    Raises
    ------
    ValueError
        If primary key dictionary is empty.
    """
    if not primary_key_value:
        raise ValueError("Primary key value dictionary cannot be empty")
