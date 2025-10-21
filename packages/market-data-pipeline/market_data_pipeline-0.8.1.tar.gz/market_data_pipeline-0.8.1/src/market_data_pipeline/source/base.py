"""Base source protocol and status definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterator, List, Optional, Protocol, runtime_checkable

from ..types import Quote
from .capabilities import SourceCapabilities, SourceHealth, SourceSLA


@dataclass(frozen=True)
class SourceStatus:
    """Source connection status."""

    connected: bool
    detail: str = ""


@runtime_checkable
class TickSource(Protocol):
    """Protocol for market data sources.

    SLA Contract:
    - Single responsibility: one source instance = one upstream connection
    - Ordering: items yielded are non-decreasing by event time (best effort for live, strict for replay)
    - Cancellation: must stop quickly (no long sleeps blocking close())
    - Backpressure: never blocks indefinitely or buffers unboundedly
    - Telemetry: exports standard counters for observability
    """

    # Core protocol methods
    async def stream(self) -> AsyncIterator[Quote]:
        """Stream market data quotes.

        Yields quotes in non-decreasing event time order.
        Must respect backpressure and pacing limits.
        Must exit quickly on cancellation.
        """
        ...

    async def status(self) -> SourceStatus:
        """Get current source status."""
        ...

    async def close(self) -> None:
        """Close the source connection.

        Must complete within SLA max_close_time_ms.
        Must not block indefinitely.
        """
        ...

    # Optional extensions
    @property
    def symbols(self) -> List[str]:
        """Get immutable list of symbols this source handles."""
        ...

    @property
    def capabilities(self) -> SourceCapabilities:
        """Get source capabilities (trades, quotes, book, etc.)."""
        ...

    async def start(self) -> None:
        """Explicit connect/handshake for sources that need pre-warming."""
        ...

    async def health(self) -> SourceHealth:
        """Get machine-parsable health information."""
        ...
