from __future__ import annotations

import typing as _t

import sqlalchemy as _sa

import fullmetalalchemy.delete as _delete
import fullmetalalchemy.drop as _drop
import fullmetalalchemy.insert as _insert
import fullmetalalchemy.types as _types
import fullmetalalchemy.update as _update
from fullmetalalchemy.basetable import BaseTable


class Table(BaseTable):
    """
    Class that combines all (non-session) fullmetalalchemy table functions.
    Methods change SQL table.

    Example
    -------
    >>> from fullmetalalchemy.table import Table

    >>> table = Table('xy', engine)
    >>> table.insert_records([{'id': 5, 'x': 5, 'y': 9}])
    >>> table.update_records([{'id': 2, 'x': 33, 'y': 8}])
    """

    def __repr__(self) -> str:
        return (
            f"Table(name={self.name}, columns={self.column_names}, "
            f"pks={self.primary_key_names}, types={self.column_types})"
        )

    def drop(self, if_exists: bool = True) -> None:
        _drop.drop_table(self.sa_table, self.engine, if_exists, self.schema)  # type: ignore

    def delete_records(self, column_name: str, values: _t.Sequence[_t.Any]) -> None:
        _delete.delete_records(self.sa_table, column_name, values)

    def delete_records_by_values(self, records: _t.List[_t.Dict[str, _t.Any]]) -> None:
        _delete.delete_records_by_values(self.sa_table, records, self.engine)  # type: ignore

    def delete_all_records(self) -> None:
        _delete.delete_all_records(self.sa_table, self.engine)  # type: ignore

    def insert_from_table(self, sa_table: _sa.Table) -> None:
        _insert.insert_from_table(self.sa_table, sa_table, self.engine)  # type: ignore

    def insert_records(self, records: _t.Sequence[_types.Record]) -> None:
        _insert.insert_records(self.sa_table, records, self.engine)  # type: ignore

    def update_matching_records(
        self, records: _t.Sequence[_types.Record], match_column_names: _t.Sequence[str]
    ) -> None:
        _update.update_matching_records(self.sa_table, records, match_column_names, self.engine)  # type: ignore

    def update_records(
        self,
        records: _t.Sequence[_types.Record],
        match_column_names: _t.Sequence[str] | None = None,
    ) -> None:
        _update.update_records(self.sa_table, records, self.engine, match_column_names)  # type: ignore

    def set_column_values(self, column_name: str, value: _t.Any) -> None:
        _update.set_column_values(self.sa_table, column_name, value, self.engine)  # type: ignore
