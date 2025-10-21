"""Base sink protocol."""

from __future__ import annotations

from typing import List, Optional, Protocol

from ..types import Bar
from .capabilities import SinkCapabilities, SinkHealth, SinkSLA


class Sink(Protocol):
    """Protocol for data persistence sinks.

    SLA Contract:
    - Ordering: Single write(batch) persisted in-order; cross-batch ordering is best-effort
    - At-least-once: Retries may happen; downstream must be idempotent
    - Bounded memory: Must expose bounded buffer or explicit backpressure behavior
    - Graceful drain: close() drains in-flight work and shuts down cleanly
    - Observability: Exports standard counters/histograms and get_metrics() snapshot
    """

    # Core protocol methods
    async def write(self, batch: List[Bar]) -> None:
        """Write a batch of bars to the sink.

        Must respect backpressure policy (block/drop_oldest/drop_newest).
        Single batch must be persisted in-order.
        """
        ...

    async def close(self, drain: bool = True) -> None:
        """Close the sink connection.

        If drain=True, waits for in-flight work to complete.
        Must complete within SLA max_drain_time_ms.
        """
        ...

    # Optional extensions
    @property
    def capabilities(self) -> SinkCapabilities:
        """Get sink capabilities (batch writes, transactions, etc.)."""
        ...

    async def start(self) -> None:
        """Initialize worker pools/producers before first write()."""
        ...

    async def flush(self) -> None:
        """Force a commit of queued work without closing."""
        ...

    async def health(self) -> SinkHealth:
        """Get machine-parsable health information."""
        ...

    def get_metrics(self) -> dict:
        """Get sink metrics snapshot."""
        ...
