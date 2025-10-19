from __future__ import annotations

import typing as _t

import sqlalchemy as _sa
import sqlalchemy.engine as _sa_engine
import sqlalchemy.orm.session as _sa_session
from hasattrs import has_iterable_attrs  # type: ignore[import-untyped]

import fullmetalalchemy.features as _features
import fullmetalalchemy.select as _select
import fullmetalalchemy.types as _types

Record = _t.Dict[str, _t.Any]


class BaseTable:
    """
    Base table class for fullmetalalchemy.table.Table
    and fullmetalalchemy.sessiontable.SessionTable to inherit
    """

    def __init__(
        self, name: str, engine: _sa_engine.Engine | _sa_session.Session, schema: str | None = None
    ) -> None:
        self.name = name
        if type(engine) is _sa_session.Session:
            self.engine: _sa_engine.Engine | _sa_session.Session = engine
        else:
            self.engine = engine
        self.schema = schema

    def __len__(self) -> int:
        return _features.get_row_count(self.sa_table, self.engine)

    def __eq__(self, other: _t.Any) -> bool:
        return _features.tables_metadata_equal(self.sa_table, other)

    def __getitem__(
        self, key: _t.Union[int, str, slice]
    ) -> _t.Union[_t.Dict[str, _t.Any], _t.List[_t.Any]]:
        """get records based on what type key is"""
        # int: a record at index
        if type(key) is int:
            return self.select_record_by_index(key)
        # str: a list of values for a named column
        elif type(key) is str:
            return self.select_column_values_all(key)
        # slice: a list of records
        elif type(key) is slice:
            return self.select_records_slice(key.start, key.stop)
        else:
            raise ValueError("key must be int, str, or slice")

    def __add__(
        self, other: _t.Union[_t.Dict[str, _t.Any], _t.Iterable[_t.Dict[str, _t.Any]]]
    ) -> None:
        """insert records from other"""
        # dict: insert a record
        if isinstance(other, dict):
            self.insert_records([other])
        # iterable[dict]: insert each record
        elif has_iterable_attrs(other):
            self.insert_records(list(other))

    def __sub__(
        self, other: _t.Union[_t.Dict[str, _t.Any], _t.Iterable[_t.Dict[str, _t.Any]]]
    ) -> None:
        """delete record that match other"""
        # dict: delete all records that match values
        if isinstance(other, dict):
            self.delete_records_by_values([other])
        # iterable[dict]: delete all records that match each record
        elif has_iterable_attrs(other):
            self.delete_records_by_values(list(other))

    def __delitem__(self, key: _t.Union[int, slice]) -> None:
        """delete records based on type of key"""
        # int: delete record at index
        if type(key) is int:
            record = self.select_record_by_index(key)
            self.delete_records_by_values([record])
        # slice: delete records in index slice
        elif type(key) is slice:
            records = self.select_records_slice(key.start, key.stop)
            self.delete_records_by_values(records)

    @property
    def records(self) -> _t.List[Record]:
        return self.select_records_all()

    @property
    def columns(self) -> _t.List[str]:
        return self.column_names

    def insert_records(self, records: _t.List[_t.Dict[str, _t.Any]]) -> None:
        raise NotImplementedError

    def delete_records_by_values(self, records: _t.List[_t.Dict[str, _t.Any]]) -> None:
        raise NotImplementedError

    @property
    def sa_table(self) -> _sa.Table:
        return _features.get_table(self.name, self.engine, self.schema)

    @property
    def row_count(self) -> int:
        return _features.get_row_count(self.sa_table, self.engine)

    @property
    def primary_key_names(self) -> list[str]:
        return _features.primary_key_names(self.sa_table)

    @property
    def column_names(self) -> list[str]:
        return _features.get_column_names(self.sa_table)

    @property
    def column_types(self) -> _t.Dict[str, _t.Any]:
        return _features.get_column_types(self.sa_table)

    def select_records_all(
        self, sorted: bool = False, include_columns: _t.Sequence[str] | None = None
    ) -> _t.List[_types.Record]:
        return _select.select_records_all(self.sa_table, self.engine, sorted, include_columns)

    def select_records_chunks(
        self,
        chunksize: int = 2,
        sorted: bool = False,
        include_columns: _t.Sequence[str] | None = None,
    ) -> _t.Generator[_t.List[_types.Record], None, None]:
        return _select.select_records_chunks(
            self.sa_table, self.engine, chunksize, sorted, include_columns
        )

    def select_existing_values(
        self, column_name: str, values: _t.Sequence[_t.Any]
    ) -> _t.List[_t.Any]:
        return _select.select_existing_values(self.sa_table, column_name, values)

    def select_column_values_all(self, column_name: str) -> _t.List[_t.Any]:
        return _select.select_column_values_all(self.sa_table, column_name, self.engine)

    def select_column_values_chunks(
        self, column_name: str, chunksize: int
    ) -> _t.Generator[_t.Sequence[_t.Any], None, None]:
        return _select.select_column_values_chunks(
            self.sa_table, column_name, chunksize, self.engine
        )

    def select_records_slice(
        self,
        start: int | None = None,
        stop: int | None = None,
        sorted: bool = False,
        include_columns: _t.Sequence[str] | None = None,
    ) -> list[_types.Record]:
        return _select.select_records_slice(
            self.sa_table, start, stop, self.engine, sorted, include_columns
        )

    def select_column_values_by_slice(
        self, column_name: str, start: int | None = None, stop: int | None = None
    ) -> _t.List[_t.Any]:
        return _select.select_column_values_by_slice(
            self.sa_table, column_name, start, stop, self.engine
        )

    def select_column_value_by_index(self, column_name: str, index: int) -> _t.Any:
        return _select.select_column_value_by_index(self.sa_table, column_name, index, self.engine)

    def select_record_by_index(self, index: int) -> dict[str, _t.Any]:
        return _select.select_record_by_index(self.sa_table, index, self.engine)

    def select_primary_key_records_by_slice(
        self, _slice: slice, sorted: bool = False
    ) -> list[_types.Record]:
        return _select.select_primary_key_records_by_slice(
            self.sa_table, _slice, self.engine, sorted
        )

    def select_record_by_primary_key(
        self, primary_key_value: _types.Record, include_columns: _t.Sequence[str] | None = None
    ) -> _types.Record:
        return _select.select_record_by_primary_key(
            self.sa_table, primary_key_value, self.engine, include_columns
        )

    def select_records_by_primary_keys(
        self,
        primary_keys_values: _t.Sequence[_types.Record],
        schema: str | None = None,
        include_columns: _t.Sequence[str] | None = None,
    ) -> list[_types.Record]:
        return _select.select_records_by_primary_keys(
            self.sa_table, primary_keys_values, self.engine, schema, include_columns
        )

    def select_column_values_by_primary_keys(
        self, column_name: str, primary_keys_values: _t.Sequence[_types.Record]
    ) -> _t.List[_t.Any]:
        return _select.select_column_values_by_primary_keys(
            self.sa_table, column_name, primary_keys_values, self.engine
        )

    def select_value_by_primary_keys(
        self, column_name: str, primary_key_value: _types.Record, schema: str | None = None
    ) -> _t.Any:
        return _select.select_value_by_primary_keys(
            self.sa_table, column_name, primary_key_value, self.engine, schema
        )
