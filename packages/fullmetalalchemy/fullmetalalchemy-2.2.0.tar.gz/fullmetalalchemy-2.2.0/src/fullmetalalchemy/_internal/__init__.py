"""Internal shared logic modules for FullmetalAlchemy.

This package contains shared logic used by both sync and async implementations
to minimize code duplication. These modules are private and not part of the
public API.

Modules:
    query_builders: SQL query construction (no I/O)
    validators: Input validation and type checking
    converters: Table/engine/connection conversions
    helpers: Shared utilities (PK operations, columns, etc.)
"""

__all__ = ["converters", "helpers", "query_builders", "validators"]
