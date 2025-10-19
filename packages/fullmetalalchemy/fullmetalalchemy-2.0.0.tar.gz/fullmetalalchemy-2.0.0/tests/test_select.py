import pytest

import fullmetalalchemy as fa
from fullmetalalchemy.records import records_equal


def test_select_records_all(engine_and_table):
    """Test select records all."""
    engine, table = engine_and_table
    results = fa.select.select_records_all(table, engine)
    expected = [{'id': 1, 'x': 1, 'y': 2},
                {'id': 2, 'x': 2, 'y': 4},
                {'id': 3, 'x': 4, 'y': 8},
                {'id': 4, 'x': 8, 'y': 11}]
    equals = records_equal(results, expected)
    assert equals

def test_select_records_all_table_name(engine_and_table):
    """Test select records all table name."""
    engine, _table = engine_and_table
    results = fa.select.select_records_all('xy', engine)
    expected = [{'id': 1, 'x': 1, 'y': 2},
                {'id': 2, 'x': 2, 'y': 4},
                {'id': 3, 'x': 4, 'y': 8},
                {'id': 4, 'x': 8, 'y': 11}]
    equals = records_equal(results, expected)
    assert equals

def test_select_records_all_no_engine(engine_and_table):
    """Test select records all no engine."""
    _engine, table = engine_and_table
    results = fa.select.select_records_all(table)
    expected = [{'id': 1, 'x': 1, 'y': 2},
                {'id': 2, 'x': 2, 'y': 4},
                {'id': 3, 'x': 4, 'y': 8},
                {'id': 4, 'x': 8, 'y': 11}]
    equals = records_equal(results, expected)
    assert equals

def test_select_records_chunks(engine_and_table):
    """Test select records chunks."""
    engine, table = engine_and_table
    records_chunks = fa.select.select_records_chunks(table, engine)
    results = next(records_chunks)
    expected = [{'id': 1, 'x': 1, 'y': 2},
                {'id': 2, 'x': 2, 'y': 4}]
    equals = records_equal(results, expected)
    assert equals
    results = next(records_chunks)
    expected = [{'id': 3, 'x': 4, 'y': 8},
                {'id': 4, 'x': 8, 'y': 11}]
    equals = records_equal(results, expected)
    assert equals

def test_select_records_chunks_table_name(engine_and_table):
    """Test select records chunks table name."""
    engine, _table = engine_and_table
    records_chunks = fa.select.select_records_chunks('xy', engine)
    results = next(records_chunks)
    expected = [{'id': 1, 'x': 1, 'y': 2},
                {'id': 2, 'x': 2, 'y': 4}]
    equals = records_equal(results, expected)
    assert equals
    results = next(records_chunks)
    expected = [{'id': 3, 'x': 4, 'y': 8},
                {'id': 4, 'x': 8, 'y': 11}]
    equals = records_equal(results, expected)
    assert equals

def test_select_records_chunks_no_engine(engine_and_table):
    """Test select records chunks no engine."""
    _engine, table = engine_and_table
    records_chunks = fa.select.select_records_chunks(table)
    results = next(records_chunks)
    expected = [{'id': 1, 'x': 1, 'y': 2},
                {'id': 2, 'x': 2, 'y': 4}]
    equals = records_equal(results, expected)
    assert equals
    results = next(records_chunks)
    expected = [{'id': 3, 'x': 4, 'y': 8},
                {'id': 4, 'x': 8, 'y': 11}]
    equals = records_equal(results, expected)
    assert equals

def test_select_existing_values(engine_and_table):
    """Test select existing values."""
    engine, table = engine_and_table
    values = [1, 2, 3, 4, 5]
    results = set(fa.select.select_existing_values(table, 'x', values, engine))
    expected = {1, 2, 4}
    assert results == expected

def test_select_existing_values_table_name(engine_and_table):
    """Test select existing values table name."""
    engine, _table = engine_and_table
    values = [1, 2, 3, 4, 5]
    results = set(fa.select.select_existing_values('xy', 'x', values, engine))
    expected = {1, 2, 4}
    assert results == expected

def test_select_existing_values_no_engine(engine_and_table):
    """Test select existing values no engine."""
    _engine, table = engine_and_table
    values = [1, 2, 3, 4, 5]
    results = set(fa.select.select_existing_values(table, 'x', values))
    expected = {1, 2, 4}
    assert results == expected

