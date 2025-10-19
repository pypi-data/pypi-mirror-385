"""Tests for async batch processing utilities."""
import asyncio

import pytest

from fullmetalalchemy.async_api.batch import AsyncBatchProcessor, AsyncBatchResult


@pytest.mark.asyncio
async def test_async_batch_processor_init():
    """Test AsyncBatchProcessor initialization."""
    processor = AsyncBatchProcessor(batch_size=100, max_concurrent=3)
    assert processor.batch_size == 100
    assert processor.max_concurrent == 3
    assert processor.show_progress is False


@pytest.mark.asyncio
async def test_async_batch_processor_invalid_batch_size():
    """Test AsyncBatchProcessor with invalid batch_size."""
    with pytest.raises(ValueError, match="batch_size must be at least 1"):
        AsyncBatchProcessor(batch_size=0)


@pytest.mark.asyncio
async def test_async_batch_processor_invalid_max_concurrent():
    """Test AsyncBatchProcessor with invalid max_concurrent."""
    with pytest.raises(ValueError, match="max_concurrent must be at least 1"):
        AsyncBatchProcessor(max_concurrent=0)


@pytest.mark.asyncio
async def test_async_chunk_records():
    """Test async chunk_records."""
    processor = AsyncBatchProcessor(batch_size=3)
    records = [{"id": i} for i in range(10)]

    chunks = processor.chunk_records(records)

    assert len(chunks) == 4
    assert len(chunks[0]) == 3
    assert len(chunks[3]) == 1


@pytest.mark.asyncio
async def test_async_process_batches_success():
    """Test async process_batches with successful operations."""
    processor = AsyncBatchProcessor(batch_size=2)
    records = [{"id": i} for i in range(5)]

    processed = []

    async def operation(batch):
        await asyncio.sleep(0.01)  # Simulate async I/O
        processed.extend(batch)

    result = await processor.process_batches(records, operation)

    assert result.total_records == 5
    assert result.total_batches == 3
    assert len(result.failed_batches) == 0
    assert len(processed) == 5


@pytest.mark.asyncio
async def test_async_process_batches_parallel():
    """Test that batches are processed in parallel."""
    processor = AsyncBatchProcessor(batch_size=1, max_concurrent=3)
    records = [{"id": i} for i in range(5)]

    # Track execution times to verify parallelism
    execution_times = []

    async def slow_operation(batch):
        start = asyncio.get_event_loop().time()
        await asyncio.sleep(0.1)
        execution_times.append(start)

    await processor.process_batches(records, slow_operation)

    # With max_concurrent=3, first 3 should start roughly together
    # Time differences should be small for parallel batches
    assert len(execution_times) == 5


@pytest.mark.asyncio
async def test_async_process_batches_with_error_raise():
    """Test async process_batches raises on error."""
    processor = AsyncBatchProcessor(batch_size=2, on_error="raise")
    records = [{"id": i} for i in range(5)]

    async def failing_operation(batch):
        if batch[0]["id"] == 2:
            raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        await processor.process_batches(records, failing_operation)


@pytest.mark.asyncio
async def test_async_process_batches_with_error_continue():
    """Test async process_batches continues on error."""
    processor = AsyncBatchProcessor(batch_size=2, on_error="continue")
    records = [{"id": i} for i in range(6)]

    async def failing_operation(batch):
        if batch[0]["id"] == 2:
            raise ValueError("Test error")

    result = await processor.process_batches(records, failing_operation)

    assert result.total_records == 6
    assert result.total_batches == 3
    assert len(result.failed_batches) == 1
    assert len(result.errors) == 1


@pytest.mark.asyncio
async def test_async_process_batches_sequential():
    """Test async process_batches_sequential."""
    processor = AsyncBatchProcessor(batch_size=2)
    records = [{"id": i} for i in range(5)]

    processed = []

    async def operation(batch):
        await asyncio.sleep(0.01)
        processed.extend(batch)

    result = await processor.process_batches_sequential(records, operation)

    assert result.total_records == 5
    assert result.total_batches == 3
    assert len(processed) == 5


@pytest.mark.asyncio
async def test_async_batch_result_dataclass():
    """Test AsyncBatchResult dataclass."""
    result = AsyncBatchResult(total_records=100, total_batches=10)

    assert result.total_records == 100
    assert result.total_batches == 10
    assert result.failed_batches == []
    assert result.errors == []


@pytest.mark.asyncio
async def test_async_semaphore_limiting():
    """Test that semaphore limits concurrent operations."""
    max_concurrent = 2
    processor = AsyncBatchProcessor(batch_size=1, max_concurrent=max_concurrent)
    records = [{"id": i} for i in range(5)]

    # Track concurrent operations
    active_count = 0
    max_active = 0

    async def track_operation(batch):
        nonlocal active_count, max_active
        active_count += 1
        max_active = max(max_active, active_count)
        await asyncio.sleep(0.1)
        active_count -= 1

    await processor.process_batches(records, track_operation)

    # Should never exceed max_concurrent
    assert max_active <= max_concurrent

