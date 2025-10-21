"""Kafka sink for streaming data to Kafka topics."""

from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import List, Optional

from ..context import PipelineContext
from ..errors import SinkError
from ..sink.base import Sink
from ..sink.capabilities import SinkCapabilities, SinkHealth
from ..sink.telemetry import get_sink_telemetry
from ..types import Bar

# Import aiokafka when available
try:
    from aiokafka import AIOKafkaProducer
except ImportError:
    AIOKafkaProducer = None


class KafkaSink(Sink):
    """Sink that writes batches to Kafka topics.

    Features:
    - aiokafka producer with idempotent writes
    - Configurable backpressure policy
    - Partitioning by symbol for ordering
    - Comprehensive telemetry and metrics
    """

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        queue_max: int = 500,
        backpressure_policy: str = "block",
        ctx: Optional[PipelineContext] = None,
    ) -> None:
        """Initialize the Kafka sink."""
        if AIOKafkaProducer is None:
            raise ImportError(
                "aiokafka is required for KafkaSink. Install with: pip install aiokafka"
            )

        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.queue_max = queue_max
        self.backpressure_policy = backpressure_policy
        self.ctx = ctx
        self._producer: Optional[AIOKafkaProducer] = None
        self._queue: Optional[asyncio.Queue[List[Bar]]] = None
        self._worker: Optional[asyncio.Task] = None
        self._closed = False
        self._started = False

        # Telemetry
        self.telemetry = get_sink_telemetry()
        self._last_commit_at: Optional[datetime] = None
        self._last_error_at: Optional[datetime] = None
        self._retry_count = 0

    async def start(self) -> None:
        """Initialize Kafka producer and worker."""
        if self._started:
            return

        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            linger_ms=50,
            acks="all",
            enable_idempotence=True,
            compression_type="gzip",
        )
        await self._producer.start()

        self._queue = asyncio.Queue(maxsize=self.queue_max)
        self._worker = asyncio.create_task(self._pump())
        self._started = True

    async def write(self, batch: List[Bar]) -> None:
        """Write a batch of bars to Kafka."""
        if self._closed:
            raise SinkError("Sink is closed")

        if not batch:
            return

        if not self._started:
            await self.start()

        # Record batch accepted
        self._record_batch_in()

        # Apply backpressure policy
        await self._apply_backpressure(batch)

    async def flush(self) -> None:
        """Force a commit of queued work without closing."""
        if self._queue is None:
            return

        # Wait until queue drains
        while not self._queue.empty():
            await asyncio.sleep(0.01)

    async def close(self, drain: bool = True) -> None:
        """Close the Kafka sink."""
        if self._closed:
            return

        self._closed = True

        if self._queue and drain:
            # Send sentinel to worker for graceful shutdown
            await self._queue.put(None)  # type: ignore[arg-type]
            if self._worker:
                await self._worker

        if self._producer:
            await self._producer.stop()

    @property
    def capabilities(self) -> SinkCapabilities:
        """Get sink capabilities."""
        return SinkCapabilities.BATCH_WRITES | SinkCapabilities.EXACTLY_ONCE

    async def health(self) -> SinkHealth:
        """Get machine-parsable health information."""
        queue_depth = 0
        if self._queue:
            queue_depth = self._queue.qsize()

        return SinkHealth(
            connected=self._started and not self._closed,
            queue_depth=queue_depth,
            in_flight_batches=1 if self._worker and not self._worker.done() else 0,
            last_commit_at=self._last_commit_at,
            last_error_at=self._last_error_at,
            retry_count=self._retry_count,
            detail=f"KafkaSink to {self.topic} via {self.bootstrap_servers}",
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

    async def _pump(self) -> None:
        """Worker task that pumps batches to Kafka."""
        if self._producer is None or self._queue is None:
            return

        producer = self._producer

        while True:
            try:
                batch = await self._queue.get()

                # Check for sentinel (shutdown signal)
                if batch is None:
                    return

                # Process batch with retry logic
                await self._process_with_retry(batch)

            except asyncio.CancelledError:
                return
            except Exception as e:
                self._last_error_at = datetime.now(timezone.utc)
                print(f"KafkaSink pump error: {e}")

    async def _process_with_retry(self, batch: List[Bar]) -> None:
        """Process batch with retry logic for transient errors."""
        max_attempts = 5
        delay = 0.05
        attempt = 0
        start = time.perf_counter()

        while True:
            try:
                await self._process_batch(batch)

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
        # TODO: Map from Kafka error taxonomy
        # For now, assume all errors are transient
        return True

    async def _process_batch(self, batch: List[Bar]) -> None:
        """Process a batch of bars to Kafka."""
        if self._producer is None:
            return

        # Send each bar as a separate message for ordering
        for bar in batch:
            key = bar.symbol.encode()
            value = json.dumps(self._bar_to_dict(bar)).encode()

            await self._producer.send_and_wait(self.topic, value=value, key=key)

    def _bar_to_dict(self, bar: Bar) -> dict:
        """Convert a Bar to dictionary for JSON serialization."""
        return {
            "symbol": bar.symbol,
            "timestamp": bar.timestamp.isoformat(),
            "open": float(bar.open),
            "high": float(bar.high),
            "low": float(bar.low),
            "close": float(bar.close),
            "volume": float(bar.volume),
            "source": bar.source,
            "vwap": float(bar.vwap) if bar.vwap else None,
            "trade_count": bar.trade_count,
            "metadata": bar.metadata,
        }

    def _record_batch_in(self) -> None:
        """Record batch accepted by write()."""
        tenant_id = self.ctx.tenant_id if self.ctx else "unknown"
        pipeline_id = self.ctx.pipeline_id if self.ctx else "unknown"
        self.telemetry.record_batch_in("kafka", tenant_id, pipeline_id)

    def _record_batch_committed(self, items: int) -> None:
        """Record successful batch commit."""
        tenant_id = self.ctx.tenant_id if self.ctx else "unknown"
        pipeline_id = self.ctx.pipeline_id if self.ctx else "unknown"
        self.telemetry.record_batch_committed("kafka", tenant_id, pipeline_id, items)

    def _record_batch_failed(self) -> None:
        """Record failed batch commit."""
        tenant_id = self.ctx.tenant_id if self.ctx else "unknown"
        pipeline_id = self.ctx.pipeline_id if self.ctx else "unknown"
        self.telemetry.record_batch_failed("kafka", tenant_id, pipeline_id)

    def _record_retry(self) -> None:
        """Record retry attempt."""
        tenant_id = self.ctx.tenant_id if self.ctx else "unknown"
        pipeline_id = self.ctx.pipeline_id if self.ctx else "unknown"
        self.telemetry.record_retry("kafka", tenant_id, pipeline_id)

    def _record_commit_duration(self, duration: float) -> None:
        """Record commit duration."""
        tenant_id = self.ctx.tenant_id if self.ctx else "unknown"
        pipeline_id = self.ctx.pipeline_id if self.ctx else "unknown"
        self.telemetry.record_commit_duration("kafka", tenant_id, pipeline_id, duration)

    def _record_dropped_batch(self, reason: str) -> None:
        """Record a dropped batch."""
        tenant_id = self.ctx.tenant_id if self.ctx else "unknown"
        pipeline_id = self.ctx.pipeline_id if self.ctx else "unknown"
        self.telemetry.record_dropped_batch("kafka", tenant_id, pipeline_id, reason)

    def get_metrics(self) -> dict:
        """Get sink metrics."""
        return {
            "queue_depth": self._queue.qsize() if self._queue else 0,
            "retry_count": self._retry_count,
            "last_commit_at": self._last_commit_at,
            "last_error_at": self._last_error_at,
        }
