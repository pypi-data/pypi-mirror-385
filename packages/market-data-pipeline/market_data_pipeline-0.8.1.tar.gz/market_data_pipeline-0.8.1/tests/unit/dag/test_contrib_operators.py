import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from market_data_pipeline.orchestration.dag import Bar, Channel
from market_data_pipeline.orchestration.dag.contrib.operators_contrib import (
    deduplicate,
    resample_ohlc,
    router,
    throttle,
)

UTC = timezone.utc


@pytest.mark.asyncio
async def test_resample_ohlc_produces_bars():
    base = datetime(2024, 1, 1, 9, 30, tzinfo=UTC)
    ticks = [
        {"sym": "AAPL", "t": base + timedelta(seconds=i), "px": 100 + i} for i in range(5)
    ]

    async def src():
        for t in ticks:
            yield t

    bars = []
    async for bar in resample_ohlc(
        src().__aiter__(),
        get_symbol=lambda x: x["sym"],
        get_price=lambda x: x["px"],
        get_time=lambda x: x["t"],
        window=timedelta(seconds=5),
    ):
        bars.append(bar)

    assert len(bars) == 1
    b = bars[0]
    assert isinstance(b, Bar)
    assert b.open == 100
    assert b.close == 104
    assert b.high == 104
    assert b.low == 100
    assert b.count == 5


@pytest.mark.asyncio
async def test_deduplicate_filters_duplicates():
    async def src():
        items = [
            {"k": "A", "v": 1},
            {"k": "A", "v": 1},  # duplicate
            {"k": "A", "v": 2},  # new value
        ]
        for it in items:
            await asyncio.sleep(0)
            yield it

    seen = []
    async for it in deduplicate(src().__aiter__(), key_fn=lambda x: (x["k"], x["v"]), ttl=1.0):
        seen.append(it)

    assert len(seen) == 2


@pytest.mark.asyncio
async def test_throttle_approx_rate():
    async def src():
        for i in range(5):
            yield i

    t0 = asyncio.get_event_loop().time()
    async for _ in throttle(src().__aiter__(), rate_limit=5):
        pass
    t1 = asyncio.get_event_loop().time()

    # at least ~1s total duration for 5 messages at 5/sec
    assert (t1 - t0) >= 0.9


@pytest.mark.asyncio
async def test_router_fanout():
    async def src():
        for i in range(4):
            yield {"sym": "AAPL" if i % 2 == 0 else "MSFT", "v": i}

    aapl_ch, msft_ch = Channel(), Channel()
    routes = {"AAPL": aapl_ch, "MSFT": msft_ch}

    router_task = asyncio.create_task(router(src().__aiter__(), routes, route_key=lambda x: x["sym"]))
    results = {"AAPL": [], "MSFT": []}

    async def consume(sym, ch):
        try:
            while True:
                item = await ch.get()
                results[sym].append(item)
        except Exception:
            pass

    consumers = [
        asyncio.create_task(consume("AAPL", aapl_ch)),
        asyncio.create_task(consume("MSFT", msft_ch))
    ]
    
    # Wait for router to complete
    await router_task
    
    # Give consumers a moment to finish
    await asyncio.sleep(0.1)
    
    # Cancel consumers
    for c in consumers:
        c.cancel()
    
    await asyncio.gather(*consumers, return_exceptions=True)

    assert len(results["AAPL"]) == 2
    assert len(results["MSFT"]) == 2

