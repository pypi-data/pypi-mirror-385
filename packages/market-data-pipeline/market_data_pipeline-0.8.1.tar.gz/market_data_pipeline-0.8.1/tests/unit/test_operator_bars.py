# tests/unit/test_operator_bars.py
import pytest
from decimal import Decimal
from datetime import datetime, timezone
from market_data_pipeline.operator.bars import SecondBarAggregator
from market_data_pipeline.types import Bar
from tests.utils.factories import make_tick, utc


@pytest.mark.asyncio
async def test_bars_aggregator_basic_ohlcv():
    op = SecondBarAggregator(window_sec=1, allowed_lateness_sec=0)

    # Three ticks in same second
    t0 = 1_700_000_000
    out = []
    out.append(await op.handle(make_tick("NVDA", 100, 2, t0 + 0.01)))
    out.append(await op.handle(make_tick("NVDA", 105, 1, t0 + 0.40)))
    out.append(await op.handle(make_tick("NVDA", 102, 3, t0 + 0.90)))
    # Move to next second → should flush the previous
    flushed = await op.handle(make_tick("NVDA", 103, 1, t0 + 1.01))

    # Only the flush emits a bar (others return None)
    assert all(x is None for x in out)
    assert isinstance(flushed, Bar)
    assert flushed.timestamp == datetime.fromtimestamp(t0, tz=timezone.utc)
    assert flushed.open == Decimal("100")
    assert flushed.high == Decimal("105")
    assert flushed.low == Decimal("100")
    assert flushed.close == Decimal("102")
    assert flushed.volume == Decimal("6")  # 2+1+3
    assert flushed.vwap == (
        Decimal("100") * 2 + Decimal("105") * 1 + Decimal("102") * 3
    ) / Decimal("6")
    assert flushed.trade_count == 3


@pytest.mark.asyncio
async def test_bars_aggregator_flush_all_drains():
    op = SecondBarAggregator(window_sec=1)
    t0 = 1_700_000_010
    await op.handle(make_tick("SPY", 500, 1, t0 + 0.2))
    await op.handle(make_tick("SPY", 501, 1, t0 + 0.7))
    # Same second; nothing emitted yet
    bars = await op.flush_all()
    assert len(bars) == 1
    assert bars[0].symbol == "SPY"
    assert bars[0].timestamp == utc(t0)