def test_select_column_values_all(engine_and_table):
    """Test select column values all."""
    engine, table = engine_and_table
    results = set(fa.select.select_column_values_all(table, 'x', engine))
    expected = {1, 2, 4, 8}
    assert results == expected

def test_select_column_values_all_table_name(engine_and_table):
    """Test select column values all table name."""
    engine, _table = engine_and_table
    results = set(fa.select.select_column_values_all('xy', 'x', engine))
    expected = {1, 2, 4, 8}
    assert results == expected

def test_select_column_values_all_no_engine(engine_and_table):
    """Test select column values all no engine."""
    _engine, table = engine_and_table
    results = set(fa.select.select_column_values_all(table, 'x'))
    expected = {1, 2, 4, 8}
    assert results == expected

def test_select_column_values_chunks(engine_and_table):
    """Test select column values chunks."""
    engine, table = engine_and_table
    col_chunks = fa.select.select_column_values_chunks(table, 'x', 2, engine)
    results = next(col_chunks)
    expected = [1, 2]
    assert results == expected
    results = next(col_chunks)
    expected = [4, 8]
    assert results == expected

def test_select_column_values_chunks_table_name(engine_and_table):
    """Test select column values chunks table name."""
    engine, _table = engine_and_table
    col_chunks = fa.select.select_column_values_chunks('xy', 'x', 2, engine)
    results = next(col_chunks)
    expected = [1, 2]
    assert results == expected
    results = next(col_chunks)
    expected = [4, 8]
    assert results == expected

def test_select_column_values_chunks_no_engine(engine_and_table):
    """Test select column values chunks no engine."""
    _engine, table = engine_and_table
    col_chunks = fa.select.select_column_values_chunks(table, 'x', 2)
    results = next(col_chunks)
    expected = [1, 2]
    assert results == expected
    results = next(col_chunks)
    expected = [4, 8]
    assert results == expected

def test_select_records_slice(engine_and_table):
    """Test select records slice."""
    engine, table = engine_and_table
    results = fa.select.select_records_slice(table, start=1, stop=3, connection=engine)
    expected = [{'id': 2, 'x': 2, 'y': 4},
                {'id': 3, 'x': 4, 'y': 8}]
    equals = records_equal(results, expected)
    assert equals

def test_select_records_slice_table_name(engine_and_table):
    """Test select records slice table name."""
    engine, _table = engine_and_table
    results = fa.select.select_records_slice('xy', start=1, stop=3, connection=engine)
    expected = [{'id': 2, 'x': 2, 'y': 4},
                {'id': 3, 'x': 4, 'y': 8}]
    equals = records_equal(results, expected)
    assert equals

def test_select_records_slice_no_engine(engine_and_table):
    """Test select records slice no engine."""
    _engine, table = engine_and_table
    results = fa.select.select_records_slice(table, start=1, stop=3)
    expected = [{'id': 2, 'x': 2, 'y': 4},
                {'id': 3, 'x': 4, 'y': 8}]
    equals = records_equal(results, expected)
    assert equals

def test_select_column_values_by_slice(engine_and_table):
    """Test select column values by slice."""
    engine, table = engine_and_table
    results = fa.select.select_column_values_by_slice(table, 'y', start=1, stop=3, connection=engine)
    expected = [4, 8]
    assert results == expected

def test_select_column_values_by_slice_table_name(engine_and_table):
    """Test select column values by slice table name."""
    engine, _table = engine_and_table
    results = fa.select.select_column_values_by_slice('xy', 'y', start=1, stop=3, connection=engine)
    expected = [4, 8]
    assert results == expected

def test_select_column_values_by_slice_no_engine(engine_and_table):
    """Test select column values by slice no engine."""
    _engine, table = engine_and_table
    results = fa.select.select_column_values_by_slice(table, 'y', start=1, stop=3)
    expected = [4, 8]
    assert results == expected

def test_select_column_value_by_index(engine_and_table):
    """Test select column value by index."""
    engine, table = engine_and_table
    result = fa.select.select_column_value_by_index(table, 'y', 2, engine)
    expected = 8
    assert result == expected

def test_select_column_value_by_index_table_name(engine_and_table):
    """Test select column value by index table name."""
    engine, _table = engine_and_table
    result = fa.select.select_column_value_by_index('xy', 'y', 2, engine)
    expected = 8
    assert result == expected

