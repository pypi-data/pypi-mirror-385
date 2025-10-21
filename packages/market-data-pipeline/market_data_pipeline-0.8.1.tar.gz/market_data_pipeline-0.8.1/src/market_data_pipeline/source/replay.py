"""Replay source for historical data from Parquet/CSV files."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import AsyncIterator, List, Optional

import pandas as pd

from ..context import PipelineContext
from ..errors import SourceError
from ..pacing import Budget, Pacer
from ..source.base import SourceStatus, TickSource
from ..source.capabilities import SourceCapabilities, SourceHealth
from ..source.telemetry import get_source_telemetry
from ..types import Quote


class ReplaySource(TickSource):
    """Replay source for historical market data.

    Features:
    - Event time gating (not pacing) for deterministic replays
    - Cross-symbol timing preserved in merged stream
    - Progress tracking for resumable replays
    - Telemetry for observability
    """

    def __init__(
        self,
        file_path: str,
        symbols: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        replay_speed: float = 1.0,  # 1.0 = real-time, 2.0 = 2x speed, etc.
        pacing_budget: tuple[int, int] = (1000, 1000),
        ctx: Optional[PipelineContext] = None,
    ) -> None:
        """Initialize replay source."""
        self.file_path = Path(file_path)
        self.symbols = symbols
        self.start_time = start_time
        self.end_time = end_time
        self.replay_speed = replay_speed
        self.ctx = ctx
        self._running = False
        self._closed = False

        # Setup pacing - only used for "as fast as possible" mode
        budget = Budget(max_msgs_per_sec=pacing_budget[0], burst=pacing_budget[1])
        self.pacer = Pacer(budget)

        # Load and prepare data
        self._data: Optional[pd.DataFrame] = None
        self._current_index = 0
        self._start_timestamp: Optional[datetime] = None

        # Telemetry
        self.telemetry = get_source_telemetry()
        self._last_item_time: Optional[datetime] = None

    async def stream(self) -> AsyncIterator[Quote]:
        """Stream replayed market data with event time gating."""
        if self._closed:
            raise SourceError("Source is closed")

        if self._data is None:
            await self._load_data()

        self._running = True
        self._start_timestamp = datetime.now(timezone.utc)

        try:
            for _, row in self._data.iterrows():
                if not self._running or self._closed:
                    break

                loop_start = time.time()

                # Event time gating (not pacing) for deterministic replays
                if self.replay_speed > 0:
                    await self._apply_event_time_delay(row)
                else:
                    # "As fast as possible" mode - use pacer
                    await self.pacer.allow(1)

                # Create quote from row
                quote = self._row_to_quote(row)

                # Record telemetry
                self._record_telemetry(quote)

                yield quote

                # Record loop duration
                loop_duration = time.time() - loop_start
                self.telemetry.record_loop_duration("replay", loop_duration)

                self._current_index += 1

        except asyncio.CancelledError:
            # Handle cancellation gracefully
            self._running = False
            raise
        except Exception as e:
            self._running = False
            raise SourceError(f"Error in replay source: {e}") from e

    async def status(self) -> SourceStatus:
        """Get source status."""
        if self._closed:
            return SourceStatus(connected=False, detail="Source is closed")
        elif self._running:
            progress = (
                (self._current_index / len(self._data)) * 100
                if self._data is not None
                else 0
            )
            return SourceStatus(
                connected=True, detail=f"Replaying data ({progress:.1f}% complete)"
            )
        else:
            return SourceStatus(connected=False, detail="Source not started")

    async def close(self) -> None:
        """Close the source."""
        self._running = False
        self._closed = True

    @property
    def symbols(self) -> List[str]:
        """Get symbols from loaded data."""
        if self._data is None:
            return []
        return self._data["symbol"].unique().tolist()

    @property
    def capabilities(self) -> SourceCapabilities:
        """Get source capabilities."""
        return SourceCapabilities.TRADES | SourceCapabilities.QUOTES

    async def start(self) -> None:
        """Load data on start."""
        if self._data is None:
            await self._load_data()

    async def health(self) -> SourceHealth:
        """Get machine-parsable health information."""
        progress = 0.0
        if self._data is not None and len(self._data) > 0:
            progress = (self._current_index / len(self._data)) * 100

        return SourceHealth(
            connected=self._running and not self._closed,
            last_item_ts=self._last_item_time,
            queued_msgs=0,  # Replay source has no queue
            pacing_blocked_count=0,
            detail=f"Replaying {progress:.1f}% complete",
        )

    async def _apply_event_time_delay(self, row: pd.Series) -> None:
        """Apply event time delay for deterministic replay."""
        if self._current_index == 0:
            return  # No delay for first item

        # Get current and previous timestamps
        current_ts = pd.to_datetime(row["timestamp"])
        prev_row = self._data.iloc[self._current_index - 1]
        prev_ts = pd.to_datetime(prev_row["timestamp"])

        # Calculate time difference
        time_diff = (current_ts - prev_ts).total_seconds()

        # Apply replay speed
        if time_diff > 0:
            replay_delay = time_diff / self.replay_speed
            await asyncio.sleep(replay_delay)

    def _record_telemetry(self, quote: Quote) -> None:
        """Record telemetry for emitted quote."""
        self._last_item_time = quote.timestamp

        # Record item
        tenant_id = self.ctx.tenant_id if self.ctx else "unknown"
        self.telemetry.record_item("replay", tenant_id, quote.symbol)

        # Update lag
        if self._last_item_time:
            lag = (datetime.now(timezone.utc) - self._last_item_time).total_seconds()
            self.telemetry.set_lag("replay", quote.symbol, lag)

    async def _load_data(self) -> None:
        """Load data from file."""
        if not self.file_path.exists():
            raise SourceError(f"File not found: {self.file_path}")

        # Load data based on file extension
        if self.file_path.suffix.lower() == ".parquet":
            self._data = pd.read_parquet(self.file_path)
        elif self.file_path.suffix.lower() in [".csv", ".tsv"]:
            self._data = pd.read_csv(self.file_path)
        else:
            raise SourceError(f"Unsupported file format: {self.file_path.suffix}")

        # Filter by symbols if specified
        if self.symbols:
            self._data = self._data[self._data["symbol"].isin(self.symbols)]

        # Filter by time range if specified
        if "timestamp" in self._data.columns:
            self._data["timestamp"] = pd.to_datetime(self._data["timestamp"])

            if self.start_time:
                self._data = self._data[self._data["timestamp"] >= self.start_time]
            if self.end_time:
                self._data = self._data[self._data["timestamp"] <= self.end_time]

        # Sort by timestamp
        self._data = self._data.sort_values("timestamp").reset_index(drop=True)

        if self._data.empty:
            raise SourceError("No data found after filtering")

    def _row_to_quote(self, row: pd.Series) -> Quote:
        """Convert a DataFrame row to a Quote."""
        return Quote(
            symbol=str(row["symbol"]),
            timestamp=pd.to_datetime(row["timestamp"]).to_pydatetime(),
            price=Decimal(str(row["price"])),
            size=Decimal(str(row.get("size", 0))),
            bid=(
                Decimal(str(row["bid"]))
                if "bid" in row and pd.notna(row["bid"])
                else None
            ),
            ask=(
                Decimal(str(row["ask"]))
                if "ask" in row and pd.notna(row["ask"])
                else None
            ),
            bid_size=(
                Decimal(str(row["bid_size"]))
                if "bid_size" in row and pd.notna(row["bid_size"])
                else None
            ),
            ask_size=(
                Decimal(str(row["ask_size"]))
                if "ask_size" in row and pd.notna(row["ask_size"])
                else None
            ),
            source="replay",
            metadata={
                "replay": True,
                "file_path": str(self.file_path),
                "replay_speed": self.replay_speed,
            },
        )
