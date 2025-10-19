"""Tests for type_convert module."""
import datetime
import decimal

from sqlalchemy import sql

from fullmetalalchemy.type_convert import (
    get_sql_type,
    get_sql_types,
    python_type,
    sql_type,
)


def test_sql_type_int():
    """Test sql_type returns correct SQLAlchemy type for int."""
    result = sql_type(int)
    assert result == sql.sqltypes.Integer


def test_sql_type_str():
    """Test sql_type returns correct SQLAlchemy type for str."""
    result = sql_type(str)
    assert result == sql.sqltypes.Unicode


def test_sql_type_float():
    """Test sql_type returns correct SQLAlchemy type for float."""
    result = sql_type(float)
    assert result == sql.sqltypes.Float


def test_sql_type_decimal():
    """Test sql_type returns correct SQLAlchemy type for Decimal."""
    result = sql_type(decimal.Decimal)
    assert result == sql.sqltypes.Numeric


def test_sql_type_datetime():
    """Test sql_type returns correct SQLAlchemy type for datetime."""
    result = sql_type(datetime.datetime)
    assert result == sql.sqltypes.DateTime


def test_sql_type_bytes():
    """Test sql_type returns correct SQLAlchemy type for bytes."""
    result = sql_type(bytes)
    assert result == sql.sqltypes.LargeBinary


def test_sql_type_bool():
    """Test sql_type returns correct SQLAlchemy type for bool."""
    result = sql_type(bool)
    assert result == sql.sqltypes.Boolean


def test_python_type_integer():
    """Test python_type returns int for SQL Integer."""
    result = python_type(sql.sqltypes.Integer)
    assert result is int


def test_python_type_unicode():
    """Test python_type returns str for SQL Unicode."""
    result = python_type(sql.sqltypes.Unicode)
    assert result is str


def test_python_type_float():
    """Test python_type returns Decimal for SQL Float."""
    result = python_type(sql.sqltypes.Float)
    assert result == decimal.Decimal


def test_get_sql_types_basic():
    """Test get_sql_types with basic data types."""
    data = {
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'score': [95.5, 87.3, 92.1]
    }
    results = get_sql_types(data)
    assert len(results) == 3
    assert results[0] == sql.sqltypes.Integer
    assert results[1] == sql.sqltypes.Unicode
    assert results[2] == sql.sqltypes.Float


def test_get_sql_type_all_int():
    """Test get_sql_type with all integer values."""
    values = [1, 2, 3, 4, 5]
    result = get_sql_type(values)
    assert result == sql.sqltypes.Integer


def test_get_sql_type_all_str():
    """Test get_sql_type with all string values."""
    values = ['a', 'b', 'c']
    result = get_sql_type(values)
    assert result == sql.sqltypes.Unicode


def test_get_sql_type_mixed_types_fallback():
    """Test get_sql_type falls back to str for mixed types."""
    values = [1, 'a', 2.5, None]
    result = get_sql_type(values)
    assert result == sql.sqltypes.Unicode


def test_get_sql_type_empty_sequence():
    """Test get_sql_type with empty sequence returns Integer (first type checked)."""
    values = []
    result = get_sql_type(values)
    # Empty sequence matches all types, returns first one (int)
    assert result == sql.sqltypes.Integer


def test_get_sql_type_datetime():
    """Test get_sql_type with datetime values."""
    values = [datetime.datetime.now(), datetime.datetime(2020, 1, 1)]
    result = get_sql_type(values)
    assert result == sql.sqltypes.DateTime


def test_get_sql_type_date():
    """Test get_sql_type with date values."""
    values = [datetime.date.today(), datetime.date(2020, 1, 1)]
    result = get_sql_type(values)
    assert result == sql.sqltypes.Date


def test_get_sql_type_bool():
    """Test get_sql_type with boolean values returns Integer (bool is subclass of int)."""
    values = [True, False, True]
    result = get_sql_type(values)
    # In Python, bool is subclass of int, so isinstance(True, int) is True
    assert result == sql.sqltypes.Integer


def test_get_sql_type_bytes():
    """Test get_sql_type with bytes values."""
    values = [b'hello', b'world']
    result = get_sql_type(values)
    assert result == sql.sqltypes.LargeBinary