def test_select_column_value_by_index_no_engine(engine_and_table):
    """Test select column value by index no engine."""
    _engine, table = engine_and_table
    result = fa.select.select_column_value_by_index(table, 'y', 2)
    expected = 8
    assert result == expected

def test_select_record_by_index(engine_and_table):
    """Test select record by index."""
    engine, table = engine_and_table
    result = fa.select.select_record_by_index(table, 2, engine)
    expected = {'id': 3, 'x': 4, 'y': 8}
    assert result == expected

def test_select_record_by_index_table_name(engine_and_table):
    """Test select record by index table name."""
    engine, _table = engine_and_table
    result = fa.select.select_record_by_index('xy', 2, engine)
    expected = {'id': 3, 'x': 4, 'y': 8}
    assert result == expected

def test_select_record_by_index_no_engine(engine_and_table):
    """Test select record by index no engine."""
    _engine, table = engine_and_table
    result = fa.select.select_record_by_index(table, 2)
    expected = {'id': 3, 'x': 4, 'y': 8}
    assert result == expected

def test_select_primary_key_records_by_slice(engine_and_table):
    """Test select primary key records by slice."""
    engine, table = engine_and_table
    results = fa.select.select_primary_key_records_by_slice(table, slice(1, 3), engine)
    expected = [{'id': 2}, {'id': 3}]
    equals = records_equal(results, expected)
    assert equals

def test_select_primary_key_records_by_slice_table_name(engine_and_table):
    """Test select primary key records by slice table name."""
    engine, _table = engine_and_table
    results = fa.select.select_primary_key_records_by_slice('xy', slice(1, 3), engine)
    expected = [{'id': 2}, {'id': 3}]
    equals = records_equal(results, expected)
    assert equals

def test_select_primary_key_records_by_slice_no_engine(engine_and_table):
    """Test select primary key records by slice no engine."""
    _engine, table = engine_and_table
    results = fa.select.select_primary_key_records_by_slice(table, slice(1, 3))
    expected = [{'id': 2}, {'id': 3}]
    equals = records_equal(results, expected)
    assert equals

def test_select_record_by_primary_key(engine_and_table):
    """Test select record by primary key."""
    engine, table = engine_and_table
    result = fa.select.select_record_by_primary_key(table, {'id': 3}, engine)
    expected = {'id': 3, 'x': 4, 'y': 8}
    assert result == expected

def test_select_record_by_primary_key_table_name(engine_and_table):
    """Test select record by primary key table name."""
    engine, _table = engine_and_table
    result = fa.select.select_record_by_primary_key('xy', {'id': 3}, engine)
    expected = {'id': 3, 'x': 4, 'y': 8}
    assert result == expected

def test_select_record_by_primary_key_no_engine(engine_and_table):
    """Test select record by primary key no engine."""
    _engine, table = engine_and_table
    result = fa.select.select_record_by_primary_key(table, {'id': 3})
    expected = {'id': 3, 'x': 4, 'y': 8}
    assert result == expected

def test_select_records_by_primary_keys(engine_and_table):
    """Test select records by primary keys."""
    engine, table = engine_and_table
    results = fa.select.select_records_by_primary_keys(table, [{'id': 3}, {'id': 1}], engine)
    expected = [{'id': 1, 'x': 1, 'y': 2},
                {'id': 3, 'x': 4, 'y': 8}]
    equals = records_equal(results, expected)
    assert equals

def test_select_records_by_primary_keys_table_name(engine_and_table):
    """Test select records by primary keys table name."""
    engine, _table = engine_and_table
    results = fa.select.select_records_by_primary_keys('xy', [{'id': 3}, {'id': 1}], engine)
    expected = [{'id': 1, 'x': 1, 'y': 2},
                {'id': 3, 'x': 4, 'y': 8}]
    equals = records_equal(results, expected)
    assert equals

def test_select_records_by_primary_keys_no_engine(engine_and_table):
    """Test select records by primary keys no engine."""
    _engine, table = engine_and_table
    results = fa.select.select_records_by_primary_keys(table, [{'id': 3}, {'id': 1}])
    expected = [{'id': 1, 'x': 1, 'y': 2},
                {'id': 3, 'x': 4, 'y': 8}]
    equals = records_equal(results, expected)
    assert equals

