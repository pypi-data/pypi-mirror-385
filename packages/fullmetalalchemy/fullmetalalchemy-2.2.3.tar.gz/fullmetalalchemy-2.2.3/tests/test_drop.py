import pytest

import fullmetalalchemy as fa
from fullmetalalchemy.drop import drop_table
from fullmetalalchemy.features import get_table_names


def test_drop_table(engine_and_table):
    """Test dropping a table from the database."""
    engine, table = engine_and_table
    names = get_table_names(engine)
    assert names == ["xy"]

    drop_table(table, engine)
    names = get_table_names(engine)
    assert names == []


def test_drop_table_by_string_name(engine_and_table):
    """Test dropping a table using string name."""
    engine, _ = engine_and_table
    names = get_table_names(engine)
    assert "xy" in names

    drop_table("xy", engine)
    names = get_table_names(engine)
    assert "xy" not in names


def test_drop_table_if_exists_true_nonexistent():
    """Test dropping nonexistent table with if_exists=True."""
    engine = fa.create_engine("sqlite://")

    # Should not raise error
    drop_table("nonexistent", engine, if_exists=True)

    names = get_table_names(engine)
    assert "nonexistent" not in names


def test_drop_table_string_no_engine():
    """Test dropping table by string name without engine raises ValueError."""
    with pytest.raises(ValueError, match="Must pass engine if table is str"):
        drop_table("xy", None)
