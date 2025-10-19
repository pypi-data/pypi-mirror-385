"""Batch processing utilities for efficient bulk operations.

This module provides utilities for processing large datasets in configurable batches
with optional progress tracking.
"""
import typing as _t
from dataclasses import dataclass

from fullmetalalchemy.types import Record


@dataclass
class BatchResult:
    """Result of batch processing operation.

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


class BatchProcessor:
    """Process records in batches with optional progress tracking.

    Parameters
    ----------
    batch_size : int
        Number of records per batch (default 1000)
    show_progress : bool
        Show progress bar using tqdm if available (default False)
    on_error : str
        Error handling mode: 'raise' or 'continue' (default 'raise')

    Examples
    --------
    >>> from fullmetalalchemy import BatchProcessor
    >>>
    >>> processor = BatchProcessor(batch_size=500, show_progress=True)
    >>> result = processor.process_batches(
    ...     records,
    ...     lambda batch: insert_records(table, batch, engine)
    ... )
    >>> print(f"Processed {result.total_records} records in {result.total_batches} batches")
    """

    def __init__(
        self,
        batch_size: int = 1000,
        show_progress: bool = False,
        on_error: str = "raise",
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")
        if on_error not in ("raise", "continue"):
            raise ValueError("on_error must be 'raise' or 'continue'")

        self.batch_size = batch_size
        self.show_progress = show_progress
        self.on_error = on_error

    def chunk_records(self, records: _t.Sequence[Record]) -> _t.Iterator[_t.Sequence[Record]]:
        """Split records into chunks of batch_size.

        Parameters
        ----------
        records : Sequence[Record]
            Records to chunk

        Yields
        ------
        Sequence[Record]
            Batches of records
        """
        for i in range(0, len(records), self.batch_size):
            yield records[i : i + self.batch_size]

    def process_batches(
        self, records: _t.Sequence[Record], operation: _t.Callable[[_t.Sequence[Record]], None]
    ) -> BatchResult:
        """Process records in batches.

        Parameters
        ----------
        records : Sequence[Record]
            Records to process
        operation : Callable[[Sequence[Record]], None]
            Function to apply to each batch

        Returns
        -------
        BatchResult
            Result object with processing statistics

        Examples
        --------
        >>> processor = BatchProcessor(batch_size=100)
        >>> result = processor.process_batches(
        ...     records,
        ...     lambda batch: insert_records(table, batch, engine)
        ... )
        """
        batches = list(self.chunk_records(records))
        total_batches = len(batches)
        failed_batches: _t.List[int] = []
        errors: _t.List[Exception] = []

        # Try to import tqdm for progress bar
        iterator: _t.Any = batches
        if self.show_progress:
            try:
                from tqdm import tqdm  # type: ignore[import-untyped]

                iterator = tqdm(batches, desc="Processing batches", unit="batch")
            except ImportError:
                # tqdm not available, use plain iterator
                pass

        for batch_idx, batch in enumerate(iterator):
            try:
                operation(batch)
            except Exception as e:
                if self.on_error == "raise":
                    raise
                else:
                    failed_batches.append(batch_idx)
                    errors.append(e)

        return BatchResult(
            total_records=len(records),
            total_batches=total_batches,
            failed_batches=failed_batches,
            errors=errors,
        )


def chunk_sequence(
    sequence: _t.Sequence[_t.Any], chunk_size: int
) -> _t.Iterator[_t.Sequence[_t.Any]]:
    """Split a sequence into chunks of specified size.

    Parameters
    ----------
    sequence : Sequence[Any]
        Sequence to chunk
    chunk_size : int
        Size of each chunk

    Yields
    ------
    Sequence[Any]
        Chunks of the sequence

    Examples
    --------
    >>> list(chunk_sequence([1, 2, 3, 4, 5], 2))
    [[1, 2], [3, 4], [5]]
    """
    for i in range(0, len(sequence), chunk_size):
        yield sequence[i : i + chunk_size]