def test_select_column_values_by_primary_keys(engine_and_table):
    """Test select column values by primary keys."""
    engine, table = engine_and_table
    results = fa.select.select_column_values_by_primary_keys(table, 'y', [{'id': 3}, {'id': 1}], engine)
    expected = [2, 8]
    assert results == expected

def test_select_column_values_by_primary_keys_table_name(engine_and_table):
    """Test select column values by primary keys table name."""
    engine, _table = engine_and_table
    results = fa.select.select_column_values_by_primary_keys('xy', 'y', [{'id': 3}, {'id': 1}], engine)
    expected = [2, 8]
    assert results == expected

def test_select_column_values_by_primary_keys_no_engine(engine_and_table):
    """Test select column values by primary keys no engine."""
    _engine, table = engine_and_table
    results = fa.select.select_column_values_by_primary_keys(table, 'y', [{'id': 3}, {'id': 1}])
    expected = [2, 8]
    assert results == expected

def test_select_value_by_primary_keys(engine_and_table):
    """Test select value by primary keys."""
    engine, table = engine_and_table
    result = fa.select.select_value_by_primary_keys(table, 'y', {'id': 3}, engine)
    expected = 8
    assert result == expected

def test_select_value_by_primary_keys_table_name(engine_and_table):
    """Test select value by primary keys table name."""
    engine, _table = engine_and_table
    result = fa.select.select_value_by_primary_keys('xy', 'y', {'id': 3}, engine)
    expected = 8
    assert result == expected

def test_select_value_by_primary_keys_no_engine(engine_and_table):
    """Test select value by primary keys no engine."""
    _engine, table = engine_and_table
    result = fa.select.select_value_by_primary_keys(table, 'y', {'id': 3})
    expected = 8
    assert result == expected


def test_select_records_all_sorted(engine_and_table):
    """Test select records all with sorted=True."""
    engine, table = engine_and_table
    results = fa.select.select_records_all(table, engine, sorted=True)
    # Should be sorted by primary key (id)
    assert results[0]['id'] == 1
    assert results[-1]['id'] == 4
    assert len(results) == 4


def test_select_records_all_include_columns(engine_and_table):
    """Test select records all with include_columns."""
    engine, table = engine_and_table
    results = fa.select.select_records_all(table, engine, include_columns=['id', 'x'])
    # Should only have id and x columns
    assert all('y' not in r for r in results)
    assert all('id' in r and 'x' in r for r in results)
    assert len(results) == 4


def test_select_records_all_sorted_and_include_columns(engine_and_table):
    """Test select records all with both sorted and include_columns."""
    engine, table = engine_and_table
    results = fa.select.select_records_all(
        table, engine, sorted=True, include_columns=['id', 'y']
    )
    assert results[0] == {'id': 1, 'y': 2}
    assert len(results) == 4


def test_select_records_chunks_sorted(engine_and_table):
    """Test select records chunks with sorted=True."""
    engine, table = engine_and_table
    chunks = list(fa.select.select_records_chunks(table, engine, chunksize=2, sorted=True))
    # Should get 2 chunks
    assert len(chunks) == 2
    # First chunk should have records sorted by id
    assert chunks[0][0]['id'] == 1
    assert chunks[0][1]['id'] == 2


def test_select_records_chunks_include_columns(engine_and_table):
    """Test select records chunks with include_columns."""
    engine, table = engine_and_table
    chunks = list(fa.select.select_records_chunks(
        table, engine, chunksize=2, include_columns=['id', 'x']
    ))
    # All records should only have id and x
    for chunk in chunks:
        for record in chunk:
            assert 'y' not in record
            assert 'id' in record and 'x' in record


def test_select_records_slice_sorted(engine_and_table):
    """Test select records slice with sorted=True."""
    engine, table = engine_and_table
    results = fa.select.select_records_slice(table, 1, 3, engine, sorted=True)
    # Should get records at index 1 and 2 (sorted by primary key)
    assert len(results) == 2
    assert results[0]['id'] == 2
    assert results[1]['id'] == 3


def test_select_records_slice_include_columns(engine_and_table):
    """Test select records slice with include_columns."""
    engine, table = engine_and_table
    results = fa.select.select_records_slice(
        table, 0, 2, engine, include_columns=['id']
    )
    # Should only have id column
    assert all(set(r.keys()) == {'id'} for r in results)
    assert len(results) == 2


