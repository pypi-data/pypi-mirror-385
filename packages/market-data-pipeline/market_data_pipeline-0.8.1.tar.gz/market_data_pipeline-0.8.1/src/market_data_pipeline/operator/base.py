"""Base operator protocol and reusable stateful operator base."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Deque, Dict, Optional, Protocol

from ..types import Bar, Quote


class Operator(Protocol):
    """Protocol for data transformation operators.

    SLA Contract:
    - Deterministic transform: given a tick, emit either None (no bar ready) or a completed Bar
    - Per-symbol independence: state is tracked per symbol; no unintended cross-talk
    - Idempotent emissions: same tick sequence produces same bar sequence
    - Bounded memory: must not hold unbounded tick history (always windowed or reset)
    - Telemetry: emit counters like ticks_in_total, bars_out_total, operator_latency_seconds
    """

    async def handle(self, tick: Quote) -> Optional[Bar]:
        """Process a tick and return an aggregated bar if ready."""
        ...

    async def flush_symbol(self, symbol: str) -> Optional[Bar]:
        """Force-flush any pending aggregate for the symbol (if applicable)."""
        ...

    async def flush_all(self) -> list[Bar]:
        """Force-flush all pending aggregates (e.g., on shutdown/drain)."""
        ...

    def status(self) -> dict[str, Any]:
        """Lightweight, machine-parsable status for observability."""
        ...


@dataclass(frozen=True)
class EventTimePolicy:
    """Controls how an operator treats time & disorder."""

    window_sec: int = 1  # window length
    allowed_lateness_sec: int = 0  # accept OOO ticks up to this many secs
    drop_late_beyond_watermark: bool = (
        True  # drop beyond watermark (else correct? usually True)
    )


class StatefulOperator(ABC, Operator):
    """Reusable base with ready-queue, bounded symbol maps, and metrics hooks."""

    # ---- Metrics hooks (override or wire to Prometheus in your project) ----
    def _inc(self, name: str, **labels: Any) -> None:  # counters
        pass

    def _observe(self, name: str, value: float, **labels: Any) -> None:  # histograms
        pass

    def _set_gauge(self, name: str, value: float, **labels: Any) -> None:  # gauges
        pass

    # -----------------------------------------------------------------------

    def __init__(self, *, policy: EventTimePolicy, max_symbols: int = 10_000) -> None:
        self.policy = policy
        self.max_symbols = max_symbols
        self._ready: Deque[Bar] = deque()  # output buffer (ensures 1-per-handle)
        self._symbols_seen: int = 0  # cheap cardinality stat
        # subclasses maintain per-symbol state in their own structures

    async def handle(self, tick: Quote) -> Optional[Bar]:
        """Template method: route, update, watermark flush, and emit one ready bar if exists."""
        self._inc("operator_ticks_in_total", operator=self.__class__.__name__)

        # Delegate to subclass to update state & potentially close prior windows.
        self._on_tick(tick)

        # Emit at most one bar per call to keep the simple pipeline contract.
        if self._ready:
            bar = self._ready.popleft()
            self._inc("operator_bars_out_total", operator=self.__class__.__name__)
            return bar
        return None

    @abstractmethod
    def _on_tick(self, tick: Quote) -> None:
        """Subclass implements event-time update + may push completed Bar(s) into self._ready."""
        raise NotImplementedError

    async def flush_symbol(self, symbol: str) -> Optional[Bar]:
        """Subclass may override to flush a specific symbol window."""
        return None

    async def flush_all(self) -> list[Bar]:
        """Default: drain any queued completions; subclass can push before returning."""
        out: list[Bar] = []
        while self._ready:
            out.append(self._ready.popleft())
        if out:
            self._inc("operator_bars_out_total", operator=self.__class__.__name__)
        return out

    # Utilities
    @staticmethod
    def _floor_utc(ts: datetime, window_sec: int) -> datetime:
        epoch = int(ts.timestamp())
        return datetime.fromtimestamp(
            (epoch // window_sec) * window_sec, tz=timezone.utc
        )

    def status(self) -> dict[str, Any]:
        return {
            "operator": self.__class__.__name__,
            "window_sec": self.policy.window_sec,
            "allowed_lateness_sec": self.policy.allowed_lateness_sec,
            "ready_queue": len(self._ready),
            "symbols_seen": self._symbols_seen,
        }
