"""Store sink for persisting data to market_data_store."""

from __future__ import annotations

import asyncio
import math
import time
from datetime import datetime, timezone
from typing import List, Optional

from ..context import PipelineContext
from ..errors import SinkError
from ..sink.base import Sink
from ..sink.capabilities import SinkCapabilities, SinkHealth
from ..sink.telemetry import get_sink_telemetry
from ..types import Bar


class StoreSink(Sink):
    """Sink that writes batches to market_data_store via AsyncBatchProcessor.

    Features:
    - Deterministic lifecycle with start/flush/drain
    - Configurable backpressure policy (block/drop_oldest/drop_newest)
    - Retry logic with exponential backoff for transient errors
    - Comprehensive telemetry and metrics
    """

    def __init__(
        self,
        batch_processor: "AsyncBatchProcessor",
        workers: int = 2,
        queue_max: int = 100,
        backpressure_policy: str = "block",
        ctx: Optional[PipelineContext] = None,
    ) -> None:
        """Initialize the store sink."""
        self.batch_processor = batch_processor
        self.workers = max(1, workers)
        self.queue_max = max(1, queue_max)
        self.backpressure_policy = (
            backpressure_policy  # "block" | "drop_oldest" | "drop_newest"
        )
        self.ctx = ctx
        self._queue: Optional[asyncio.Queue[List[Bar]]] = None
        self._workers: List[asyncio.Task] = []
        self._closed = False
        self._started = False

        # Telemetry
        self.telemetry = get_sink_telemetry()
        self._last_commit_at: Optional[datetime] = None
        self._last_error_at: Optional[datetime] = None
        self._retry_count = 0

    async def write(self, batch: List[Bar]) -> None:
        """Write a batch of bars to the store."""
        if self._closed:
            raise SinkError("Sink is closed")

        if not batch:
            return

        # Initialize worker pool if not already done
        if not self._started:
            await self.start()

        # Record batch accepted
        self._record_batch_in()

        # Apply backpressure policy
        await self._apply_backpressure(batch)

    async def start(self) -> None:
        """Initialize worker pool and queue."""
        if self._started:
            return

        self._queue = asyncio.Queue(maxsize=self.queue_max)
        for i in range(self.workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)
        self._started = True

    async def flush(self) -> None:
        """Force a commit of queued work without closing."""
        if self._queue is None:
            return

        # Wait until queue drains
        while not self._queue.empty():
            await asyncio.sleep(0.01)

    async def close(self, drain: bool = True) -> None:
        """Close the sink and wait for all workers to finish."""
        if self._closed:
            return

        self._closed = True

        if self._queue and drain:
            # Send sentinel pills to workers for graceful shutdown
            for _ in range(self.workers):
                await self._queue.put(None)  # type: ignore[arg-type]

        # Wait for workers to finish
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)

        # Close the batch processor
        if hasattr(self.batch_processor, "close"):
            await self.batch_processor.close()

    @property
    def capabilities(self) -> SinkCapabilities:
        """Get sink capabilities."""
        return SinkCapabilities.BATCH_WRITES

    async def health(self) -> SinkHealth:
        """Get machine-parsable health information."""
        queue_depth = 0
        if self._queue:
            queue_depth = self._queue.qsize()

        return SinkHealth(
            connected=self._started and not self._closed,
            queue_depth=queue_depth,
            in_flight_batches=len(self._workers),
            last_commit_at=self._last_commit_at,
            last_error_at=self._last_error_at,
            retry_count=self._retry_count,
            detail=f"StoreSink with {self.workers} workers, queue_max={self.queue_max}",
        )

    async def _apply_backpressure(self, batch: List[Bar]) -> None:
        """Apply backpressure policy to batch."""
        if self._queue is None:
            return

        if self.backpressure_policy == "block":
            await self._queue.put(batch)
        else:
            try:
                self._queue.put_nowait(batch)
            except asyncio.QueueFull:
                if self.backpressure_policy == "drop_oldest":
                    try:
                        self._queue.get_nowait()  # Drop one
                    except asyncio.QueueEmpty:
                        pass
                    self._queue.put_nowait(batch)
                else:  # drop_newest
                    self._record_dropped_batch("queue_full")
                    return

    def _record_batch_in(self) -> None:
        """Record batch accepted by write()."""
        tenant_id = self.ctx.tenant_id if self.ctx else "unknown"
        pipeline_id = self.ctx.pipeline_id if self.ctx else "unknown"
        self.telemetry.record_batch_in("store", tenant_id, pipeline_id)

    def _record_dropped_batch(self, reason: str) -> None:
        """Record a dropped batch."""
        tenant_id = self.ctx.tenant_id if self.ctx else "unknown"
        pipeline_id = self.ctx.pipeline_id if self.ctx else "unknown"
        self.telemetry.record_dropped_batch("store", tenant_id, pipeline_id, reason)

    async def _worker(self, worker_id: str) -> None:
        """Worker task that processes batches."""
        if self._queue is None:
            return

        while True:
            try:
                # Get batch from queue
                batch = await self._queue.get()

                # Check for sentinel (shutdown signal)
                if batch is None:
                    return

                # Process batch with retry logic
                await self._process_with_retry(batch, worker_id)

            except asyncio.CancelledError:
                # Worker was cancelled
                return
            except Exception as e:
                # Log error and continue
                self._last_error_at = datetime.now(timezone.utc)
                print(f"Worker {worker_id} error: {e}")

    async def _process_with_retry(self, batch: List[Bar], worker_id: str) -> None:
        """Process batch with retry logic for transient errors."""
        max_attempts = 5
        delay = 0.05
        attempt = 0
        start = time.perf_counter()

        while True:
            try:
                await self._process_batch(batch, worker_id)

                # Record successful commit
                self._record_batch_committed(len(batch))
                self._last_commit_at = datetime.now(timezone.utc)

                # Record commit duration
                duration = time.perf_counter() - start
                self._record_commit_duration(duration)

                return

            except Exception as e:
                # Check if this is a transient error
                if self._is_transient_error(e) and attempt < max_attempts:
                    attempt += 1
                    self._retry_count += 1
                    self._record_retry()

                    # Exponential backoff with jitter
                    await asyncio.sleep(delay)
                    delay *= 2  # Backoff
                else:
                    # Fatal error or max attempts reached
                    self._record_batch_failed()
                    self._last_error_at = datetime.now(timezone.utc)
                    raise

    def _is_transient_error(self, error: Exception) -> bool:
        """Check if error is transient and should be retried."""
        # TODO: Map from market_data_store error taxonomy
        # For now, assume all errors are transient
        return True

    async def _process_batch(self, batch: List[Bar], worker_id: str) -> None:
        """Process a batch of bars."""
        # Convert bars to the format expected by AsyncBatchProcessor
        records = []
        for bar in batch:
            record = self._to_store_record(bar)
            records.append(record)

        # Write to batch processor
        # Handle both sync and async upsert_bars methods
        if asyncio.iscoroutinefunction(self.batch_processor.upsert_bars):
            # Async method - await directly
            await self.batch_processor.upsert_bars(records)
        else:
            # Sync method - run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.batch_processor.upsert_bars, records)

    def _to_store_record(self, bar: Bar) -> dict:
        """Convert a Bar to store record format."""
        record = {
            "symbol": bar.symbol,
            "timestamp": bar.timestamp,
            "open": float(bar.open),
            "high": float(bar.high),
            "low": float(bar.low),
            "close": float(bar.close),
            "volume": float(bar.volume),
            "source": bar.source,
        }

        # Add optional fields
        if bar.vwap is not None:
            record["vwap"] = float(bar.vwap)
        if bar.trade_count is not None:
            record["trade_count"] = bar.trade_count
        if bar.metadata:
            record["metadata"] = bar.metadata

        # Add idempotency key if context is available
        if self.ctx:
            window_ts = bar.timestamp.strftime("%Y%m%d%H%M%S")
            record["idempotency_key"] = self.ctx.get_idempotency_key(
                bar.symbol, window_ts
            )

        return record

    def _record_batch_committed(self, items: int) -> None:
        """Record successful batch commit."""
        tenant_id = self.ctx.tenant_id if self.ctx else "unknown"
        pipeline_id = self.ctx.pipeline_id if self.ctx else "unknown"
        self.telemetry.record_batch_committed("store", tenant_id, pipeline_id, items)

    def _record_batch_failed(self) -> None:
        """Record failed batch commit."""
        tenant_id = self.ctx.tenant_id if self.ctx else "unknown"
        pipeline_id = self.ctx.pipeline_id if self.ctx else "unknown"
        self.telemetry.record_batch_failed("store", tenant_id, pipeline_id)

    def _record_retry(self) -> None:
        """Record retry attempt."""
        tenant_id = self.ctx.tenant_id if self.ctx else "unknown"
        pipeline_id = self.ctx.pipeline_id if self.ctx else "unknown"
        self.telemetry.record_retry("store", tenant_id, pipeline_id)

    def _record_commit_duration(self, duration: float) -> None:
        """Record commit duration."""
        tenant_id = self.ctx.tenant_id if self.ctx else "unknown"
        pipeline_id = self.ctx.pipeline_id if self.ctx else "unknown"
        self.telemetry.record_commit_duration("store", tenant_id, pipeline_id, duration)

    def get_metrics(self) -> dict:
        """Get sink metrics."""
        return {
            "batches_written": self._batches_written,
            "items_written": self._items_written,
            "write_errors": self._write_errors,
            "workers": len(self._workers),
        }
