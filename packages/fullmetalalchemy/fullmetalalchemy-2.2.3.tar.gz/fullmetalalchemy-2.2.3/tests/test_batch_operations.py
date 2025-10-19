"""Tests for batch processing utilities."""

import pytest

from fullmetalalchemy import BatchProcessor, BatchResult

# Sync BatchProcessor Tests


def test_batch_processor_init():
    """Test BatchProcessor initialization."""
    processor = BatchProcessor(batch_size=100, show_progress=False)
    assert processor.batch_size == 100
    assert processor.show_progress is False
    assert processor.on_error == "raise"


def test_batch_processor_invalid_batch_size():
    """Test BatchProcessor with invalid batch_size."""
    with pytest.raises(ValueError, match="batch_size must be at least 1"):
        BatchProcessor(batch_size=0)


def test_batch_processor_invalid_on_error():
    """Test BatchProcessor with invalid on_error."""
    with pytest.raises(ValueError, match="on_error must be 'raise' or 'continue'"):
        BatchProcessor(on_error="invalid")


def test_chunk_records_basic():
    """Test chunk_records splits records correctly."""
    processor = BatchProcessor(batch_size=3)
    records = [{"id": i, "val": i * 2} for i in range(10)]

    chunks = list(processor.chunk_records(records))

    assert len(chunks) == 4  # 10 records / 3 per batch = 4 batches
    assert len(chunks[0]) == 3
    assert len(chunks[1]) == 3
    assert len(chunks[2]) == 3
    assert len(chunks[3]) == 1  # Last batch has remainder


def test_chunk_records_exact_division():
    """Test chunk_records with exact division."""
    processor = BatchProcessor(batch_size=5)
    records = [{"id": i} for i in range(15)]

    chunks = list(processor.chunk_records(records))

    assert len(chunks) == 3  # 15 / 5 = 3 exactly
    assert all(len(chunk) == 5 for chunk in chunks)


def test_process_batches_success():
    """Test process_batches with successful operations."""
    processor = BatchProcessor(batch_size=2)
    records = [{"id": i, "val": i * 2} for i in range(5)]

    processed = []

    def operation(batch):
        processed.extend(batch)

    result = processor.process_batches(records, operation)

    assert result.total_records == 5
    assert result.total_batches == 3  # 5 records / 2 per batch
    assert len(result.failed_batches) == 0
    assert len(result.errors) == 0
    assert len(processed) == 5


def test_process_batches_with_error_raise():
    """Test process_batches raises on error."""
    processor = BatchProcessor(batch_size=2, on_error="raise")
    records = [{"id": i} for i in range(5)]

    def failing_operation(batch):
        if batch[0]["id"] == 2:
            raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        processor.process_batches(records, failing_operation)


def test_process_batches_with_error_continue():
    """Test process_batches continues on error."""
    processor = BatchProcessor(batch_size=2, on_error="continue")
    records = [{"id": i} for i in range(6)]

    def failing_operation(batch):
        if batch[0]["id"] == 2:
            raise ValueError("Test error on batch")
        # Simulate successful processing
        pass

    result = processor.process_batches(records, failing_operation)

    assert result.total_records == 6
    assert result.total_batches == 3
    assert len(result.failed_batches) == 1  # One batch failed
    assert 1 in result.failed_batches  # Batch index 1 (records 2-3)
    assert len(result.errors) == 1
    assert isinstance(result.errors[0], ValueError)


def test_batch_result_dataclass():
    """Test BatchResult dataclass."""
    result = BatchResult(total_records=100, total_batches=10)

    assert result.total_records == 100
    assert result.total_batches == 10
    assert result.failed_batches == []
    assert result.errors == []


def test_batch_result_with_errors():
    """Test BatchResult with errors."""
    result = BatchResult(
        total_records=100,
        total_batches=10,
        failed_batches=[2, 5],
        errors=[ValueError("err1"), RuntimeError("err2")],
    )

    assert len(result.failed_batches) == 2
    assert len(result.errors) == 2


# Integration with real operations


def test_batch_processor_with_accumulator():
    """Test batch processor collecting results."""
    processor = BatchProcessor(batch_size=3)
    records = [{"id": i, "value": i * 10} for i in range(10)]

    # Track which batches were processed
    processed_batches = []

    def track_operation(batch):
        processed_batches.append(len(batch))

    result = processor.process_batches(records, track_operation)

    assert result.total_records == 10
    assert result.total_batches == 4
    assert processed_batches == [3, 3, 3, 1]


def test_chunk_sequence_helper():
    """Test chunk_sequence helper function."""
    from fullmetalalchemy.batch import chunk_sequence

    items = list(range(10))
    chunks = list(chunk_sequence(items, 3))

    assert len(chunks) == 4
    assert chunks[0] == [0, 1, 2]
    assert chunks[1] == [3, 4, 5]
    assert chunks[2] == [6, 7, 8]
    assert chunks[3] == [9]
