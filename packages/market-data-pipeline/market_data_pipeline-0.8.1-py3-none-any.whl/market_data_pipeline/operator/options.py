"""Options-specific operators: per-contract snapshots, greeks-ready."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, Optional, Protocol, Tuple

from .base import EventTimePolicy, StatefulOperator
from ..types import Bar, Quote

# OCC-like symbol parser e.g., "AAPL250117C00200000"
_OCC_RE = re.compile(
    r"^(?P<under>[A-Z]{1,6})(?P<y>\d{2})(?P<m>\d{2})(?P<d>\d{2})(?P<right>[CP])(?P<strike>\d{8})$"
)


def _parse_occ(symbol: str) -> Optional[dict[str, Any]]:
    m = _OCC_RE.match(symbol)
    if not m:
        return None
    y = 2000 + int(m.group("y"))
    m_ = int(m.group("m"))
    d_ = int(m.group("d"))
    strike = Decimal(m.group("strike")) / Decimal("1000")
    return {
        "under": m.group("under"),
        "expiry": datetime(y, m_, d_, tzinfo=timezone.utc),
        "right": "call" if m.group("right") == "C" else "put",
        "strike": strike,
    }


class GreeksPricer(Protocol):
    """Plug-in interface for greeks; implement with BS or provider values."""

    def compute(
        self,
        *,
        S: Decimal,
        K: Decimal,
        T_years: float,
        r: float,
        q: float,
        sigma: Optional[Decimal],
        right: str,
        mid: Optional[Decimal],
    ) -> dict[str, Decimal]: ...


@dataclass
class _CSnap:
    # per-contract snapshot window
    start: datetime
    last: Optional[Quote] = None
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    mid: Optional[Decimal] = None
    trades: int = 0
    volume: Decimal = Decimal("0")


class OptionsChainOperator(StatefulOperator):
    """Per-contract 1s snapshots for options with greeks hook (Phase-1).

    Emits a per-contract Bar-like record each window_sec with last/mid/volume.
    Later phases can aggregate across strikes/expiries for DEX/GEX curves.
    """

    def __init__(
        self,
        window_sec: int = 1,
        *,
        allowed_lateness_sec: int = 0,
        pricer: Optional[GreeksPricer] = None,
        underlying_last_provider: Optional[callable[[str], Optional[Decimal]]] = None,
        risk_free_rate: float = 0.0,
        dividend_yield: float = 0.0,
        implied_vol_provider: Optional[callable[[str], Optional[Decimal]]] = None,
    ) -> None:
        policy = EventTimePolicy(
            window_sec=window_sec, allowed_lateness_sec=allowed_lateness_sec
        )
        super().__init__(policy=policy)
        self._snaps: Dict[str, Dict[datetime, _CSnap]] = defaultdict(
            dict
        )  # contract -> {win_start: snap}
        self._last_event_ts: Dict[str, datetime] = {}
        self._pricer = pricer
        self._under = underlying_last_provider
        self._r = risk_free_rate
        self._q = dividend_yield
        self._sigma = implied_vol_provider

    def _emit(self, symbol: str, snap: _CSnap) -> None:
        # Build a Bar-like payload in your schema (using metadata for options fields)
        last_p = snap.last.price if snap.last else None
        vwap = None  # optional for options; could compute with sizes if desired
        meta = {
            "window_sec": self.policy.window_sec,
            "aggregated": True,
            "kind": "option",
        }
        occ = _parse_occ(symbol)
        if occ:
            meta.update(occ)

        # Optional greeks
        if self._pricer and occ:
            S = self._under(occ["under"]) if self._under else None
            sigma = self._sigma(symbol) if self._sigma else None
            if S is not None and occ["strike"] is not None:
                T = max((occ["expiry"] - (snap.start)).days / 365.25, 0.0)
                try:
                    g = self._pricer.compute(
                        S=S,
                        K=occ["strike"],
                        T_years=T,
                        r=self._r,
                        q=self._q,
                        sigma=sigma,
                        right=occ["right"],
                        mid=snap.mid,
                    )
                    meta["greeks"] = {k: str(v) for k, v in g.items()}
                except Exception:
                    pass  # don't fail the pipeline on greeks calc

        self._ready.append(
            Bar(
                symbol=symbol,
                timestamp=snap.start,
                open=last_p,
                high=last_p,
                low=last_p,
                close=last_p,  # snapshots, not OHLC
                volume=snap.volume,
                vwap=vwap,
                trade_count=snap.trades,
                source=(snap.last.source if snap.last else "unknown"),
                metadata=meta,
            )
        )

    def _floor(self, ts: datetime) -> datetime:
        return self._floor_utc(ts, self.policy.window_sec)

    def _on_tick(self, tick: Quote) -> None:
        sym = tick.symbol
        self._symbols_seen += 1 if sym not in self._snaps else 0

        # Event-time tracking
        if (lt := self._last_event_ts.get(sym)) is None or tick.timestamp > lt:
            self._last_event_ts[sym] = tick.timestamp

        win0 = self._floor(tick.timestamp)

        # Late handling: same pattern as bars (drop late beyond watermark)
        wm = self._last_event_ts.get(sym)
        if wm and self.policy.allowed_lateness_sec > 0:
            wm_deadline = wm.replace(tzinfo=timezone.utc) - timedelta(
                seconds=self.policy.allowed_lateness_sec
            )
            if self._floor(wm_deadline) > win0:
                if self.policy.drop_late_beyond_watermark:
                    self._inc(
                        "operator_options_late_dropped_total",
                        operator=self.__class__.__name__,
                    )
                    return

        # Get/create this window snapshot
        snaps = self._snaps[sym]
        cs = snaps.get(win0)
        if not cs:
            # bound to 2 windows (current + previous)
            if len(snaps) >= 2:
                oldest = min(snaps.keys())
                self._emit(sym, snaps[oldest])
                del snaps[oldest]
            cs = snaps[win0] = _CSnap(start=win0)

        # Update snapshot
        cs.last = tick
        p, sz = tick.price, tick.size
        # If Quote carries bid/ask via metadata, prefer them; else treat as last.
        bid = getattr(tick, "bid", None) or (tick.metadata or {}).get("bid")
        ask = getattr(tick, "ask", None) or (tick.metadata or {}).get("ask")
        if bid is not None:
            cs.bid = Decimal(str(bid))
        if ask is not None:
            cs.ask = Decimal(str(ask))
        if cs.bid is not None and cs.ask is not None:
            cs.mid = (cs.bid + cs.ask) / Decimal("2")
        cs.trades += 1
        cs.volume += sz

        # Watermark flush
        if wm and self.policy.allowed_lateness_sec > 0:
            wm_deadline = wm.replace(tzinfo=timezone.utc) - timedelta(
                seconds=self.policy.allowed_lateness_sec
            )
            ready = [
                k
                for k in snaps.keys()
                if (k + timedelta(seconds=self.policy.window_sec)) <= wm_deadline
            ]
            for k in sorted(ready):
                self._emit(sym, snaps[k])
                del snaps[k]

    async def flush_symbol(self, symbol: str) -> Optional[Bar]:
        snaps = self._snaps.get(symbol)
        if not snaps:
            return None
        k = min(snaps.keys())
        self._emit(symbol, snaps[k])
        del snaps[k]
        return self._ready.popleft() if self._ready else None

    async def flush_all(self) -> list[Bar]:
        for sym, snaps in list(self._snaps.items()):
            for k in sorted(list(snaps.keys())):
                self._emit(sym, snaps[k])
                del snaps[k]
            if not snaps:
                del self._snaps[sym]
        return await super().flush_all()

    def status(self) -> dict[str, Any]:
        base = super().status()
        base.update(
            {
                "contracts": len(self._snaps),
                "active_windows_total": sum(len(m) for m in self._snaps.values()),
            }
        )
        return base
