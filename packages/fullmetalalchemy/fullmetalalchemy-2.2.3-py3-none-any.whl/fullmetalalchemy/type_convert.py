"""
Functions for converting between Python and SQL data types.
"""

import datetime as _datetime
import decimal as _decimal
import typing as _t

from sqlalchemy import sql as _sql


def sql_type(t: type) -> _t.Any:
    return _type_convert[t]


def python_type(t: _t.Any) -> type:
    return _sql_to_python[t]


_type_convert = {
    int: _sql.sqltypes.Integer,
    str: _sql.sqltypes.Unicode,
    float: _sql.sqltypes.Float,
    _decimal.Decimal: _sql.sqltypes.Numeric,
    _datetime.datetime: _sql.sqltypes.DateTime,
    bytes: _sql.sqltypes.LargeBinary,
    bool: _sql.sqltypes.Boolean,
    _datetime.date: _sql.sqltypes.Date,
    _datetime.time: _sql.sqltypes.Time,
    _datetime.timedelta: _sql.sqltypes.Interval,
    list: _sql.sqltypes.ARRAY,
    dict: _sql.sqltypes.JSON,
}

_sql_to_python = {
    _sql.sqltypes.Integer: int,
    _sql.sqltypes.SmallInteger: int,
    _sql.sqltypes.SMALLINT: int,
    _sql.sqltypes.BigInteger: int,
    _sql.sqltypes.BIGINT: int,
    _sql.sqltypes.INTEGER: int,
    _sql.sqltypes.Unicode: str,
    _sql.sqltypes.NVARCHAR: str,
    _sql.sqltypes.NCHAR: str,
    _sql.sqltypes.Float: _decimal.Decimal,
    _sql.sqltypes.REAL: _decimal.Decimal,
    _sql.sqltypes.FLOAT: _decimal.Decimal,
    _sql.sqltypes.Numeric: _decimal.Decimal,
    _sql.sqltypes.NUMERIC: _decimal.Decimal,
    _sql.sqltypes.DECIMAL: _decimal.Decimal,
    _sql.sqltypes.DateTime: _datetime.datetime,
    _sql.sqltypes.TIMESTAMP: _datetime.datetime,
    _sql.sqltypes.DATETIME: _datetime.datetime,
    _sql.sqltypes.LargeBinary: bytes,
    _sql.sqltypes.BLOB: bytes,
    _sql.sqltypes.Boolean: bool,
    _sql.sqltypes.BOOLEAN: bool,
    _sql.sqltypes.MatchType: bool,
    _sql.sqltypes.Date: _datetime.date,
    _sql.sqltypes.DATE: _datetime.date,
    _sql.sqltypes.Time: _datetime.time,
    _sql.sqltypes.TIME: _datetime.time,
    _sql.sqltypes.Interval: _datetime.timedelta,
    _sql.sqltypes.ARRAY: list,
    _sql.sqltypes.JSON: dict,
}


def get_sql_types(data: _t.Mapping[str, _t.Sequence[_t.Any]]) -> _t.List[_t.Any]:
    return [get_sql_type(values) for values in data.values()]


def get_sql_type(values: _t.Sequence[_t.Any]) -> _t.Any:
    for python_type in _type_convert:
        if all(isinstance(val, python_type) for val in values):
            return _type_convert[python_type]
    return _type_convert[str]