def test_select_existing_values_with_filter(engine_and_table):
    """Test select existing values filters non-existent values."""
    _engine, table = engine_and_table
    values_to_check = [1, 2, 5, 10]
    existing = fa.select.select_existing_values(table, 'x', values_to_check)
    # Only 1 and 2 exist in the x column
    assert set(existing) == {1, 2}


def test_select_record_by_primary_key_include_columns(engine_and_table):
    """Test select record by primary key with include_columns."""
    engine, table = engine_and_table
    result = fa.select.select_record_by_primary_key(
        table, {'id': 2}, engine, include_columns=['id', 'x']
    )
    assert result == {'id': 2, 'x': 2}
    assert 'y' not in result


def test_select_primary_key_records_by_slice_sorted(engine_and_table):
    """Test select primary key records by slice with sorted=True."""
    engine, table = engine_and_table
    results = fa.select.select_primary_key_records_by_slice(
        table, slice(0, 2), engine, sorted=True
    )
    # Should get first 2 records sorted by primary key
    assert len(results) == 2
    assert all(set(r.keys()) == {'id'} for r in results)
    assert results[0]['id'] == 1
    assert results[1]['id'] == 2


def test_select_column_value_by_negative_index(engine_and_table):
    """Test select_column_value_by_index with negative index."""
    engine, table = engine_and_table
    # -1 should get last record
    value = fa.select.select_column_value_by_index(table, 'x', -1, engine)
    assert value == 8  # Last x value


def test_select_column_value_by_negative_index_out_of_range(engine_and_table):
    """Test select_column_value_by_index with negative index out of range."""
    engine, table = engine_and_table
    # Table has 4 records, so -5 is out of range
    with pytest.raises(IndexError, match='Index out of range'):
        fa.select.select_column_value_by_index(table, 'x', -5, engine)


def test_select_record_by_negative_index(engine_and_table):
    """Test select_record_by_index with negative index."""
    engine, table = engine_and_table
    # -2 should get second-to-last record
    record = fa.select.select_record_by_index(table, -2, engine)
    assert record == {'id': 3, 'x': 4, 'y': 8}


def test_select_record_by_negative_index_out_of_range(engine_and_table):
    """Test select_record_by_index with negative index out of range."""
    engine, table = engine_and_table
    with pytest.raises(IndexError, match='Index out of range'):
        fa.select.select_record_by_index(table, -10, engine)


def test_select_records_slice_stop_less_than_start(engine_and_table):
    """Test select_records_slice raises SliceError when stop < start."""
    engine, table = engine_and_table
    from fullmetalalchemy.exceptions import SliceError
    with pytest.raises(SliceError, match='stop cannot be less than start'):
        fa.select.select_records_slice(table, 3, 1, engine)  # stop < start


def test_select_column_values_by_slice_negative_indices(engine_and_table):
    """Test select_column_values_by_slice with negative indices."""
    engine, table = engine_and_table
    # -2 to None should get last 2 values
    values = fa.select.select_column_values_by_slice(table, 'x', -2, None, engine)
    assert values == [4, 8]


def test_select_records_by_primary_keys_with_missing_key(engine_and_table):
    """Test select_records_by_primary_keys with non-existent key."""
    engine, table = engine_and_table
    # Request records that don't exist
    records = fa.select.select_records_by_primary_keys(
        table, [{'id': 99}, {'id': 100}], engine
    )
    # Should return empty list
    assert records == []


def test_select_record_by_primary_key_missing_key_error(engine_and_table):
    """Test select_record_by_primary_key raises error for non-existent key."""
    engine, table = engine_and_table
    from fullmetalalchemy.exceptions import MissingPrimaryKeyError
    with pytest.raises(MissingPrimaryKeyError, match='Primary key values missing in table'):
        fa.select.select_record_by_primary_key(table, {'id': 999}, engine)


def test_select_column_values_by_slice_stop_less_than_start(engine_and_table):
    """Test select_column_values_by_slice raises SliceError when stop < start."""
    engine, table = engine_and_table
    from fullmetalalchemy.exceptions import SliceError
    with pytest.raises(SliceError, match='stop cannot be less than start'):
        fa.select.select_column_values_by_slice(table, 'x', 3, 1, engine)


