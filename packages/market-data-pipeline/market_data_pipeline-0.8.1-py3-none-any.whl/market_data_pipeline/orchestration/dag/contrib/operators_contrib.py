from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import (
    Any,
    TypeVar,
)

from ..channel import Channel, ChannelClosed
from ..windowing import (
    TumblingWindowSpec,
    WatermarkPolicy,
    tumbling_window_event_time,
)

T = TypeVar("T")


# ---------------------------------------------------------------------------
# OHLC Resample Operator
# ---------------------------------------------------------------------------

@dataclass
class Bar:
    symbol: str
    open: float
    high: float
    low: float
    close: float
    start: datetime
    end: datetime
    count: int


async def resample_ohlc(
    src: AsyncIterator[dict],
    *,
    get_symbol: Callable[[dict], str],
    get_price: Callable[[dict], float],
    get_time: Callable[[dict], datetime],
    window: timedelta,
    watermark_lag: timedelta = timedelta(seconds=2),
) -> AsyncIterator[Bar]:
    """
    Aggregates tick-like dicts into OHLC bars by symbol using
    tumbling event-time windows.
    """
    spec = TumblingWindowSpec(size=window)
    policy = WatermarkPolicy(lag=watermark_lag)

    async for frame in tumbling_window_event_time(
        src,
        spec,
        get_event_time=get_time,
        get_key=get_symbol,
        watermark_policy=policy,
    ):
        if not frame.items:
            continue
        prices = [get_price(it) for it in frame.items]
        yield Bar(
            symbol=frame.key or "UNK",
            open=prices[0],
            high=max(prices),
            low=min(prices),
            close=prices[-1],
            start=frame.start,
            end=frame.end,
            count=len(prices),
        )


# ---------------------------------------------------------------------------
# Deduplicate Operator
# ---------------------------------------------------------------------------

async def deduplicate(
    src: AsyncIterator[dict],
    *,
    key_fn: Callable[[dict], tuple[str, Any]],
    ttl: float = 5.0,
) -> AsyncIterator[dict]:
    """
    Removes duplicate (key,value) pairs within TTL seconds of each other.
    """
    last_seen: dict[str, tuple[Any, float]] = {}
    async for item in src:
        k, v = key_fn(item)
        now = asyncio.get_event_loop().time()
        prev = last_seen.get(k)
        if prev and prev[0] == v and (now - prev[1]) < ttl:
            continue
        last_seen[k] = (v, now)
        yield item


# ---------------------------------------------------------------------------
# Throttle Operator
# ---------------------------------------------------------------------------

async def throttle(
    src: AsyncIterator[T],
    *,
    rate_limit: int = 100,  # messages per second
) -> AsyncIterator[T]:
    """
    Throttles messages to an approximate rate_limit per second.
    """
    interval = 1.0 / max(1, rate_limit)
    async for item in src:
        await asyncio.sleep(interval)
        yield item


# ---------------------------------------------------------------------------
# Router Operator
# ---------------------------------------------------------------------------

async def router(
    src: AsyncIterator[dict],
    routes: dict[str, Channel],
    *,
    route_key: Callable[[dict], str],
) -> None:
    """
    Routes messages to the appropriate Channel by route_key.
    """
    try:
        async for item in src:
            key = route_key(item)
            if key in routes:
                await routes[key].put(item)
    except ChannelClosed:
        pass
    finally:
        for ch in routes.values():
            await ch.close()

