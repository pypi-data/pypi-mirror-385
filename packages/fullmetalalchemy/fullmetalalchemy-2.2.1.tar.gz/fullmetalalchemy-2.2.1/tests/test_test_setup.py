"""Tests for test_setup module."""

import sqlalchemy as sa

from fullmetalalchemy.test_setup import create_second_test_table, setup


def test_setup_function():
    """Test setup function creates and populates table."""
    engine = sa.create_engine("sqlite://")

    table = setup(engine)

    assert table.name == "xy"
    assert len(table.columns) == 3


def test_create_second_test_table():
    """Test create_second_test_table function."""
    engine = sa.create_engine("sqlite://")

    table = create_second_test_table(engine)

    assert table.name == "xyz"
    assert len(table.columns) == 4