def test_select_primary_key_records_by_slice_stop_less_than_start(engine_and_table):
    """Test select_primary_key_records_by_slice raises SliceError when stop < start."""
    engine, table = engine_and_table
    from fullmetalalchemy.exceptions import SliceError
    with pytest.raises(SliceError, match='stop cannot be less than start'):
        fa.select.select_primary_key_records_by_slice(table, slice(3, 1), engine)




def test_select_value_by_primary_keys_missing_key_error(engine_and_table):
    """Test select_value_by_primary_keys with non-existent key raises error."""
    engine, table = engine_and_table
    # Raises IndexError when no results found
    with pytest.raises(IndexError):
        fa.select.select_value_by_primary_keys(table, 'x', {'id': 999}, engine)


def test_select_record_by_primary_key_with_empty_pk_dict():
    """Test select_record_by_primary_key raises error with empty primary key dict."""
    import sqlalchemy as sa

    from fullmetalalchemy.exceptions import MissingPrimaryKeyError

    engine = sa.create_engine('sqlite://')
    table = fa.create.create_table(
        'test_empty_pk',
        ['id', 'x'],
        [int, int],
        ['id'],
        engine,
        if_exists='replace'
    )

    # Empty primary key value dict should raise error
    with pytest.raises(MissingPrimaryKeyError, match='Primary key values missing'):
        fa.select.select_record_by_primary_key(table, {}, engine)


def test_select_slice_on_empty_table():
    """Test selecting from empty table returns empty list."""
    import sqlalchemy as sa

    engine = sa.create_engine('sqlite://')
    table = fa.create.create_table(
        'empty_table',
        ['id', 'x'],
        [int, int],
        ['id'],
        engine,
        if_exists='replace'
    )

    # Select from empty table should return empty list (tests line 759)
    results = fa.select.select_records_slice(table, 0, 10, engine)
    assert results == []


def test_select_value_by_primary_keys_with_empty_pk_dict():
    """Test select_value_by_primary_keys raises KeyError with empty primary key dict."""
    import sqlalchemy as sa

    engine = sa.create_engine('sqlite://')
    table = fa.create.create_table(
        'test_value_empty_pk',
        ['id', 'x'],
        [int, int],
        ['id'],
        engine,
        if_exists='replace'
    )

    # Empty primary key value dict should raise KeyError (line 704)
    with pytest.raises(KeyError, match='No such primary key values exist'):
        fa.select.select_value_by_primary_keys(table, 'x', {}, engine)


def test_select_records_by_primary_keys_with_empty_list(engine_and_table):
    """Test select_records_by_primary_keys with empty primary key list."""
    engine, table = engine_and_table

    # Empty list should return empty results (line 601-604)
    results = fa.select.select_records_by_primary_keys(table, [], engine)
    assert results == []


def test_select_column_values_by_primary_keys_with_empty_list():
    """Test select_column_values_by_primary_keys with empty list."""
    import sqlalchemy as sa

    engine = sa.create_engine('sqlite://')
    table = fa.create.create_table(
        'test_col_vals_empty',
        ['id', 'x'],
        [int, int],
        ['id'],
        engine,
        if_exists='replace'
    )

    # Empty list should return empty results (line 654)
    results = fa.select.select_column_values_by_primary_keys(table, 'x', [], engine)
    assert results == []


def test_select_records_by_primary_keys_with_include_columns(engine_and_table):
    """Test select_records_by_primary_keys with include_columns parameter."""
    engine, table = engine_and_table

    # Test with include_columns (line 603-604)
    results = fa.select.select_records_by_primary_keys(
        table, [{'id': 1}, {'id': 3}], engine, include_columns=['id', 'x']
    )
    assert len(results) == 2
    assert all('y' not in r for r in results)
    assert all('id' in r and 'x' in r for r in results)


def test_select_records_slice_with_extreme_negative_start(engine_and_table):
    """Test select_records_slice with start index far below -row_count."""
    engine, table = engine_and_table

    # Table has 4 records, -100 is way beyond that (tests line 862)
    results = fa.select.select_records_slice(table, -100, 2, engine)
    # Should get records from beginning to index 2
    assert len(results) == 2
    assert results[0]['id'] == 1
    assert results[1]['id'] == 2


