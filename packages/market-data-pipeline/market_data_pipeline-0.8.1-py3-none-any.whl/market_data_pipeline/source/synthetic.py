"""Synthetic market data source for testing and simulation."""

from __future__ import annotations

import asyncio
import random
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


class SyntheticSource(TickSource):
    """Synthetic market data source for testing and simulation.

    Features:
    - Round-robin symbol selection for fairness
    - Single pacing mechanism (no double throttling)
    - Aggregate rate across all symbols
    - Small jitter to avoid lockstep interactions
    """

    def __init__(
        self,
        symbols: List[str],
        ticks_per_sec: int = 100,
        pacing_budget: tuple[int, int] = (1000, 1000),
        seed: Optional[int] = None,
        ctx: Optional[PipelineContext] = None,
    ) -> None:
        """Initialize synthetic source."""
        self._symbols = symbols
        self.ticks_per_sec = ticks_per_sec
        self.ctx = ctx
        self._running = False
        self._closed = False
        self._symbol_index = 0  # For round-robin selection

        # Setup pacing - use pacer as primary rate limiter
        budget = Budget(max_msgs_per_sec=pacing_budget[0], burst=pacing_budget[1])
        self.pacer = Pacer(budget)

        # Setup random seed for deterministic behavior
        if seed is not None:
            random.seed(seed)

        # Generate initial prices for each symbol
        self.base_prices = {
            symbol: Decimal(str(random.uniform(50.0, 500.0))) for symbol in symbols
        }

        # Telemetry
        self.telemetry = get_source_telemetry()
        self._last_item_time: Optional[datetime] = None
        self._pacing_blocked_count = 0

    async def stream(self) -> AsyncIterator[Quote]:
        """Stream synthetic market data with round-robin fairness."""
        if self._closed:
            raise SourceError("Source is closed")

        self._running = True

        try:
            while self._running and not self._closed:
                loop_start = time.time()

                # Apply pacing (primary rate limiter)
                await self.pacer.allow(1)

                # Round-robin symbol selection for fairness
                symbol = self._get_next_symbol()
                tick = self._generate_tick(symbol)

                # Record telemetry
                self._record_telemetry(symbol)

                yield tick

                # Add small jitter to avoid lockstep interactions
                jitter = random.uniform(-0.002, 0.002)  # ±2ms jitter
                base_delay = 1.0 / self.ticks_per_sec
                await asyncio.sleep(max(0, base_delay + jitter))

                # Record loop duration
                loop_duration = time.time() - loop_start
                self.telemetry.record_loop_duration("synthetic", loop_duration)

        except asyncio.CancelledError:
            # Handle cancellation gracefully
            self._running = False
            raise
        except Exception as e:
            self._running = False
            raise SourceError(f"Error in synthetic source: {e}") from e

    async def status(self) -> SourceStatus:
        """Get source status."""
        if self._closed:
            return SourceStatus(connected=False, detail="Source is closed")
        elif self._running:
            return SourceStatus(connected=True, detail="Generating synthetic data")
        else:
            return SourceStatus(connected=False, detail="Source not started")

    async def close(self) -> None:
        """Close the source."""
        self._running = False
        self._closed = True

    @property
    def symbols(self) -> List[str]:
        """Get immutable list of symbols."""
        return self._symbols.copy()

    @property
    def capabilities(self) -> SourceCapabilities:
        """Get source capabilities."""
        return SourceCapabilities.TRADES | SourceCapabilities.QUOTES

    async def start(self) -> None:
        """No pre-warming needed for synthetic source."""
        pass

    async def health(self) -> SourceHealth:
        """Get machine-parsable health information."""
        return SourceHealth(
            connected=self._running and not self._closed,
            last_item_ts=self._last_item_time,
            queued_msgs=0,  # Synthetic source has no queue
            pacing_blocked_count=self._pacing_blocked_count,
            detail="Generating synthetic data" if self._running else "Stopped",
        )

    def _get_next_symbol(self) -> str:
        """Get next symbol using round-robin selection."""
        symbol = self._symbols[self._symbol_index]
        self._symbol_index = (self._symbol_index + 1) % len(self._symbols)
        return symbol

    def _record_telemetry(self, symbol: str) -> None:
        """Record telemetry for emitted item."""
        self._last_item_time = datetime.now(timezone.utc)

        # Record item
        tenant_id = self.ctx.tenant_id if self.ctx else "unknown"
        self.telemetry.record_item("synthetic", tenant_id, symbol)

        # Update lag
        if self._last_item_time:
            lag = (datetime.now(timezone.utc) - self._last_item_time).total_seconds()
            self.telemetry.set_lag("synthetic", symbol, lag)

    def _generate_tick(self, symbol: str) -> Quote:
        """Generate a synthetic tick for the given symbol."""
        # Get current base price
        base_price = self.base_prices[symbol]

        # Generate price movement (-2% to +2%)
        price_change = random.uniform(-0.02, 0.02)
        new_price = base_price * Decimal(str(1 + price_change))

        # Update base price for next tick
        self.base_prices[symbol] = new_price

        # Generate bid/ask spread
        spread = new_price * Decimal("0.001")  # 0.1% spread
        bid = new_price - spread / 2
        ask = new_price + spread / 2

        # Generate sizes
        size = Decimal(str(random.uniform(100, 1000)))
        bid_size = Decimal(str(random.uniform(100, 500)))
        ask_size = Decimal(str(random.uniform(100, 500)))

        return Quote(
            symbol=symbol,
            timestamp=datetime.now(timezone.utc),
            price=new_price,
            size=size,
            bid=bid,
            ask=ask,
            bid_size=bid_size,
            ask_size=ask_size,
            source="synthetic",
            metadata={
                "generated": True,
                "base_price": float(base_price),
                "price_change": price_change,
            },
        )
