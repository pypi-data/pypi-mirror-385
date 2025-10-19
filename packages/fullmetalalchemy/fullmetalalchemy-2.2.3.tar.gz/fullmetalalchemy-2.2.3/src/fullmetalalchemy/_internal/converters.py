"""Shared conversion logic for sync and async implementations.

This module handles conversions between types (string to Table, extracting engines, etc.).
Contains both sync and async variants where needed.
"""

import typing as _t

import sqlalchemy as _sa
import sqlalchemy.engine as _sa_engine
import sqlalchemy.orm.session as _sa_session

try:
    from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession

    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
    AsyncEngine = _t.Any  # type: ignore
    AsyncConnection = _t.Any  # type: ignore
    AsyncSession = _t.Any  # type: ignore


# Sync converters
def extract_engine_from_connection(
    connection: _t.Union[_sa_engine.Engine, _sa.engine.Connection, _sa_session.Session],
) -> _sa_engine.Engine:
    """Extract Engine from various connection types (sync).

    Parameters
    ----------
    connection : Union[Engine, Connection, Session]
        Connection object.

    Returns
    -------
    Engine
        SQLAlchemy Engine object.

    Raises
    ------
    TypeError
        If connection type is not supported.
    """
    if isinstance(connection, _sa_engine.Engine):
        return connection
    elif isinstance(connection, _sa.engine.Connection):
        return connection.engine
    elif isinstance(connection, _sa_session.Session):
        bind = connection.get_bind()
        if bind is None:
            raise TypeError("Session is not bound to an engine or connection.")
        if isinstance(bind, _sa.engine.Connection):
            return bind.engine
        if isinstance(bind, _sa_engine.Engine):
            return bind
        raise TypeError("Unsupported bind object returned from session.")
    else:
        raise TypeError("Unsupported connection type provided.")


# Async converters
def extract_async_engine_from_connection(
    connection: _t.Union[_t.Any, _t.Any, _t.Any],  # AsyncEngine, AsyncConnection, AsyncSession
) -> _t.Any:  # AsyncEngine
    """Extract AsyncEngine from various async connection types.

    Parameters
    ----------
    connection : Union[AsyncEngine, AsyncConnection, AsyncSession]
        Async connection object.

    Returns
    -------
    AsyncEngine
        SQLAlchemy AsyncEngine object.

    Raises
    ------
    TypeError
        If connection type is not supported.
    """
    if not ASYNC_AVAILABLE:
        raise ImportError(
            "SQLAlchemy async support not available. "
            "Install with: pip install 'SQLAlchemy[asyncio]'"
        )

    # Check for AsyncEngine
    if isinstance(connection, AsyncEngine):
        return connection
    # Check for AsyncConnection
    elif isinstance(connection, AsyncConnection):
        return connection.engine
    # Check for AsyncSession
    elif isinstance(connection, AsyncSession):
        bind = connection.get_bind()
        if bind is None:
            raise TypeError("AsyncSession is not bound to an engine or connection.")
        if isinstance(bind, AsyncConnection):
            return bind.engine
        if isinstance(bind, AsyncEngine):
            return bind
        raise TypeError("Unsupported bind object returned from async session.")
    else:
        raise TypeError("Unsupported async connection type provided.")
