"""Async batch processing utilities with parallel execution.

This module provides async batch processing with concurrent execution
for improved performance on I/O-bound database operations.
"""

import asyncio
import typing as _t
from dataclasses import dataclass

from fullmetalalchemy.types import Record


@dataclass
class AsyncBatchResult:
    """Result of async batch processing operation.

    Attributes
    ----------
    total_records : int
        Total number of records processed
    total_batches : int
        Number of batches processed
    failed_batches : List[int]
        Indices of batches that failed (if on_error='continue')
    errors : List[Exception]
        Exceptions encountered (if on_error='continue')
    """

    total_records: int
    total_batches: int
    failed_batches: _t.List[int] = None  # type: ignore
    errors: _t.List[Exception] = None  # type: ignore

    def __post_init__(self) -> None:
        if self.failed_batches is None:
            self.failed_batches = []
        if self.errors is None:
            self.errors = []


class AsyncBatchProcessor:
    """Process records in batches asynchronously with parallel execution.

    Parameters
    ----------
    batch_size : int
        Number of records per batch (default 1000)
    max_concurrent : int
        Maximum number of batches to process concurrently (default 5)
    show_progress : bool
        Show progress bar using tqdm if available (default False)
    on_error : str
        Error handling mode: 'raise' or 'continue' (default 'raise')

    Examples
    --------
    >>> import asyncio
    >>> from fullmetalalchemy.async_api import AsyncBatchProcessor
    >>>
    >>> async def main():
    ...     processor = AsyncBatchProcessor(batch_size=500, max_concurrent=3)
    ...     result = await processor.process_batches(
    ...         records,
    ...         lambda batch: insert_records(table, batch, engine)
    ...     )
    ...     print(f"Processed {result.total_records} in {result.total_batches} batches")
    >>> asyncio.run(main())
    """

    def __init__(
        self,
        batch_size: int = 1000,
        max_concurrent: int = 5,
        show_progress: bool = False,
        on_error: str = "raise",
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")
        if max_concurrent < 1:
            raise ValueError("max_concurrent must be at least 1")
        if on_error not in ("raise", "continue"):
            raise ValueError("on_error must be 'raise' or 'continue'")

        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.show_progress = show_progress
        self.on_error = on_error

    def chunk_records(self, records: _t.Sequence[Record]) -> _t.List[_t.Sequence[Record]]:
        """Split records into chunks of batch_size.

        Parameters
        ----------
        records : Sequence[Record]
            Records to chunk

        Returns
        -------
        List[Sequence[Record]]
            List of batches
        """
        batches = []
        for i in range(0, len(records), self.batch_size):
            batches.append(records[i : i + self.batch_size])
        return batches

    async def process_batches(
        self,
        records: _t.Sequence[Record],
        operation: _t.Callable[[_t.Sequence[Record]], _t.Coroutine[_t.Any, _t.Any, None]],
    ) -> AsyncBatchResult:
        """Process records in batches with parallel execution.

        Parameters
        ----------
        records : Sequence[Record]
            Records to process
        operation : Callable[[Sequence[Record]], Coroutine]
            Async function to apply to each batch

        Returns
        -------
        AsyncBatchResult
            Result object with processing statistics

        Examples
        --------
        >>> async def insert_batch(batch):
        ...     await insert_records(table, batch, engine)
        >>>
        >>> processor = AsyncBatchProcessor(batch_size=100, max_concurrent=5)
        >>> result = await processor.process_batches(large_dataset, insert_batch)
        >>> print(f"Processed {result.total_batches} batches")
        """
        batches = self.chunk_records(records)
        total_batches = len(batches)
        failed_batches: _t.List[int] = []
        errors: _t.List[Exception] = []

        # Create semaphore to limit concurrent operations
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def process_with_semaphore(batch_idx: int, batch: _t.Sequence[Record]) -> None:
            """Process single batch with semaphore control."""
            async with semaphore:
                try:
                    await operation(batch)
                except Exception as e:
                    if self.on_error == "raise":
                        raise
                    else:
                        failed_batches.append(batch_idx)
                        errors.append(e)

        # Process all batches concurrently (limited by semaphore)
        tasks = [process_with_semaphore(idx, batch) for idx, batch in enumerate(batches)]

        # Use tqdm if available and requested
        if self.show_progress:
            try:
                from tqdm.asyncio import tqdm  # type: ignore[import-untyped]

                await tqdm.gather(*tasks, desc="Processing batches", unit="batch")
            except ImportError:
                # tqdm not available, use plain gather
                await asyncio.gather(*tasks, return_exceptions=(self.on_error == "continue"))
        else:
            await asyncio.gather(*tasks, return_exceptions=(self.on_error == "continue"))

        return AsyncBatchResult(
            total_records=len(records),
            total_batches=total_batches,
            failed_batches=failed_batches,
            errors=errors,
        )

    async def process_batches_sequential(
        self,
        records: _t.Sequence[Record],
        operation: _t.Callable[[_t.Sequence[Record]], _t.Coroutine[_t.Any, _t.Any, None]],
    ) -> AsyncBatchResult:
        """Process records in batches sequentially (no parallelism).

        Useful when order matters or database doesn't support concurrent writes.

        Parameters
        ----------
        records : Sequence[Record]
            Records to process
        operation : Callable[[Sequence[Record]], Coroutine]
            Async function to apply to each batch

        Returns
        -------
        AsyncBatchResult
            Result object with processing statistics
        """
        batches = self.chunk_records(records)
        total_batches = len(batches)
        failed_batches: _t.List[int] = []
        errors: _t.List[Exception] = []

        # Try to import tqdm for progress bar
        iterator: _t.Any = enumerate(batches)
        if self.show_progress:
            try:
                from tqdm import tqdm  # type: ignore[import-untyped]

                iterator = tqdm(
                    enumerate(batches), total=total_batches, desc="Processing", unit="batch"
                )
            except ImportError:
                pass

        for batch_idx, batch in iterator:
            try:
                await operation(batch)
            except Exception as e:
                if self.on_error == "raise":
                    raise
                else:
                    failed_batches.append(batch_idx)
                    errors.append(e)

        return AsyncBatchResult(
            total_records=len(records),
            total_batches=total_batches,
            failed_batches=failed_batches,
            errors=errors,
        )
