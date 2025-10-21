# tests/unit/test_batcher_hybrid.py
import asyncio
import pytest
from decimal import Decimal
from datetime import datetime, timezone
from market_data_pipeline.batcher.hybrid import HybridBatcher
from market_data_pipeline.types import Bar


def mkbar(sym: str, i: int) -> Bar:
    return Bar(
        symbol=sym,
        timestamp=datetime.now(timezone.utc),
        open=Decimal(i),
        high=Decimal(i),
        low=Decimal(i),
        close=Decimal(i),
        volume=Decimal(1),
        vwap=None,
        trade_count=1,
        source="test",
        metadata={},
    )


@pytest.mark.asyncio
async def test_hybrid_batcher_flush_by_size():
    b = HybridBatcher(max_rows=3, max_bytes=10_000, flush_ms=10_000)
    out = await b.add(mkbar("NVDA", 1))
    assert out is None
    out = await b.add(mkbar("NVDA", 2))
    assert out is None
    out = await b.add(mkbar("NVDA", 3))
    assert out is not None
    assert len(out) == 3


@pytest.mark.asyncio
async def test_hybrid_batcher_flush_by_time():
    b = HybridBatcher(max_rows=1000, max_bytes=10_000, flush_ms=50)
    out = await b.add(mkbar("SPY", 1))
    assert out is None
    await asyncio.sleep(0.08)
    tail = await b.flush()
    assert tail is not None and len(tail) == 1
