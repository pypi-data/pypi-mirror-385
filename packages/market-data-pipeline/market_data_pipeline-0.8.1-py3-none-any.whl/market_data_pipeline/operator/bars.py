"""Bar aggregation operators (event-time, watermark, bounded state)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, Optional

from .base import EventTimePolicy, StatefulOperator
from ..types import Bar, Quote


@dataclass
class _Win:
    start: datetime
    open: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    close: Optional[Decimal] = None
    v_sum: Decimal = Decimal("0")
    pv_sum: Decimal = Decimal("0")
    trades: int = 0
    last_tick: Optional[Quote] = None


class SecondBarAggregator(StatefulOperator):
    """Aggregates ticks into aligned OHLCV bars with event-time correctness.

    Features:
      - Aligns windows to epoch boundaries (0..n)*window_sec
      - Accepts late ticks up to `allowed_lateness_sec`
      - Drops beyond-watermark late ticks (configurable)
      - Bounded state per symbol: at most 2 active windows (current + maybe previous)
      - Flush-on-watermark: completes windows once past lateness horizon
      - VWAP = pv_sum / v_sum when v_sum > 0
    """

    def __init__(self, window_sec: int = 1, *, allowed_lateness_sec: int = 0) -> None:
        policy = EventTimePolicy(
            window_sec=window_sec, allowed_lateness_sec=allowed_lateness_sec
        )
        super().__init__(policy=policy)
        self._wins: Dict[str, Dict[datetime, _Win]] = defaultdict(
            dict
        )  # symbol -> {win_start: _Win}
        self._last_event_ts: Dict[str, datetime] = {}  # watermark basis per symbol

    def _emit(self, b: Bar) -> None:
        self._ready.append(b)

    def _close_window(self, symbol: str, w: _Win) -> None:
        if w.open is None:
            return
        vwap = (w.pv_sum / w.v_sum) if w.v_sum > 0 else None
        self._emit(
            Bar(
                symbol=symbol,
                timestamp=w.start,
                open=w.open,
                high=w.high,
                low=w.low,
                close=w.close,
                volume=w.v_sum,
                vwap=vwap,
                trade_count=w.trades,
                source=(w.last_tick.source if w.last_tick else "unknown"),
                metadata={"window_sec": self.policy.window_sec, "aggregated": True},
            )
        )

    def _apply(self, w: _Win, tick: Quote) -> None:
        p, sz = tick.price, tick.size
        if w.open is None:
            w.open = w.high = w.low = w.close = p
        else:
            if p > w.high:
                w.high = p
            if p < w.low:
                w.low = p
            w.close = p
        w.v_sum += sz
        w.pv_sum += p * sz
        w.trades += 1
        w.last_tick = tick

    def _watermark_deadline(self, symbol: str) -> Optional[datetime]:
        last = self._last_event_ts.get(symbol)
        if not last:
            return None
        return last - timedelta(seconds=self.policy.allowed_lateness_sec)

    def _on_tick(self, tick: Quote) -> None:
        sym = tick.symbol
        self._symbols_seen += 1 if sym not in self._wins else 0

        # Update watermark basis
        if (lt := self._last_event_ts.get(sym)) is None or tick.timestamp > lt:
            self._last_event_ts[sym] = tick.timestamp

        # Determine this tick's window start (event-time aligned)
        win0 = self._floor_utc(tick.timestamp, self.policy.window_sec)

        # Late/OOO handling: if tick falls before watermark, decide to drop or ignore
        wm_deadline = self._watermark_deadline(sym)
        if wm_deadline and win0 < self._floor_utc(wm_deadline, self.policy.window_sec):
            # too-late beyond watermark horizon
            if self.policy.drop_late_beyond_watermark:
                self._inc(
                    "operator_bars_late_dropped_total", operator=self.__class__.__name__
                )
                return
            # else: (not recommended) could re-open/adjust historical window; omitted for simplicity.

        # Get/create current window
        wins = self._wins[sym]
        w = wins.get(win0)
        if not w:
            # Keep at most 2 windows per symbol: current + possibly previous (waiting for lateness)
            if len(wins) >= 2:
                # find the oldest and close it
                oldest_key = min(wins.keys())
                self._close_window(sym, wins[oldest_key])
                del wins[oldest_key]
            w = wins[win0] = _Win(start=win0)

        # Apply tick
        self._apply(w, tick)

        # Watermark flush: any window that ends strictly before watermark is ready
        if wm_deadline:
            ready_keys = [
                k
                for k in wins.keys()
                if (k + timedelta(seconds=self.policy.window_sec)) <= wm_deadline
            ]
            for k in sorted(ready_keys):
                self._close_window(sym, wins[k])
                del wins[k]

    async def flush_symbol(self, symbol: str) -> Optional[Bar]:
        wins = self._wins.get(symbol)
        if not wins:
            return None
        # close the oldest pending window
        k = min(wins.keys())
        self._close_window(symbol, wins[k])
        del wins[k]
        return self._ready.popleft() if self._ready else None

    async def flush_all(self) -> list[Bar]:
        # Close everything deterministically in symbol->window order
        for sym, wins in list(self._wins.items()):
            for k in sorted(list(wins.keys())):
                self._close_window(sym, wins[k])
                del wins[k]
            if not wins:
                del self._wins[sym]
        return await super().flush_all()

    def status(self) -> dict[str, Any]:
        base = super().status()
        base.update(
            {
                "active_symbols": len(self._wins),
                "active_windows_total": sum(len(m) for m in self._wins.values()),
            }
        )
        return base
