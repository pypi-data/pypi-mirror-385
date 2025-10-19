"""Tests for records module."""
from fullmetalalchemy.records import filter_record, records_equal


def test_records_equal_same_records():
    """Test records_equal returns True for identical records."""
    records1 = [{'id': 1, 'x': 2}, {'id': 2, 'x': 4}]
    records2 = [{'id': 1, 'x': 2}, {'id': 2, 'x': 4}]
    assert records_equal(records1, records2)


def test_records_equal_different_order_same_content():
    """Test records_equal returns True for same records in different order."""
    records1 = [{'id': 1, 'x': 2}, {'id': 2, 'x': 4}]
    records2 = [{'id': 2, 'x': 4}, {'id': 1, 'x': 2}]
    assert records_equal(records1, records2)


def test_records_equal_different_records():
    """Test records_equal returns False for different records."""
    records1 = [{'id': 1, 'x': 2}]
    records2 = [{'id': 1, 'x': 3}]
    assert not records_equal(records1, records2)


def test_records_equal_different_lengths():
    """Test records_equal returns False for different lengths."""
    records1 = [{'id': 1, 'x': 2}, {'id': 2, 'x': 4}]
    records2 = [{'id': 1, 'x': 2}]
    assert not records_equal(records1, records2)


def test_records_equal_empty_lists():
    """Test records_equal returns True for empty lists."""
    records1 = []
    records2 = []
    assert records_equal(records1, records2)


def test_filter_record():
    """Test filter_record extracts only specified columns."""
    record = {'id': 1, 'name': 'Alice', 'age': 30, 'city': 'NYC'}
    column_names = ['id', 'name']

    result = filter_record(record, column_names)

    assert result == {'id': 1, 'name': 'Alice'}
    assert 'age' not in result
    assert 'city' not in result

