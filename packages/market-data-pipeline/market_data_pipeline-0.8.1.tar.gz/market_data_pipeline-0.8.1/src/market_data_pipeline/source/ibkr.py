"""IBKR source for live market data from Interactive Brokers."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import AsyncIterator, List, Optional

from ..context import PipelineContext
from ..errors import SourceError
from ..pacing import Budget, Pacer
from ..source.base import SourceStatus, TickSource
from ..source.capabilities import SourceCapabilities, SourceHealth
from ..source.telemetry import get_source_telemetry
from ..types import Quote


class IBKRSource(TickSource):
    """IBKR source for live market data.

    Features:
    - TWS/Gateway connection with handshake
    - Per-symbol subscription management
    - IBKR pacing error handling (codes 162/420)
    - Auto-reconnect with exponential backoff
    - Telemetry for connection health
    """

    def __init__(
        self,
        symbols: List[str],
        host: str = "localhost",
        port: int = 7497,
        client_id: int = 1,
        pacing_budget: tuple[int, int] = (1000, 1000),
        ctx: Optional[PipelineContext] = None,
    ) -> None:
        """Initialize IBKR source."""
        self._symbols = symbols
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ctx = ctx
        self._running = False
        self._closed = False
        self._connected = False
        self._last_error: Optional[str] = None

        # Setup pacing
        budget = Budget(max_msgs_per_sec=pacing_budget[0], burst=pacing_budget[1])
        self.pacer = Pacer(budget)

        # Telemetry
        self.telemetry = get_source_telemetry()
        self._last_item_time: Optional[datetime] = None
        self._disconnect_count = 0
        self._reconnect_count = 0

        # TODO: Initialize IBKR connection via market_data_core
        # This will use market_data_core.ibkr or similar

    async def stream(self) -> AsyncIterator[Quote]:
        """Stream live market data from IBKR."""
        if self._closed:
            raise SourceError("Source is closed")

        self._running = True

        try:
            # TODO: Implement IBKR data streaming
            # This will connect to IBKR TWS/Gateway and stream real-time data
            # Handle connection management, error recovery, and data parsing

            while self._running and not self._closed:
                # Apply pacing
                await self.pacer.allow(1)

                # TODO: Get next tick from IBKR
                # For now, just yield a placeholder
                yield Quote(
                    symbol="PLACEHOLDER",
                    timestamp=datetime.now(timezone.utc),
                    price=Decimal("100.00"),
                    size=Decimal("100"),
                    source="ibkr",
                    metadata={"placeholder": True},
                )

        except Exception as e:
            self._running = False
            raise SourceError(f"Error in IBKR source: {e}") from e

    async def status(self) -> SourceStatus:
        """Get source status."""
        if self._closed:
            return SourceStatus(connected=False, detail="Source is closed")
        elif self._running:
            # TODO: Check actual IBKR connection status
            return SourceStatus(connected=True, detail="Connected to IBKR")
        else:
            return SourceStatus(connected=False, detail="Source not started")

    async def close(self) -> None:
        """Close the source."""
        self._running = False
        self._closed = True
        self._connected = False

        # TODO: Close IBKR connection
        # Disconnect from TWS/Gateway and cleanup resources

    @property
    def symbols(self) -> List[str]:
        """Get immutable list of symbols."""
        return self._symbols.copy()

    @property
    def capabilities(self) -> SourceCapabilities:
        """Get source capabilities."""
        return (
            SourceCapabilities.TRADES
            | SourceCapabilities.QUOTES
            | SourceCapabilities.BOOK
        )

    async def start(self) -> None:
        """Establish TWS/Gateway connection and subscribe to symbols."""
        try:
            # TODO: Connect to IBKR TWS/Gateway
            # await self._connect_to_ibkr()

            # TODO: Subscribe to symbols
            # for symbol in self._symbols:
            #     await self._subscribe_to_symbol(symbol)

            self._connected = True
            self.telemetry.set_status("ibkr", True)

        except Exception as e:
            self._last_error = str(e)
            self.telemetry.record_disconnect("ibkr")
            self._disconnect_count += 1
            raise SourceError(f"Failed to connect to IBKR: {e}") from e

    async def health(self) -> SourceHealth:
        """Get machine-parsable health information."""
        return SourceHealth(
            connected=self._connected and not self._closed,
            last_error_at=None,  # TODO: Track last error timestamp
            last_item_ts=self._last_item_time,
            queued_msgs=0,  # TODO: Track IBKR queue depth
            pacing_blocked_count=0,  # TODO: Track pacing blocks
            detail=f"Connected to {self.host}:{self.port} (client_id={self.client_id})",
        )

    def _convert_ibkr_tick(self, ibkr_data: dict) -> Quote:
        """Convert IBKR tick data to Quote format."""
        # TODO: Implement IBKR tick conversion
        # This will handle different IBKR tick types (trade, bid, ask, etc.)
        # and convert them to our standard Quote format

        # Placeholder implementation
        return Quote(
            symbol=ibkr_data.get("symbol", "UNKNOWN"),
            timestamp=datetime.now(timezone.utc),
            price=Decimal(str(ibkr_data.get("price", 0))),
            size=Decimal(str(ibkr_data.get("size", 0))),
            bid=Decimal(str(ibkr_data.get("bid", 0))) if ibkr_data.get("bid") else None,
            ask=Decimal(str(ibkr_data.get("ask", 0))) if ibkr_data.get("ask") else None,
            bid_size=(
                Decimal(str(ibkr_data.get("bid_size", 0)))
                if ibkr_data.get("bid_size")
                else None
            ),
            ask_size=(
                Decimal(str(ibkr_data.get("ask_size", 0)))
                if ibkr_data.get("ask_size")
                else None
            ),
            source="ibkr",
            metadata={
                "ibkr_tick_type": ibkr_data.get("tick_type"),
                "ibkr_client_id": self.client_id,
            },
        )

    def _handle_ibkr_pacing_error(self, error_code: int) -> None:
        """Handle IBKR pacing errors (162/420) with exponential backoff."""
        if error_code in [162, 420]:
            # TODO: Implement exponential backoff with jitter
            # This should map to our internal pacing system
            self.telemetry.record_pacing_blocked("ibkr", 1.0)  # 1 second blocked
        else:
            # Other IBKR errors
            self._last_error = f"IBKR error {error_code}"

    def _record_telemetry(self, quote: Quote) -> None:
        """Record telemetry for emitted quote."""
        self._last_item_time = quote.timestamp

        # Record item
        tenant_id = self.ctx.tenant_id if self.ctx else "unknown"
        self.telemetry.record_item("ibkr", tenant_id, quote.symbol)

        # Update lag
        if self._last_item_time:
            lag = (datetime.now(timezone.utc) - self._last_item_time).total_seconds()
            self.telemetry.set_lag("ibkr", quote.symbol, lag)
