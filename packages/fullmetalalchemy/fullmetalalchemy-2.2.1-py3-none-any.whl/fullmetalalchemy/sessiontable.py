from __future__ import annotations

import typing as _t

import sqlalchemy as _sa
import sqlalchemy.engine as _sa_engine
import sqlalchemy.orm.session as _sa_session

import fullmetalalchemy.delete as _delete
import fullmetalalchemy.features as _features
import fullmetalalchemy.insert as _insert
import fullmetalalchemy.types as _types
import fullmetalalchemy.update as _update
from fullmetalalchemy.basetable import BaseTable


class SessionTable(BaseTable):
    """
    Class that combines all session FullmetalAlchemy table functions.
    Methods add changes to session.
    Call commit method to commit all changes added to session.
    Call rollback method to reverse all changes added to session.
    Use context manager to rollback all changes on error.

    Examples
    --------
    >>> from fullmetalalchemy.sessiontable import SessionTable

    >>> table = SessionTable('xy', engine)
    >>> table.insert_records([{'id': 5, 'x': 5, 'y': 9}])
    >>> table.update_records([{'id': 2, 'x': 33, 'y': 8}])
    >>> table.commit()

    Same but using context manager
    >>> with SessionTable('xy', engine) as table:
    >>>    table.insert_records([{'id': 5, 'x': 5, 'y': 9}])
    >>>    table.update_records([{'id': 2, 'x': 33, 'y': 8}])

    See Also
    --------
    fullmetalalchemy.table.Table
    """

    def __init__(
        self, name: str, engine: _sa_engine.Engine | _sa_session.Session, schema: str | None = None
    ) -> None:
        super().__init__(name, engine, schema)
        if type(engine) is _sa_session.Session:
            self.session = engine
        elif type(engine) is _sa_engine.Engine:
            self.session = _features.get_session(engine)
        else:
            raise TypeError("engine must be SqlAlchemy Engine or Session")

    def __enter__(self) -> SessionTable:
        return self

    def __exit__(
        self,
        exc_type: _t.Optional[_t.Type[BaseException]],
        exc_value: _t.Optional[BaseException],
        traceback: _t.Optional[_t.Any],
    ) -> None:
        if exc_type and exc_value:
            self.rollback()
            raise exc_value
        else:
            self.commit()

    def __repr__(self) -> str:
        return (
            f"SessionTable(name={self.name}, columns={self.column_names}, "
            f"pks={self.primary_key_names}, types={self.column_types})"
        )

    def commit(self) -> SessionTable:
        """Commit session, return new SessionTable"""
        self.session.commit()
        return SessionTable(self.name, self.engine, self.schema)

    def rollback(self) -> SessionTable:
        """Rollback session, return new SessionTable"""
        self.session.rollback()
        return SessionTable(self.name, self.engine, self.schema)

    def delete_records(self, column_name: str, values: _t.Sequence[_t.Any]) -> None:
        _delete.delete_records_session(self.sa_table, column_name, values, self.session)

    def delete_records_by_values(self, records: _t.List[_t.Dict[str, _t.Any]]) -> None:
        _delete.delete_records_by_values_session(self.sa_table, records, self.session)

    def delete_all_records(self) -> None:
        _delete.delete_all_records_session(self.sa_table, self.session)

    def insert_from_table(self, sa_table: _sa.Table) -> None:
        _insert.insert_from_table_session(self.sa_table, sa_table, self.session)

    def insert_records(self, records: _t.Sequence[_types.Record]) -> None:
        _insert.insert_records_session(self.sa_table, records, self.session)

    def update_matching_records(
        self, records: _t.Sequence[_types.Record], match_column_names: _t.Sequence[str]
    ) -> None:
        _update.update_matching_records_session(
            self.sa_table, records, match_column_names, self.session
        )

    def update_records(
        self,
        records: _t.Sequence[_types.Record],
        match_column_names: _t.Sequence[str] | None = None,
    ) -> None:
        _update.update_records_session(self.sa_table, records, self.session, match_column_names)

    def set_column_values(self, column_name: str, value: _t.Any) -> None:
        _update.set_column_values_session(self.sa_table, column_name, value, self.session)
