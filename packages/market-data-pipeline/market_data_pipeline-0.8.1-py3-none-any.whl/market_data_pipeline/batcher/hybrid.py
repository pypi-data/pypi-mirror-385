"""Hybrid batcher with size, bytes, and time thresholds."""

from __future__ import annotations

import asyncio
import time
from collections import deque
from typing import List, Optional

from ..batcher.base import Batcher
from ..errors import BatcherError
from ..types import Bar


class HybridBatcher(Batcher):
    """Hybrid batcher that flushes based on size, bytes, or time thresholds."""

    def __init__(
        self,
        max_rows: int = 500,
        max_bytes: int = 512_000,
        flush_ms: int = 100,
        op_queue_max: int = 8,
        drop_policy: str = "oldest",
    ) -> None:
        """Initialize the hybrid batcher."""
        self.max_rows = max_rows
        self.max_bytes = max_bytes
        self.flush_ms = flush_ms
        self.op_queue_max = op_queue_max
        self.drop_policy = drop_policy

        # Internal state
        self._queue: deque[Bar] = deque()
        self._current_bytes = 0
        self._last_flush_time = time.time()
        self._lock = asyncio.Lock()

        # Metrics
        self._items_added = 0
        self._items_dropped = 0
        self._batches_flushed = 0

    async def add(self, item: Bar) -> Optional[List[Bar]]:
        """Add an item to the batch. Returns a batch if ready to flush."""
        async with self._lock:
            # Check if we need to drop items due to queue limits
            if len(self._queue) >= self.op_queue_max:
                if self.drop_policy == "oldest":
                    # Drop oldest item
                    dropped = self._queue.popleft()
                    self._current_bytes -= self._estimate_size(dropped)
                    self._items_dropped += 1
                elif self.drop_policy == "newest":
                    # Drop newest item (current item)
                    self._items_dropped += 1
                    return None
                else:
                    raise BatcherError(f"Invalid drop policy: {self.drop_policy}")

            # Add item to queue
            self._queue.append(item)
            self._current_bytes += self._estimate_size(item)
            self._items_added += 1

            # Check if we should flush
            should_flush = (
                len(self._queue) >= self.max_rows
                or self._current_bytes >= self.max_bytes
                or self._should_flush_by_time()
            )

            if should_flush:
                return await self._flush_internal()

        return None

    async def flush(self) -> Optional[List[Bar]]:
        """Force flush any remaining items in the batch."""
        async with self._lock:
            if not self._queue:
                return None
            return await self._flush_internal()

    async def _flush_internal(self) -> List[Bar]:
        """Internal flush method (must be called with lock held)."""
        if not self._queue:
            return []

        # Create batch from queue
        batch = list(self._queue)

        # Clear queue
        self._queue.clear()
        self._current_bytes = 0
        self._last_flush_time = time.time()
        self._batches_flushed += 1

        return batch

    def _should_flush_by_time(self) -> bool:
        """Check if we should flush based on time threshold."""
        current_time = time.time()
        return (current_time - self._last_flush_time) * 1000 >= self.flush_ms

    def _estimate_size(self, bar: Bar) -> int:
        """Estimate the size of a bar in bytes."""
        # Rough estimation based on field sizes
        size = 0
        size += len(bar.symbol) * 2  # Unicode chars
        size += 8  # timestamp
        size += 8 * 4  # OHLC (Decimal)
        size += 8  # volume (Decimal)
        size += 8 if bar.vwap else 0  # VWAP (Decimal)
        size += 4 if bar.trade_count else 0  # trade_count (int)
        size += len(bar.source) * 2  # source string
        size += 100  # metadata overhead
        return size

    def get_metrics(self) -> dict:
        """Get batcher metrics."""
        return {
            "queue_depth": len(self._queue),
            "current_bytes": self._current_bytes,
            "items_added": self._items_added,
            "items_dropped": self._items_dropped,
            "batches_flushed": self._batches_flushed,
        }
